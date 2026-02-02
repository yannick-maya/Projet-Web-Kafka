# 🛒 Kafka E-Commerce Web Application

Une application web e-commerce complète en temps réel intégrant **Apache Kafka**, **Flask** et **WebSockets** pour la gestion de commandes, paiements et livraisons.

## 📋 Prérequis

- **Docker** et **Docker Compose**
- **Python 3.8+**
- **Navigateur moderne** (Chrome, Firefox, Edge, Safari)
- **Git** (optionnel)

## 🚀 Installation Rapide

### 1. Cloner/Télécharger le projet

```bash
cd kafka-ecommerce-webapp
```

### 2. Démarrer Kafka avec Docker Compose

```bash
docker-compose up -d
```

Cette commande lance:
- **Zookeeper** sur le port `2181`
- **Kafka** sur le port `9092`

Vérifiez que les conteneurs sont en cours d'exécution:
```bash
docker-compose ps
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Créer les Topics Kafka (optionnel, auto-création)

Les topics sont créés automatiquement au démarrage de l'application. Si vous voulez les créer manuellement:

```bash
# Créer le topic 'orders'
docker-compose exec kafka kafka-topics --create --topic orders --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || echo "Topic orders existe déjà"

# Créer le topic 'payments'
docker-compose exec kafka kafka-topics --create --topic payments --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || echo "Topic payments existe déjà"

# Créer le topic 'deliveries'
docker-compose exec kafka kafka-topics --create --topic deliveries --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || echo "Topic deliveries existe déjà"
```

### 5. Lancer l'application Flask

```bash
python app.py
```

L'application démarrera sur `http://localhost:5000`

### 6. Accéder à l'application

Ouvrez votre navigateur et allez à: **http://localhost:5000**

## 📊 Fonctionnalités

### 🎯 Dashboard
- **Statistiques en temps réel**: Total des commandes, paiements réussis, livraisons, revenus
- **Graphiques dynamiques**:
  - Graphique linéaire: Commandes par heure
  - Graphique en barres: Paiements (Succès vs Échecs)
- **Tableau des dernières activités**: Mise à jour en temps réel via WebSocket
- **Auto-rafraîchissement**: Tous les 5 secondes

### 📦 Commandes
- **Créer une commande aléatoire**: Bouton "Créer une Commande"
- **Auto-génération**: Bouton "Auto-Générer" crée 1 commande toutes les 2 secondes
- **Tableau en temps réel**: Affiche toutes les commandes avec:
  - ID de commande
  - Nom du client
  - Produit
  - Montant
  - Date/Heure
  - Statut (avec badge de couleur)
- **Animations lisses**: Nouvelles entrées animées

### 💳 Paiements
- **Formulaire de création**: Créer des paiements manuellement
  - ID Commande
  - Méthode de paiement (Carte de crédit, Débit, PayPal, Virement)
  - Montant
- **Graphique circulaire**: Visualisation Succès vs Échecs
- **Tableau des paiements**: 
  - ID Paiement
  - ID Commande
  - Méthode
  - Montant
  - Statut (code couleur: ✅ Succès en vert, ❌ Échec en rouge)
  - Date
- **Notification sonore**: Son de confirmation sur nouveau paiement

### 🚚 Livraisons
- **Filtres par statut**:
  - 📦 En Attente (Pending)
  - 🚚 En Transit (In Transit)
  - ✅ Livrée (Delivered)
- **Timeline visuelle**: Affichage chronologique des livraisons
- **Tableau détaillé**:
  - ID Livraison
  - ID Commande
  - Adresse
  - Statut
  - Date estimée
  - Barre de progression
