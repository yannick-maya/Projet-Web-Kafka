"""Application Flask principale avec WebSockets et Base de données"""

import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from kafka_service import KafkaProducerService, KafkaConsumerService, generate_fake_order, generate_fake_payment, generate_fake_delivery
from config.kafka_config import create_topics_if_not_exist
from Database import Database

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation Flask et SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecommerce-secret-key-2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialiser la base de données
db = Database()

# Services Kafka
producer_service = KafkaProducerService()
consumer_service = None


def kafka_message_callback(topic, data):
    """Callback appelé quand un message Kafka arrive"""
    try:
        logger.info(f"📨 Message Kafka reçu - Topic: {topic}")
        logger.debug(f"Data: {data}")
        
        # Sauvegarder dans la base de données ET émettre via WebSocket
        if topic == 'orders':
            db.save_order(data)
            logger.info(f"✅ Commande sauvegardée et émission 'new_order'")
            # socketio.emit('new_order', data, namespace='/', broadcast=True)
            socketio.emit('new_order', data, namespace='/')
            socketio.emit('stats_update', db.get_stats(), namespace='/')
            print("EMIT SOCKET nouvelle donnees", data)

            
        elif topic == 'payments':
            db.save_payment(data)
            logger.info(f"✅ Paiement sauvegardé et émission 'new_payment'")
            socketio.emit('new_payment', data, namespace='/')
            
        elif topic == 'deliveries':
            db.save_delivery(data)
            logger.info(f"✅ Livraison sauvegardée et émission 'new_delivery'")
            socketio.emit('new_delivery', data, namespace='/')
            
    except Exception as e:
        logger.error(f"❌ Erreur dans le callback Kafka: {e}", exc_info=True)


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Redirection vers le dashboard"""
    return render_template('dashboard.html')


@app.route('/dashboard')
def dashboard():
    """Page du tableau de bord"""
    return render_template('dashboard.html')


@app.route('/orders')
def orders():
    """Page de gestion des commandes"""
    return render_template('orders.html')


@app.route('/payments')
def payments():
    """Page de suivi des paiements"""
    return render_template('payments.html')


@app.route('/deliveries')
def deliveries():
    """Page de suivi des livraisons"""
    return render_template('deliveries.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    """Crée une nouvelle commande"""
    try:
        data = request.get_json()
        
        if data:
            order_data = {
                'order_id': data.get('order_id', None),
                'customer_name': data.get('customer_name', ''),
                'customer_email': data.get('customer_email', ''),
                'product': data.get('product', ''),
                'amount': float(data.get('amount', 0)),
                'status': data.get('status', 'Pending'),
                'timestamp': data.get('timestamp', ''),
                'address': data.get('address', '')
            }
        else:
            order_data = generate_fake_order()
        
        # Envoyer à Kafka (qui sera ensuite sauvegardé par le consumer)
        result = producer_service.send_order(order_data)
        
        if result:
            return jsonify({'success': True, 'order': result}), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi à Kafka'}), 500
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la commande: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/orders/list', methods=['GET'])
def list_orders():
    """Liste toutes les commandes"""
    try:
        limit = request.args.get('limit', 50, type=int)
        orders = db.get_all_orders(limit=limit)
        return jsonify({'success': True, 'orders': orders, 'count': len(orders)}), 200
    except Exception as e:
        logger.error(f"❌ Erreur récupération commandes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/payments/create', methods=['POST'])
def create_payment():
    """Crée un nouveau paiement"""
    try:
        data = request.get_json()
        
        if data:
            payment_data = {
                'payment_id': data.get('payment_id', None),
                'order_id': data.get('order_id', ''),
                'amount': float(data.get('amount', 0)),
                'method': data.get('method', ''),
                'status': data.get('status', 'SUCCESS'),
                'timestamp': data.get('timestamp', '')
            }
        else:
            payment_data = generate_fake_payment()
        
        result = producer_service.send_payment(payment_data)
        
        if result:
            return jsonify({'success': True, 'payment': result}), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi à Kafka'}), 500
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du paiement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/payments/list', methods=['GET'])
def list_payments():
    """Liste tous les paiements"""
    try:
        limit = request.args.get('limit', 50, type=int)
        payments = db.get_all_payments(limit=limit)
        return jsonify({'success': True, 'payments': payments, 'count': len(payments)}), 200
    except Exception as e:
        logger.error(f"❌ Erreur récupération paiements: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/deliveries/create', methods=['POST'])
def create_delivery():
    """Crée une nouvelle livraison"""
    try:
        data = request.get_json()
        
        if data:
            delivery_data = {
                'delivery_id': data.get('delivery_id', None),
                'order_id': data.get('order_id', ''),
                'address': data.get('address', ''),
                'status': data.get('status', 'Pending'),
                'estimated_date': data.get('estimated_date', ''),
                'timestamp': data.get('timestamp', '')
            }
        else:
            delivery_data = generate_fake_delivery()
        
        result = producer_service.send_delivery(delivery_data)
        
        if result:
            return jsonify({'success': True, 'delivery': result}), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi à Kafka'}), 500
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la livraison: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/deliveries/list', methods=['GET'])
def list_deliveries():
    """Liste toutes les livraisons"""
    try:
        limit = request.args.get('limit', 50, type=int)
        deliveries = db.get_all_deliveries(limit=limit)
        return jsonify({'success': True, 'deliveries': deliveries, 'count': len(deliveries)}), 200
    except Exception as e:
        logger.error(f"❌ Erreur récupération livraisons: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques depuis la base de données"""
    try:
        stats = db.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"❌ Erreur récupération stats: {e}")
        return jsonify({
            'total_orders': 0,
            'total_payments': 0,
            'success_payments': 0,
            'failed_payments': 0,
            'total_deliveries': 0,
            'total_revenue': 0.0,
            'payment_success_rate': 0.0
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Supprime toutes les données (pour tests)"""
    try:
        db.clear_all_data()
        return jsonify({'success': True, 'message': 'Toutes les données ont été supprimées'}), 200
    except Exception as e:
        logger.error(f"❌ Erreur suppression données: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Événement de connexion"""
    logger.info(f"🔌 Client connecté: {request.sid}")
    emit('connect_response', {'message': 'Connecté au serveur'})
    
    # Démarrer les consumers Kafka au premier client
    global consumer_service
    if consumer_service is None:
        try:
            logger.info("🚀 Démarrage des Consumers Kafka...")
            consumer_service = KafkaConsumerService(callback=kafka_message_callback)
            consumer_service.start_consuming()
            logger.info("✅ Consumers Kafka démarrés avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage des consumers: {e}", exc_info=True)
    else:
        logger.info("ℹ️ Consumers Kafka déjà actifs")
    
    # Envoyer les données existantes au nouveau client
    try:
        orders = db.get_all_orders(limit=10)
        payments = db.get_all_payments(limit=10)
        deliveries = db.get_all_deliveries(limit=10)
        stats = db.get_stats()
        
        emit('initial_data', {
            'orders': orders,
            'payments': payments,
            'deliveries': deliveries,
            'stats': stats
        })
        logger.info("📤 Données initiales envoyées au client")
    except Exception as e:
        logger.error(f"❌ Erreur envoi données initiales: {e}")


@socketio.on('disconnect')
def handle_disconnect():
    """Événement de déconnexion"""
    logger.info(f"❌ Client déconnecté: {request.sid}")


@socketio.on('request_stats')
def handle_stats_request():
    """Envoie les statistiques au client"""
    try:
        stats = db.get_stats()
        emit('stats_update', stats)
    except Exception as e:
        logger.error(f"❌ Erreur envoi stats: {e}")


@socketio.on('load_orders')
def handle_load_orders(data):
    """Charge les commandes"""
    try:
        limit = data.get('limit', 50)
        orders = db.get_all_orders(limit=limit)
        emit('orders_loaded', {'orders': orders})
    except Exception as e:
        logger.error(f"❌ Erreur chargement commandes: {e}")


@socketio.on('load_payments')
def handle_load_payments(data):
    """Charge les paiements"""
    try:
        limit = data.get('limit', 50)
        payments = db.get_all_payments(limit=limit)
        emit('payments_loaded', {'payments': payments})
    except Exception as e:
        logger.error(f"❌ Erreur chargement paiements: {e}")


@socketio.on('load_deliveries')
def handle_load_deliveries(data):
    """Charge les livraisons"""
    try:
        limit = data.get('limit', 50)
        deliveries = db.get_all_deliveries(limit=limit)
        emit('deliveries_loaded', {'deliveries': deliveries})
    except Exception as e:
        logger.error(f"❌ Erreur chargement livraisons: {e}")


if __name__ == '__main__':
    try:
        # Créer les topics Kafka s'ils n'existent pas
        create_topics_if_not_exist()
        
        # Lancer l'application
        logger.info("=" * 80)
        logger.info("🚀 Démarrage de l'application E-Commerce Kafka")
        logger.info("=" * 80)
        logger.info("📊 Dashboard: http://localhost:5000/dashboard")
        logger.info("📦 Commandes: http://localhost:5000/orders")
        logger.info("💳 Paiements: http://localhost:5000/payments")
        logger.info("🚚 Livraisons: http://localhost:5000/deliveries")
        logger.info("=" * 80)
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage de l'application: {e}", exc_info=True)