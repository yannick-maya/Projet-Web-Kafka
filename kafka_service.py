"""Service Kafka pour la production et consommation de messages"""

import json
import threading
import logging
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from faker import Faker
from config.kafka_config import TOPICS, PRODUCER_CONFIG, CONSUMER_CONFIG

logger = logging.getLogger(__name__)
fake = Faker('fr_FR')


class KafkaProducerService:
    """Service pour envoyer des messages à Kafka"""
    
    def __init__(self):
        try:
            self.producer = KafkaProducer(**PRODUCER_CONFIG)
            logger.info("KafkaProducerService initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du producer: {e}")
            self.producer = None
    
    def send_order(self, order_data=None):
        """Envoie une commande à Kafka"""
        if order_data is None:
            order_data = generate_fake_order()
        
        try:
       
            self.producer.send('orders', value=order_data)
            self.producer.flush()
            logger.info(f"Commande envoyée: {order_data['order_id']}")
            return order_data
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la commande: {e}")
            return None
    
    def send_payment(self, payment_data=None):
        """Envoie un paiement à Kafka"""
        if payment_data is None:
            payment_data = generate_fake_payment()
        
        try:
            self.producer.send('payments', value=payment_data)
            self.producer.flush()
            logger.info(f"Paiement envoyé: {payment_data['payment_id']}")
            return payment_data
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du paiement: {e}")
            return None
    
    def send_delivery(self, delivery_data=None):
        """Envoie une livraison à Kafka"""
        if delivery_data is None:
            delivery_data = generate_fake_delivery()
        
        try:
            self.producer.send('deliveries', value=delivery_data)
            self.producer.flush()
            logger.info(f"Livraison envoyée: {delivery_data['delivery_id']}")
            return delivery_data
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la livraison: {e}")
            return None


class KafkaConsumerService:
    """Service pour consommer les messages de Kafka en temps réel"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.consumers = {}
        self.running = False
        self.threads = {}
    
    def start_consuming(self):
        """Démarre la consommation des messages pour tous les topics"""
        if self.running:
            logger.warning("Les consumers sont déjà en cours d'exécution")
            return
        
        self.running = True
        
        for topic in TOPICS:
            try:
                # ✅ CORRECTION : auto_offset_reset ne doit être défini QU’UNE FOIS
                consumer = KafkaConsumer(
                    topic,
                    **CONSUMER_CONFIG   # <-- contient auto_offset_reset
                )

                self.consumers[topic] = consumer
                
                # Thread par topic
                thread = threading.Thread(
                    target=self._consume_from_topic,
                    args=(topic, consumer),
                    daemon=True
                )
                thread.start()
                self.threads[topic] = thread

                logger.info(f"✅ Consumer Kafka démarré pour le topic '{topic}'")

            except Exception as e:
                logger.error(f"❌ Erreur lors du démarrage du consumer pour '{topic}': {e}")
    
    def _consume_from_topic(self, topic, consumer):
        """Consomme les messages d'un topic spécifique"""
        try:
            for message in consumer:
                if not self.running:
                    break
                
                try:
                    data = message.value
                    logger.info(f"📨 Message reçu de '{topic}': {data}")
                    
                    # Callback (vers app.py)
                    if self.callback:
                        self.callback(topic, data)

                except json.JSONDecodeError as e:
                    logger.error(f"Erreur lors du décodage du message: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la consommation de '{topic}': {e}")
    
    def stop_consuming(self):
        """Arrête la consommation des messages"""
        self.running = False
        
        for topic, consumer in self.consumers.items():
            try:
                consumer.close()
                logger.info(f"Consumer pour '{topic}' fermé")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du consumer '{topic}': {e}")
        
        self.consumers.clear()
        self.threads.clear()


# ======================================================================
# Fake Data Generators
# ======================================================================

def generate_fake_order():
    """Génère une commande fictive"""
    return {
        'order_id': fake.uuid4(),
        'customer_name': fake.name(),
        'customer_email': fake.email(),
        'product': fake.word(),
        'amount': round(float(fake.random.randint(10, 500)), 2),
        'status': fake.random_element(['Pending', 'Processing', 'Completed']),
        'timestamp': datetime.now().isoformat(),
        'address': fake.address().replace('\n', ', ')
    }


def generate_fake_payment():
    """Génère un paiement fictif"""
    return {
        'payment_id': fake.uuid4(),
        'order_id': fake.uuid4(),
        'amount': round(float(fake.random.randint(10, 500)), 2),
        'method': fake.random_element(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer']),
        'status': fake.random_element(['SUCCESS', 'FAILED']),
        'timestamp': datetime.now().isoformat()
    }


def generate_fake_delivery():
    """Génère une livraison fictive"""
    return {
        'delivery_id': fake.uuid4(),
        'order_id': fake.uuid4(),
        'address': fake.address().replace('\n', ', '),
        'status': fake.random_element(['Pending', 'In Transit', 'Delivered']),
        'estimated_date': str(fake.date_this_month()),
        'timestamp': datetime.now().isoformat()
    }