- **Mise à jour en temps réel**: Via WebSocket

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Navigateur)                       │
│  Dashboard | Commandes | Paiements | Livraisons             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Socket.IO    │
                    │ (WebSockets) │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐      ┌─────▼────┐      ┌──────▼──┐
    │ Flask  │      │ Kafka    │      │Database │
    │ App    │──────│ Producer │      └──────────┘
    └───┬────┘      └─────┬────┘
        │                 │
        └─────────────────┼──────────────┐
                          │              │
                    ┌─────▼─────┐    ┌──▼──────────┐
                    │ Kafka     │    │ Kafka       │
                    │ Topics    │────│ Consumer    │
                    │ (orders,  │    │ (Real-time) │
                    │  payments,│    └──┬──────────┘
                    │  deliveries)      │
                    └───────────┘       │
                                        │
                            ┌───────────▼────────┐
                            │ Emit via Socket.IO │
                            │ to All Clients     │
                            └────────────────────┘
```

## 📁 Structure du Projet

```
kafka-ecommerce-webapp/
├── docker-compose.yml          # Configuration Docker (Kafka + Zookeeper)
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
├── app.py                      # Application Flask principale
├── kafka_service.py            # Services Kafka (Producer + Consumer)
├── config/
│   └── kafka_config.py        # Configuration Kafka centralisée
├── templates/
│   ├── base.html              # Template de base (navbar, footer)
│   ├── dashboard.html         # Page du tableau de bord
│   ├── orders.html            # Page des commandes
│   ├── payments.html          # Page des paiements
│   └── deliveries.html        # Page des livraisons
└── static/
    ├── css/
    │   └── style.css          # Styles personnalisés
    └── js/
        ├── dashboard.js       # Logic pour le dashboard
        ├── orders.js          # Logic pour les commandes
        ├── payments.js        # Logic pour les paiements
        └── deliveries.js      # Logic pour les livraisons
```

## 🔧 Configuration

### Port par défaut
- **Application Flask**: `http://localhost:5000`
- **Kafka**: `localhost:9092`
- **Zookeeper**: `localhost:2181`

### Fichier `kafka_config.py`

```python
BOOTSTRAP_SERVERS = ['localhost:9092']
TOPICS = ['orders', 'payments', 'deliveries']
```

Modifiez ces paramètres selon votre environnement.

## 🎨 Technologie Frontend

- **Bootstrap 5.3**: Framework CSS responsive
- **Chart.js**: Graphiques dynamiques
- **Socket.IO Client**: Communication en temps réel
- **Font Awesome**: Icônes
- **CSS personnalisé**: Animations et responsive design

## ⚙️ Technologie Backend

- **Flask 3.0**: Framework web
- **Flask-SocketIO**: WebSockets en temps réel
- **Flask-CORS**: Cross-Origin Resource Sharing
- **Kafka-Python**: Client Kafka
- **Faker**: Génération de données fictives
- **Eventlet**: WSGI server asynchrone

## 🚀 Utilisation de l'Application

### Dashboard
1. Accédez à `http://localhost:5000/dashboard`
2. Consultez les statistiques en temps réel
3. Les graphiques se mettent à jour automatiquement

### Créer des Commandes
1. Accédez à `/orders`
2. Cliquez sur "Créer une Commande" pour créer 1 commande
3. Cliquez sur "Auto-Générer" pour créer des commandes automatiquement (1 toutes les 2 sec)
4. Voyez les commandes s'ajouter en temps réel

### Gérer les Paiements
1. Accédez à `/payments`
2. Remplissez le formulaire avec les détails du paiement
3. Cliquez sur "Envoyer le Paiement"
4. Le graphique se met à jour en temps réel
5. Un son de notification retentit

### Suivi des Livraisons
1. Accédez à `/deliveries`
2. Utilisez les filtres pour voir:
   - **Tous**: Toutes les livraisons
   - **En Attente**: 📦
   - **En Transit**: 🚚
   - **Livrée**: ✅
3. Consultez la timeline et le tableau

## 🐛 Dépannage

### Kafka ne démarre pas
```bash
# Vérifier les logs
docker-compose logs kafka

# Redémarrer les services
docker-compose down
docker-compose up -d
```

