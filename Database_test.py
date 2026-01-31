"""Script de test pour vérifier la base de données"""

from Database import Database
from kafka_service import generate_fake_order, generate_fake_payment, generate_fake_delivery

print("=" * 80)
print("🧪 TEST DE LA BASE DE DONNÉES")
print("=" * 80)

# Initialiser la base de données
db = Database()
print("✅ Base de données initialisée")

# Test 1 : Vérifier le nombre de commandes existantes
print("\n📊 Test 1 : Vérification des données existantes")
print("-" * 80)

orders = db.get_all_orders()
payments = db.get_all_payments()
deliveries = db.get_all_deliveries()

print(f"  Commandes  : {len(orders)}")
print(f"  Paiements  : {len(payments)}")
print(f"  Livraisons : {len(deliveries)}")

# Test 2 : Créer des données de test si la base est vide
if len(orders) == 0:
    print("\n⚠️  Base de données vide ! Création de données de test...")
    print("-" * 80)
    
    print("  📦 Création de 5 commandes...")
    for i in range(5):
        order = generate_fake_order()
        success = db.save_order(order)
        if success:
            print(f"    ✅ Commande {i+1} créée: {order['order_id'][:8]}... - {order['customer_name']}")
        else:
            print(f"    ❌ Erreur création commande {i+1}")
    
    print("\n  💳 Création de 3 paiements...")
    for i in range(3):
        payment = generate_fake_payment()
        success = db.save_payment(payment)
        if success:
            print(f"    ✅ Paiement {i+1} créé: {payment['payment_id'][:8]}... - {payment['status']}")
        else:
            print(f"    ❌ Erreur création paiement {i+1}")
    
    print("\n  🚚 Création de 3 livraisons...")
    for i in range(3):
        delivery = generate_fake_delivery()
        success = db.save_delivery(delivery)
        if success:
            print(f"    ✅ Livraison {i+1} créée: {delivery['delivery_id'][:8]}... - {delivery['status']}")
        else:
            print(f"    ❌ Erreur création livraison {i+1}")

# Test 3 : Relire les données
print("\n📖 Test 3 : Lecture des données après création")
print("-" * 80)

orders = db.get_all_orders()
print(f"\n  📦 {len(orders)} commandes dans la base :")
for order in orders[:5]:  # Afficher les 5 premières
    print(f"    - ID: {order['order_id'][:8]}... | Client: {order['customer_name']} | Produit: {order['product']} | Montant: {order['amount']:.2f}€")

payments = db.get_all_payments()
print(f"\n  💳 {len(payments)} paiements dans la base :")
for payment in payments[:5]:
    print(f"    - ID: {payment['payment_id'][:8]}... | Montant: {payment['amount']:.2f}€ | Statut: {payment['status']}")

deliveries = db.get_all_deliveries()
print(f"\n  🚚 {len(deliveries)} livraisons dans la base :")
for delivery in deliveries[:5]:
    print(f"    - ID: {delivery['delivery_id'][:8]}... | Statut: {delivery['status']}")

# Test 4 : Vérifier les statistiques
print("\n📊 Test 4 : Calcul des statistiques")
print("-" * 80)

stats = db.get_stats()
print(f"  Total commandes       : {stats['total_orders']}")
print(f"  Paiements réussis     : {stats['success_payments']}")
print(f"  Paiements échoués     : {stats['failed_payments']}")
print(f"  Total livraisons      : {stats['total_deliveries']}")
print(f"  Revenus totaux        : {stats['total_revenue']:.2f}€")
print(f"  Taux de succès paiements : {stats['payment_success_rate']:.2f}%")

# Test 5 : Test de l'API (si Flask tourne)
print("\n🌐 Test 5 : Test de l'API Flask")
print("-" * 80)

try:
    import requests
    
    # Tester GET /api/orders/list
    response = requests.get('http://localhost:5000/api/orders/list?limit=50')
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ API /api/orders/list fonctionne")
        print(f"     Success: {data.get('success')}")
        print(f"     Nombre de commandes: {data.get('count')}")
        if data.get('orders') and len(data['orders']) > 0:
            print(f"     Première commande: {data['orders'][0]['customer_name']}")
    else:
        print(f"  ❌ API retourne status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  ⚠️  Flask ne semble pas être en cours d'exécution")
    print("     Lancez 'python app.py' dans un autre terminal")
except ImportError:
    print("  ⚠️  Module 'requests' non installé")
    print("     Installez avec: pip install requests")

print("\n" + "=" * 80)
print("✅ TESTS TERMINÉS")
print("=" * 80)

# Afficher les prochaines étapes
print("\n📝 Prochaines étapes :")
print("  1. Si Flask ne tourne pas : python app.py")
print("  2. Ouvrir http://localhost:5000/orders")
print("  3. Ouvrir la console du navigateur (F12)")
print("  4. Vérifier les messages de débogage")
print("\n")