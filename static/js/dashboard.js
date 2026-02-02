// Connexion Socket.IO
const socket = io();

// Variables globales
let ordersChart = null;
let paymentsChart = null;
let activityCount = 0;

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    updateStats();
    
    // // Auto-rafraîchir les stats toutes les 5 secondes
    // setInterval(updateStats, 5000);
});


// Initialiser les graphiques
function initCharts() {
    // Graphique des commandes par heure
    const ordersCtx = document.getElementById('ordersChart');
    if (ordersCtx) {
        ordersChart = new Chart(ordersCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Commandes',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // Graphique des paiements
    const paymentsCtx = document.getElementById('paymentsChart');
    if (paymentsCtx) {
        paymentsChart = new Chart(paymentsCtx, {
            type: 'bar',
            data: {
                labels: ['Succès', 'Échecs'],
                datasets: [{
                    label: 'Paiements',
                    data: [0, 0],
                    backgroundColor: [
                        '#27ae60',
                        '#e74c3c'
                    ],
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

// Mettre à jour les statistiques
socket.on('stats_update', function(stats) {
    document.getElementById('totalOrders').textContent = stats.total_orders;
    document.getElementById('successPayments').textContent = stats.success_payments;
    document.getElementById('totalDeliveries').textContent = stats.total_deliveries;
    document.getElementById('totalRevenue').textContent = stats.total_revenue.toFixed(2) + ' €';
});



function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalOrders').textContent = data.total_orders;
            document.getElementById('successPayments').textContent = data.success_payments;
            document.getElementById('totalDeliveries').textContent = data.total_deliveries;
            document.getElementById('totalRevenue').textContent = data.total_revenue.toFixed(2) + ' €';

            // Mettre à jour les graphiques
            updateCharts(data);
        })
        .catch(error => console.error('Erreur:', error));
}

// Mettre à jour les graphiques
function updateCharts(data) {
    if (paymentsChart) {
        paymentsChart.data.datasets[0].data = [
            data.success_payments,
            data.failed_payments
        ];
        paymentsChart.update();
    }
}

// Listeners Socket.IO
socket.on('new_order', function(order) {
    addActivityToTable('Commande', order.customer_name, order.amount + ' €', 'Pending');
});

socket.on('new_payment', function(payment) {
    const statusBadge = payment.status === 'SUCCESS' ? 'Succès' : 'Échec';
    addActivityToTable('Paiement', payment.method, payment.amount + ' €', statusBadge);
});

socket.on('new_delivery', function(delivery) {
    addActivityToTable('Livraison', delivery.address, '-', delivery.status);
});

// Ajouter une activité au tableau
function addActivityToTable(type, description, amount, status) {
    const tbody = document.getElementById('activitiesTableBody');
    
    // Supprimer le message "En attente"
    if (tbody.children.length === 1 && tbody.children[0].querySelector('.text-muted')) {
        tbody.innerHTML = '';
    }

    const row = document.createElement('tr');
    row.classList.add('fade-in');
    
    let statusColor = 'secondary';
    if (status === 'Succès') statusColor = 'success';
    if (status === 'Échec') statusColor = 'danger';
    if (status === 'Pending') statusColor = 'warning';
    if (status === 'In Transit') statusColor = 'info';
    if (status === 'Delivered') statusColor = 'success';

    row.innerHTML = `
        <td><strong>${type}</strong></td>
        <td>${description}</td>
        <td>${amount}</td>
        <td>${new Date().toLocaleTimeString('fr-FR')}</td>
        <td><span class="badge badge-${statusColor}">${status}</span></td>
    `;

    tbody.insertBefore(row, tbody.firstChild);

    // Limiter à 10 activités
    while (tbody.children.length > 10) {
        tbody.removeChild(tbody.lastChild);
    }
}
