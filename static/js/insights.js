
// Zyrelquora - Shopping Insights Dashboard

document.addEventListener('DOMContentLoaded', function () {

    // Read actual database data from Django
    const categoryLabels = JSON.parse(
        document.getElementById('category-labels').textContent
    );

    const categoryValues = JSON.parse(
        document.getElementById('category-values').textContent
    );

    const productLabels = JSON.parse(
        document.getElementById('product-labels').textContent
    );

    const productPrices = JSON.parse(
        document.getElementById('product-prices').textContent
    );

    const stockLabels = JSON.parse(
        document.getElementById('stock-labels').textContent
    );

    const stockValues = JSON.parse(
        document.getElementById('stock-values').textContent
    );


    // Common Chart Settings
    Chart.defaults.font.family = 'Arial';
    Chart.defaults.color = '#68647a';


    // 1. Category Distribution
    new Chart(document.getElementById('categoryChart'), {
        type: 'doughnut',

        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryValues,
                backgroundColor: [
                    '#7650c9',
                    '#a58be5',
                    '#d2c3f5',
                    '#f0b7d5',
                    '#8bb9d9',
                    '#9bc9b1'
                ],
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverOffset: 12
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: 'bottom'
                }
            },

            cutout: '65%'
        }
    });


    // 2. Stock Overview
    new Chart(document.getElementById('stockChart'), {
        type: 'doughnut',

        data: {
            labels: stockLabels,
            datasets: [{
                data: stockValues,
                backgroundColor: [
                    '#7650c9',
                    '#f0a6a6'
                ],
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverOffset: 12
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: 'bottom'
                }
            },

            cutout: '65%'
        }
    });


    // 3. Product Price Comparison
    new Chart(document.getElementById('priceChart'), {
        type: 'bar',

        data: {
            labels: productLabels,
            datasets: [{
                label: 'Product Price (₹)',
                data: productPrices,
                backgroundColor: '#9675d8',
                borderRadius: 8,
                hoverBackgroundColor: '#7650c9'
            }]
        },

        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                }
            },

            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });

});
