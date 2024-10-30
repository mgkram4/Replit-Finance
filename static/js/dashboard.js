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
                            'rgba(52, 152, 219, 0.8)',  // Blue
                            'rgba(46, 204, 113, 0.8)',  // Green
                            'rgba(155, 89, 182, 0.8)',  // Purple
                            'rgba(241, 196, 15, 0.8)',  // Yellow
                            'rgba(231, 76, 60, 0.8)',   // Red
                            'rgba(52, 73, 94, 0.8)'     // Dark Blue
                        ],
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: {
                                    size: 12,
                                    family: "'Inter', sans-serif"
                                },
                                color: 'rgb(255, 255, 255)'
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: {
                                size: 14,
                                family: "'Inter', sans-serif"
                            },
                            bodyFont: {
                                size: 13,
                                family: "'Inter', sans-serif"
                            },
                            displayColors: true,
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    return `$${value.toFixed(2)}`;
                                }
                            }
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true,
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        });
});
