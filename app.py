"""Application Flask principale avec WebSockets"""

import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from kafka_service import KafkaProducerService, KafkaConsumerService, generate_fake_order, generate_fake_payment, generate_fake_delivery
from config.kafka_config import create_topics_if_not_exist

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation Flask et SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecommerce-secret-key-2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Services Kafka
producer_service = KafkaProducerService()
consumer_service = None

# Statistiques globales
stats = {
    'total_orders': 0,
    'total_payments': 0,
    'success_payments': 0,
    'failed_payments': 0,
    'total_deliveries': 0,
    'total_revenue': 0.0,
    'orders_by_hour': {},
    'payment_success_rate': 0.0
}


def kafka_message_callback(topic, data):
    """Callback appelé quand un message Kafka arrive"""
    try:
        if topic == 'orders':
            stats['total_orders'] += 1
            socketio.emit('new_order', data, namespace='/')
        elif topic == 'payments':
            stats['total_payments'] += 1
            if data['status'] == 'SUCCESS':
                stats['success_payments'] += 1
            else:
                stats['failed_payments'] += 1
            stats['total_revenue'] += data.get('amount', 0)
            socketio.emit('new_payment', data, namespace='/')
        elif topic == 'deliveries':
            stats['total_deliveries'] += 1
            socketio.emit('new_delivery', data, namespace='/')
        
        # Mettre à jour le taux de succès
        if stats['total_payments'] > 0:
            stats['payment_success_rate'] = (stats['success_payments'] / stats['total_payments']) * 100
    except Exception as e:
        logger.error(f"Erreur dans le callback Kafka: {e}")


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
            # Utiliser les données fournis ou générer des données fictives
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
            # Générer une commande fictive
            order_data = generate_fake_order()
        
        # Envoyer à Kafka
        result = producer_service.send_order(order_data)
        
        if result:
            return jsonify({'success': True, 'order': result}), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi à Kafka'}), 500
    except Exception as e:
        logger.error(f"Erreur lors de la création de la commande: {e}")
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
        logger.error(f"Erreur lors de la création du paiement: {e}")
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
        logger.error(f"Erreur lors de la création de la livraison: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques"""
    return jsonify({
        'total_orders': stats['total_orders'],
        'total_payments': stats['total_payments'],
        'success_payments': stats['success_payments'],
        'failed_payments': stats['failed_payments'],
        'total_deliveries': stats['total_deliveries'],
        'total_revenue': round(stats['total_revenue'], 2),
        'payment_success_rate': round(stats['payment_success_rate'], 2)
    })


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Événement de connexion"""
    logger.info(f"Client connecté: {request.sid}")
    emit('connect_response', {'message': 'Connecté au serveur'})
    
    # Démarrer les consumers Kafka au premier client
    global consumer_service
    if consumer_service is None:
        consumer_service = KafkaConsumerService(callback=kafka_message_callback)
        consumer_service.start_consuming()
        logger.info("Consumers Kafka démarrés")


@socketio.on('disconnect')
def handle_disconnect():
    """Événement de déconnexion"""
    logger.info(f"Client déconnecté: {request.sid}")


@socketio.on('request_stats')
def handle_stats_request():
    """Envoie les statistiques au client"""
    emit('stats_update', {
        'total_orders': stats['total_orders'],
        'total_payments': stats['total_payments'],
        'success_payments': stats['success_payments'],
        'failed_payments': stats['failed_payments'],
        'total_deliveries': stats['total_deliveries'],
        'total_revenue': round(stats['total_revenue'], 2),
        'payment_success_rate': round(stats['payment_success_rate'], 2)
    })


if __name__ == '__main__':
    try:
        # Créer les topics Kafka s'ils n'existent pas
        create_topics_if_not_exist()
        
        # Lancer l'application
        logger.info("Démarrage de l'application Flask...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {e}")
