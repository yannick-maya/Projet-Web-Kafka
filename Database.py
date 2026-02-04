"""Gestion de la base de données SQLite"""

import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='ecommerce.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des commandes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                address TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des paiements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id TEXT UNIQUE NOT NULL,
                order_id TEXT NOT NULL,
                amount REAL NOT NULL,
                method TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des livraisons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id TEXT UNIQUE NOT NULL,
                order_id TEXT NOT NULL,
                address TEXT NOT NULL,
                status TEXT NOT NULL,
                estimated_date TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(" Base de données initialisée")
    
    # ========== ORDERS ==========
    
    def save_order(self, order_data):
        """Sauvegarde une commande"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO orders 
                (order_id, customer_name, customer_email, product, amount, status, address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_data['order_id'],
                order_data['customer_name'],
                order_data.get('customer_email', ''),
                order_data['product'],
                order_data['amount'],
                order_data['status'],
                order_data.get('address', ''),
                order_data['timestamp']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f" Commande sauvegardée: {order_data['order_id']}")
            return True
        except Exception as e:
            logger.error(f" Erreur sauvegarde commande: {e}")
            return False
    
    def get_all_orders(self, limit=50):
        """Récupère toutes les commandes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT order_id, customer_name, customer_email, product, amount, status, address, timestamp
                FROM orders
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            orders = []
            for row in rows:
                orders.append({
                    'order_id': row[0],
                    'customer_name': row[1],
                    'customer_email': row[2],
                    'product': row[3],
                    'amount': row[4],
                    'status': row[5],
                    'address': row[6],
                    'timestamp': row[7]
                })
            
            return orders
        except Exception as e:
            logger.error(f" Erreur récupération commandes: {e}")
            return []
    
    # ========== PAYMENTS ==========
    
    def save_payment(self, payment_data):
        """Sauvegarde un paiement"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO payments 
                (payment_id, order_id, amount, method, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                payment_data['payment_id'],
                payment_data['order_id'],
                payment_data['amount'],
                payment_data['method'],
                payment_data['status'],
                payment_data['timestamp']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f" Paiement sauvegardé: {payment_data['payment_id']}")
            return True
        except Exception as e:
            logger.error(f" Erreur sauvegarde paiement: {e}")
            return False
    
    def get_all_payments(self, limit=50):
        """Récupère tous les paiements"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT payment_id, order_id, amount, method, status, timestamp
                FROM payments
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            payments = []
            for row in rows:
                payments.append({
                    'payment_id': row[0],
                    'order_id': row[1],
                    'amount': row[2],
                    'method': row[3],
                    'status': row[4],
                    'timestamp': row[5]
                })
            
            return payments
        except Exception as e:
            logger.error(f" Erreur récupération paiements: {e}")
            return []
    
    # ========== DELIVERIES ==========
    
    def save_delivery(self, delivery_data):
        """Sauvegarde une livraison"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO deliveries 
                (delivery_id, order_id, address, status, estimated_date, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                delivery_data['delivery_id'],
                delivery_data['order_id'],
                delivery_data['address'],
                delivery_data['status'],
                delivery_data.get('estimated_date', ''),
                delivery_data['timestamp']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f" Livraison sauvegardée: {delivery_data['delivery_id']}")
            return True
        except Exception as e:
            logger.error(f" Erreur sauvegarde livraison: {e}")
            return False
    
    def get_all_deliveries(self, limit=50):
        """Récupère toutes les livraisons"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT delivery_id, order_id, address, status, estimated_date, timestamp
                FROM deliveries
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            deliveries = []
            for row in rows:
                deliveries.append({
                    'delivery_id': row[0],
                    'order_id': row[1],
                    'address': row[2],
                    'status': row[3],
                    'estimated_date': row[4],
                    'timestamp': row[5]
                })
            
            return deliveries
        except Exception as e:
            logger.error(f" Erreur récupération livraisons: {e}")
            return []
    
    # ========== STATISTICS ==========
    
    def get_stats(self):
        """Calcule les statistiques"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Compter les commandes
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM orders')
            total_orders, total_revenue = cursor.fetchone()
            
            # Compter les paiements
            cursor.execute('SELECT COUNT(*) FROM payments WHERE status = "SUCCESS"')
            success_payments = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM payments WHERE status = "FAILED"')
            failed_payments = cursor.fetchone()[0]
            
            # Compter les livraisons
            cursor.execute('SELECT COUNT(*) FROM deliveries')
            total_deliveries = cursor.fetchone()[0]
            
            conn.close()
            
            total_payments = success_payments + failed_payments
            payment_success_rate = (success_payments / total_payments * 100) if total_payments > 0 else 0
            
            return {
                'total_orders': total_orders,
                'total_payments': total_payments,
                'success_payments': success_payments,
                'failed_payments': failed_payments,
                'total_deliveries': total_deliveries,
                'total_revenue': float(total_revenue),
                'payment_success_rate': round(payment_success_rate, 2)
            }
        except Exception as e:
            logger.error(f" Erreur calcul statistiques: {e}")
            return {
                'total_orders': 0,
                'total_payments': 0,
                'success_payments': 0,
                'failed_payments': 0,
                'total_deliveries': 0,
                'total_revenue': 0.0,
                'payment_success_rate': 0.0
            }
    
    def clear_all_data(self):
        """Supprime toutes les données (pour tests)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM orders')
            cursor.execute('DELETE FROM payments')
            cursor.execute('DELETE FROM deliveries')
            
            conn.commit()
            conn.close()
            logger.info(" Toutes les données ont été supprimées")
            return True
        except Exception as e:
            logger.error(f" Erreur suppression données: {e}")
            return False