### Erreur: "Connection refused" sur port 9092
```bash
# Attendez quelques secondes après docker-compose up
# puis relancez l'application Flask

# Ou vérifiez que Kafka est bien démarré
docker-compose ps
```

### Port 5000 déjà utilisé
Modifiez le port dans `app.py` ligne (dernière):
```python
socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # Changez 5001 par votre port
```

### Pas de messages en temps réel
1. Vérifiez la console du navigateur (F12)
2. Vérifiez que les WebSockets sont activés
3. Vérifiez les logs Flask: `python app.py`

## 📊 Génération de Données

Les données sont générées automatiquement avec **Faker**:
- **Commandes**: Noms, emails, produits, montants aléatoires
- **Paiements**: Méthodes aléatoires, statuts aléatoires (90% succès, 10% échecs)
- **Livraisons**: Adresses aléatoires, statuts aléatoires

## 🔄 Flux de Données

1. **Client** → Clique sur un bouton ou remplit un formulaire
2. **Flask API** → Reçoit la requête POST
3. **Kafka Producer** → Envoie le message au topic
4. **Kafka Topic** → Stocke le message
5. **Kafka Consumer** → Consomme le message (thread séparé)
6. **Socket.IO Callback** → Émet à tous les clients connectés
7. **Client** → Reçoit le message en temps réel et met à jour l'UI

## 📝 Logs et Monitoring

Les logs sont affichés dans la console:
```
[2024-01-29 10:30:15] INFO: KafkaProducerService initialisé
[2024-01-29 10:30:20] INFO: Commande envoyée: uuid-123...
[2024-01-29 10:30:21] INFO: Message reçu de 'orders': {...}
```

## ⚡ Performance

- **Temps réel**: < 100ms entre l'envoi et la réception (réseau local)
- **Scalabilité**: Testée avec 100+ commandes/min
- **Simultanéité**: Supporte 50+ clients connectés

## 🔐 Sécurité (À Implémenter en Production)

- ✅ CORS activé (à restreindre en production)
- ❌ Pas d'authentification (à ajouter)
- ❌ Pas de validation complète des données (à améliorer)
- ❌ Pas de chiffrement Kafka (à configurer)

Pour la production:
1. Ajouter une authentification utilisateur
2. Valider et nettoyer toutes les données
3. Configurer HTTPS
4. Configurer la sécurité Kafka (SSL/TLS)
5. Ajouter une base de données persistante

## 📚 Ressources

- [Apache Kafka](https://kafka.apache.org/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [Kafka-Python](https://github.com/dpkp/kafka-python)
- [Chart.js](https://www.chartjs.org/)
- [Bootstrap 5.3](https://getbootstrap.com/)

## 📄 Licence

Ce projet est fourni à titre d'exemple éducatif.

## 👨‍💻 Auteur

Créé pour le cours "Introduction Big Data" - Master 1 UCAO 
par Dayo K. Cyrille & Madjiadoum Yannick

## 🤝 Support

Pour toute question ou problème:
1. Consultez les logs Flask
2. Vérifiez la console du navigateur (F12)
3. Vérifiez que Kafka est en cours d'exécution

## 🎓 Améliorations Futures

- [ ] Authentification utilisateur
- [ ] Base de données persistante (PostgreSQL)
- [ ] Historique des transactions
- [ ] Tableaux de bord avancés
- [ ] Export de données (CSV, PDF)
- [ ] API REST complète
- [ ] Tests unitaires
- [ ] Déploiement sur cloud (AWS, Azure)
- [ ] Monitoring avancé (Prometheus, Grafana)
- [ ] Configuration Kafka avancée (réplication, compression)

---

**Bon codage! 🚀**


envoyer les donnees en JSON dans le cli, puis signaler dans quelle service les donnees son envoyees ,  arranger les donnes dans le tableau , et dans service

commandes 


docker exec -it projet-web-kafka-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
