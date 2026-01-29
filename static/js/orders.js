// Connexion Socket.IO
const socket = io();

// Variables globales
let autoGenerate = false;
let autoGenerateInterval = null;
let orderCount = 0;

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// Configuration des event listeners
function setupEventListeners() {
    // Bouton "Créer une commande"
    const createOrderBtn = document.getElementById('createOrderBtn');
    if (createOrderBtn) {
        createOrderBtn.addEventListener('click', createOrder);
    }

    // Bouton "Auto-Générer"
    const autoGenerateBtn = document.getElementById('autoGenerateBtn');
    if (autoGenerateBtn) {
        autoGenerateBtn.addEventListener('click', toggleAutoGenerate);
    }
}

// Créer une commande
function createOrder() {
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
            console.log('Commande créée:', data.order);
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la création de la commande');
    });
}

// Toggle auto-génération
function toggleAutoGenerate() {
    const btn = document.getElementById('autoGenerateBtn');
    
    if (autoGenerate) {
        // Arrêter l'auto-génération
        clearInterval(autoGenerateInterval);
        autoGenerate = false;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-success');
        btn.innerHTML = '<i class="fas fa-play"></i> Auto-Générer';
    } else {
        // Démarrer l'auto-génération
        autoGenerate = true;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-danger');
        btn.innerHTML = '<i class="fas fa-pause"></i> Arrêter';

        // Créer une commande toutes les 2 secondes
        autoGenerateInterval = setInterval(createOrder, 2000);
    }
}

// Ajouter une commande au tableau
function addOrderToTable(order) {
    const tbody = document.getElementById('ordersTableBody');
    
    // Supprimer le message "Aucune commande"
    if (tbody.children.length === 1 && tbody.children[0].querySelector('.text-muted')) {
        tbody.innerHTML = '';
    }

    const row = document.createElement('tr');
    row.classList.add('fade-in');

    let statusColor = 'secondary';
    if (order.status === 'Pending') statusColor = 'warning';
    if (order.status === 'Processing') statusColor = 'info';
    if (order.status === 'Completed') statusColor = 'success';

    const date = new Date(order.timestamp);
    const formattedDate = date.toLocaleString('fr-FR');
    const formattedAmount = parseFloat(order.amount).toFixed(2);

    row.innerHTML = `
        <td><code>${order.order_id.substring(0, 8)}...</code></td>
        <td>${order.customer_name}</td>
        <td>${order.product}</td>
        <td>${formattedAmount} €</td>
        <td>${formattedDate}</td>
        <td><span class="badge badge-${statusColor}">${order.status}</span></td>
    `;

    tbody.insertBefore(row, tbody.firstChild);
    orderCount++;

    // Limiter à 50 commandes
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Listener Socket.IO
socket.on('new_order', function(order) {
    addOrderToTable(order);
});

socket.on('connect', function() {
    console.log('Connecté au serveur');
});

socket.on('disconnect', function() {
    console.log('Déconnecté du serveur');
});
