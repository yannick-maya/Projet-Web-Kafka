
          ARCHITECTURE DU SYSTÈME DE GESTION DES COMMANDES EN TEMPS RÉEL 

┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Navigateur)                       │
│  Dashboard | Commandes | Paiements | Livraisons               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP + WebSocket
                   ┌─────────▼─────────┐
                   │  Flask REST API   │
                   │  (/api/orders)    │
                   │  (/api/payments)  │
                   │  (/api/deliveries)│
                   └─────────┬─────────┘
                             │
         ┌───────────────────┴────────────────────┐
         │                                        │
    ┌────▼──────────┐                    ┌───────▼──────────┐
    │  Kafka        │                    │  Kafka Consumer  │
    │  Producer     │                    │  (Thread séparé) │
    │  - Envoie les │                    │  - Écoute les   │
    │    messages   │                    │    topics        │
    └────┬──────────┘                    └───────┬──────────┘
         │                                       │
         │  Envoie messages                      │ Reçoit messages
         │                                       │
         └──────────────┬──────────────┬─────────┘
                        │              │
           ┌────────────▼──────────────▼────────────┐
           │   Kafka Broker (Port 9092)             │
           │   Zookeeper (Port 2181)                │
           │                                        │
           │  ┌──────────────────────────────────┐ │
           │  │  Topic: "orders"                 │ │
           │  │  - Partition 0                   │ │
           │  │  - [msg1, msg2, msg3, ...]       │ │
           │  └──────────────────────────────────┘ │
           │                                        │
           │  ┌──────────────────────────────────┐ │
           │  │  Topic: "payments"               │ │
           │  │  Topic: "deliveries"             │ │
           │  └──────────────────────────────────┘ │
           └────────────────────────────────────────┘
                        │
                        │ Callback Function
                        │ Émet via Socket.IO
         ┌──────────────▼──────────────┐
         │   WebSocket (Socket.IO)     │
         │   - Envoie en temps réel    │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  Navigateur                 │
         │  (Tous les clients)          │
         │  - Reçoit les updates       │
         │  - Affiche en temps réel    │
         └─────────────────────────────┘