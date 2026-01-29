"""Configuration Kafka centralisée"""

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging

# Configuration des serveurs Kafka
BOOTSTRAP_SERVERS = ['localhost:9092']

# Topics Kafka
TOPICS = ['orders', 'payments', 'deliveries']

# Configuration des consumers
CONSUMER_CONFIG = {
    'bootstrap_servers': BOOTSTRAP_SERVERS,
    'auto_offset_reset': 'earliest',
    'enable_auto_commit': True,
    'group_id': 'ecommerce-group',
    'value_deserializer': lambda m: m.decode('utf-8') if m else None,
}

# Configuration des producers
PRODUCER_CONFIG = {
    'bootstrap_servers': BOOTSTRAP_SERVERS,
    'value_serializer': lambda v: str(v).encode('utf-8'),
}

logger = logging.getLogger(__name__)


def create_topics_if_not_exist():
    """Crée les topics Kafka s'ils n'existent pas"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            client_id='kafka-admin'
        )
        
        # Créer les topics
        new_topics = [
            NewTopic(name=topic, num_partitions=1, replication_factor=1)
            for topic in TOPICS
        ]
        
        fs = admin_client.create_topics(new_topics=new_topics, validate_only=False)
        
        for topic, f in fs.items():
            try:
                f.result()  # Attendre la création
                logger.info(f"Topic '{topic}' créé avec succès")
            except TopicAlreadyExistsError:
                logger.info(f"Topic '{topic}' existe déjà")
            except Exception as e:
                logger.error(f"Erreur lors de la création du topic '{topic}': {e}")
        
        admin_client.close()
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à Kafka: {e}")
