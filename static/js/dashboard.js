document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/expense_stats')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('expenseChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#F44336',
                            '#FFC107',
                            '#9C27B0',
                            '#FF9800'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        });
});
