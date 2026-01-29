// Connexion Socket.IO
const socket = io();

// Variables globales
let currentFilter = 'all';
let deliveryCount = 0;

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// Configuration des event listeners
function setupEventListeners() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Retirer la classe active de tous les boutons
            filterButtons.forEach(b => b.classList.remove('active'));
            
            // Ajouter la classe active au bouton cliqué
            this.classList.add('active');
            
            // Mettre à jour le filtre
            currentFilter = this.getAttribute('data-filter');
            filterDeliveries(currentFilter);
        });
    });
    
    // Activer le premier bouton par défaut
    if (filterButtons.length > 0) {
        filterButtons[0].classList.add('active');
    }
}

// Ajouter une livraison à la table
function addDeliveryToTable(delivery) {
    const tbody = document.getElementById('deliveriesTableBody');
    
    // Supprimer le message "Aucune livraison"
    if (tbody.children.length === 1 && tbody.children[0].querySelector('.text-muted')) {
        tbody.innerHTML = '';
    }

    const row = document.createElement('tr');
    row.classList.add('fade-in');
    row.setAttribute('data-status', delivery.status);

    let statusColor = 'secondary';
    let statusIcon = '📦';
    if (delivery.status === 'Pending') {
        statusColor = 'warning';
        statusIcon = '📦';
    } else if (delivery.status === 'In Transit') {
        statusColor = 'info';
        statusIcon = '🚚';
    } else if (delivery.status === 'Delivered') {
        statusColor = 'success';
        statusIcon = '✅';
    }

    const progressValue = delivery.status === 'Delivered' ? 100 : (delivery.status === 'In Transit' ? 50 : 10);

    const date = new Date(delivery.timestamp);
    const formattedDate = date.toLocaleDateString('fr-FR');

    row.innerHTML = `
        <td><code>${delivery.delivery_id.substring(0, 8)}...</code></td>
        <td><code>${delivery.order_id.substring(0, 8)}...</code></td>
        <td>${delivery.address}</td>
        <td><span class="badge badge-${statusColor}">${statusIcon} ${delivery.status}</span></td>
        <td>${delivery.estimated_date || formattedDate}</td>
        <td>
            <div class="progress" style="height: 10px;">
                <div class="progress-bar" style="width: ${progressValue}%"></div>
            </div>
        </td>
    `;

    tbody.insertBefore(row, tbody.firstChild);
    deliveryCount++;

    // Limiter à 50 livraisons
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Ajouter une livraison à la timeline
function addDeliveryToTimeline(delivery) {
    const timeline = document.getElementById('deliveryTimeline');
    
    // Supprimer le message "Aucune livraison"
    if (timeline.children.length === 1 && timeline.querySelector('.text-muted')) {
        timeline.innerHTML = '';
    }

    const item = document.createElement('div');
    item.classList.add('timeline-item', 'fade-in');
    item.setAttribute('data-status', delivery.status);

    let statusColor = 'pending';
    let statusIcon = '📦';
    if (delivery.status === 'Pending') {
        statusColor = 'pending';
        statusIcon = '📦';
    } else if (delivery.status === 'In Transit') {
        statusColor = 'in-transit';
        statusIcon = '🚚';
    } else if (delivery.status === 'Delivered') {
        statusColor = 'delivered';
        statusIcon = '✅';
    }

    item.innerHTML = `
        <div class="timeline-icon ${statusColor}">
            ${statusIcon}
        </div>
        <div class="timeline-content">
            <h6>Livraison #${delivery.delivery_id.substring(0, 8)}</h6>
            <p><strong>Commande:</strong> ${delivery.order_id.substring(0, 8)}...</p>
            <p><strong>Adresse:</strong> ${delivery.address}</p>
            <p><strong>Statut:</strong> <span class="badge badge-${statusColor}">${delivery.status}</span></p>
            <p><strong>Date estimée:</strong> ${delivery.estimated_date || new Date(delivery.timestamp).toLocaleDateString('fr-FR')}</p>
        </div>
    `;

    timeline.insertBefore(item, timeline.firstChild);

    // Limiter à 10 livraisons dans la timeline
    while (timeline.children.length > 10) {
        timeline.removeChild(timeline.lastChild);
    }
}

// Filtrer les livraisons par statut
function filterDeliveries(status) {
    const rows = document.querySelectorAll('#deliveriesTableBody tr[data-status]');
    rows.forEach(row => {
        if (status === 'all' || row.getAttribute('data-status') === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    const timelineItems = document.querySelectorAll('#deliveryTimeline .timeline-item[data-status]');
    timelineItems.forEach(item => {
        if (status === 'all' || item.getAttribute('data-status') === status) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Listener Socket.IO
socket.on('new_delivery', function(delivery) {
    addDeliveryToTable(delivery);
    addDeliveryToTimeline(delivery);
});

socket.on('connect', function() {
    console.log('Connecté au serveur');
});

socket.on('disconnect', function() {
    console.log('Déconnecté du serveur');
});
