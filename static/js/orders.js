// Connexion Socket.IO
const socket = io();

// Variable pour l'auto-génération
let autoGenerate = false;
let autoGenerateInterval = null;

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    console.log(' Page Commandes chargée');
    
    // Charger les commandes existantes
    loadExistingOrders();
});

// Charger les commandes existantes depuis la base de données
function loadExistingOrders() {
    console.log(' Chargement des commandes existantes...');
    
    fetch('/api/orders/list?limit=50')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.orders) {
                console.log(` ${data.orders.length} commandes chargées`);
                
                // Ajouter chaque commande au tableau
                data.orders.reverse().forEach(order => {
                    addOrderToTable(order, false); // false = pas d'animation
                });
            }
        })
        .catch(error => {
            console.error(' Erreur chargement commandes:', error);
        });
}

// Créer une nouvelle commande
function createOrder() {
    console.log(' Création d\'une nouvelle commande...');
    
    fetch('/api/orders/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(' Commande créée:', data.order);
            // La commande sera ajoutée automatiquement via Socket.IO
        } else {
            console.error(' Erreur création commande:', data.error);
            alert('Erreur lors de la création de la commande');
        }
    })
    .catch(error => {
        console.error(' Erreur:', error);
        alert('Erreur de connexion au serveur');
    });
}

// Ajouter une commande au tableau
function addOrderToTable(order, animate = true) {
    const tbody = document.getElementById('ordersTableBody');
    
    if (!tbody) {
        console.error(' Table body non trouvé');
        return;
    }
    
    // Supprimer le message "Aucune commande"
    const emptyRow = tbody.querySelector('.text-muted');
    if (emptyRow) {
        emptyRow.remove();
    }
    
    // Vérifier si la commande existe déjà
    const existingRow = tbody.querySelector(`tr[data-order-id="${order.order_id}"]`);
    if (existingRow) {
        console.log('Commande déjà affichée:', order.order_id);
        return;
    }
    
    const row = document.createElement('tr');
    row.setAttribute('data-order-id', order.order_id);
    
    if (animate) {
        row.style.animation = 'fadeIn 0.5s ease';
    }
    
    // Badge de statut
    let statusBadge = '';
    switch(order.status) {
        case 'Pending':
            statusBadge = '<span class="badge bg-warning">En attente</span>';
            break;
        case 'Processing':
            statusBadge = '<span class="badge bg-info">En traitement</span>';
            break;
        case 'Completed':
            statusBadge = '<span class="badge bg-success">Complétée</span>';
            break;
        case 'Cancelled':
            statusBadge = '<span class="badge bg-danger">Annulée</span>';
            break;
        default:
            statusBadge = `<span class="badge bg-secondary">${order.status}</span>`;
    }
    
    row.innerHTML = `
        <td><small class="text-muted">${order.order_id.substring(0, 8)}...</small></td>
        <td><strong>${order.customer_name}</strong></td>
        <td>${order.product}</td>
        <td><strong>${parseFloat(order.amount).toFixed(2)} €</strong></td>
        <td><small>${formatTimestamp(order.timestamp)}</small></td>
        <td>${statusBadge}</td>
    `;
    
    // Insérer au début du tableau
    tbody.insertBefore(row, tbody.firstChild);
    
    // Limiter à 50 commandes
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Formater le timestamp
function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return timestamp;
    }
}

// Toggle auto-génération
function toggleAutoGenerate() {
    autoGenerate = !autoGenerate;
    
    const btn = document.getElementById('autoGenerateBtn');
    
    if (autoGenerate) {
        btn.classList.remove('btn-outline-warning');
        btn.classList.add('btn-warning');
        btn.innerHTML = '<i class="fas fa-stop"></i> Arrêter Auto-génération';
        
        // Générer une commande toutes les 2 secondes
        autoGenerateInterval = setInterval(() => {
            createOrder();
        }, 2000);
        
        console.log(' Auto-génération activée');
    } else {
        btn.classList.remove('btn-warning');
        btn.classList.add('btn-outline-warning');
        btn.innerHTML = '<i class="fas fa-sync"></i> Auto-générer';
        
        if (autoGenerateInterval) {
            clearInterval(autoGenerateInterval);
            autoGenerateInterval = null;
        }
        
        console.log(' Auto-génération désactivée');
    }
}

// ============================================================================
// SOCKET.IO EVENTS
// ============================================================================

socket.on('connect', function() {
    console.log(' Connecté au serveur Socket.IO');
});

socket.on('disconnect', function() {
    console.log(' Déconnecté du serveur Socket.IO');
});

socket.on('connect_error', function(error) {
    console.error(' Erreur de connexion Socket.IO:', error);
});

// Événement: nouvelle commande
socket.on('new_order', function(order) {
    console.log(' Nouvelle commande reçue:', order);
    addOrderToTable(order, true);
});

// Événement: données initiales (au chargement)
socket.on('initial_data', function(data) {
    console.log(' Données initiales reçues:', data);
    
    if (data.orders && data.orders.length > 0) {
        data.orders.reverse().forEach(order => {
            addOrderToTable(order, false);
        });
    }
});

// Événement: commandes chargées
socket.on('orders_loaded', function(data) {
    console.log(' Commandes chargées:', data);
    
    const tbody = document.getElementById('ordersTableBody');
    tbody.innerHTML = '';
    
    if (data.orders && data.orders.length > 0) {
        data.orders.reverse().forEach(order => {
            addOrderToTable(order, false);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Aucune commande</td></tr>';
    }
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// Bouton créer commande
document.getElementById('createOrderBtn')?.addEventListener('click', createOrder);

// Bouton auto-générer
document.getElementById('autoGenerateBtn')?.addEventListener('click', toggleAutoGenerate);

// Nettoyer l'intervalle à la fermeture de la page
window.addEventListener('beforeunload', function() {
    if (autoGenerateInterval) {
        clearInterval(autoGenerateInterval);
    }
});