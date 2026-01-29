// Connexion Socket.IO
const socket = io();

// Variables globales
let paymentPieChart = null;
let paymentCount = 0;

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    setupEventListeners();
});

// Initialiser le graphique circulaire
function initChart() {
    const ctx = document.getElementById('paymentPieChart');
    if (ctx) {
        paymentPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Succès', 'Échecs'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: [
                        '#27ae60',
                        '#e74c3c'
                    ],
                    borderColor: [
                        '#fff',
                        '#fff'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                }
            }
        });
    }
}

// Configuration des event listeners
function setupEventListeners() {
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', submitPayment);
    }
}

// Soumettre le formulaire de paiement
function submitPayment(e) {
    e.preventDefault();

    const orderId = document.getElementById('orderId').value;
    const method = document.getElementById('paymentMethod').value;
    const amount = parseFloat(document.getElementById('amount').value);

    // Valider le formulaire
    if (!orderId || !method || !amount || amount <= 0) {
        alert('Veuillez remplir tous les champs correctement');
        return;
    }

    const paymentData = {
        payment_id: generateUUID(),
        order_id: orderId,
        method: method,
        amount: amount,
        status: Math.random() > 0.1 ? 'SUCCESS' : 'FAILED',
        timestamp: new Date().toISOString()
    };

    fetch('/api/payments/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(paymentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Réinitialiser le formulaire
            document.getElementById('paymentForm').reset();
            // Jouer un son de notification
            playNotificationSound();
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la création du paiement');
    });
}

// Ajouter un paiement au tableau
function addPaymentToTable(payment) {
    const tbody = document.getElementById('paymentsTableBody');
    
    // Supprimer le message "Aucun paiement"
    if (tbody.children.length === 1 && tbody.children[0].querySelector('.text-muted')) {
        tbody.innerHTML = '';
    }

    const row = document.createElement('tr');
    row.classList.add('fade-in');

    let statusColor = 'secondary';
    let statusText = payment.status;
    if (payment.status === 'SUCCESS') {
        statusColor = 'success';
        statusText = 'Succès';
    } else if (payment.status === 'FAILED') {
        statusColor = 'danger';
        statusText = 'Échec';
    }

    const date = new Date(payment.timestamp);
    const formattedDate = date.toLocaleString('fr-FR');
    const formattedAmount = payment.amount.toFixed(2);

    row.innerHTML = `
        <td><code>${payment.payment_id.substring(0, 8)}...</code></td>
        <td><code>${payment.order_id.substring(0, 8)}...</code></td>
        <td>${payment.method}</td>
        <td>${formattedAmount} €</td>
        <td><span class="badge badge-${statusColor}">${statusText}</span></td>
        <td>${formattedDate}</td>
    `;

    tbody.insertBefore(row, tbody.firstChild);
    paymentCount++;

    // Limiter à 50 paiements
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Mettre à jour le graphique circulaire
function updatePieChart(data) {
    if (paymentPieChart) {
        paymentPieChart.data.datasets[0].data = [
            data.success_payments,
            data.failed_payments
        ];
        paymentPieChart.update();
    }
}

// Jouer un son de notification
function playNotificationSound() {
    // Créer un son simple avec la Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// Générer un UUID simple
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

// Listener Socket.IO
socket.on('new_payment', function(payment) {
    addPaymentToTable(payment);
    
    // Récupérer les statistiques mises à jour
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updatePieChart(data);
        });
});

socket.on('connect', function() {
    console.log('Connecté au serveur');
});

socket.on('disconnect', function() {
    console.log('Déconnecté du serveur');
});
