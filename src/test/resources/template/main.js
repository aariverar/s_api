document.addEventListener('DOMContentLoaded', function() {
    ['chart-scenarios', 'chart-steps'].forEach(function(className) {
        var canvases = document.getElementsByClassName(className);
        Array.prototype.forEach.call(canvases, function(canvas) {
            var featurePassedCount = parseInt(canvas.getAttribute('data-passed'));
            var featureFailedCount = parseInt(canvas.getAttribute('data-failed'));
            var featureSkippedCount = parseInt(canvas.getAttribute('data-skipped'));
            var featureName = canvas.getAttribute('data-feature-name');
            var ctx = canvas.getContext('2d');
            var data = [featurePassedCount, featureFailedCount, featureSkippedCount];
            var myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Passed', 'Failed', 'Skipped'],
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            'rgba(75, 192, 120, 0.2)',  // Color for 'Passed'
                            'rgba(255, 99, 132, 0.2)',  // Color for 'Failed'
                            '#ede9e9c5'  // Color for 'Skipped'
                        ],
                        borderColor: [
                            'rgba(75, 192, 120, 0.245)',
                            'rgba(255, 99, 133, 0.221)',
                            '#c8c6c6c5'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: className === 'chart-scenarios' ? "Scenarios" : "Steps",
                            font: {
                                size: 20 
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    var label = context.label || '';
                                    var value = context.parsed;
                                    var total = context.dataset.data.reduce(function(a, b) {
                                        return a + b;
                                    }, 0);
                                    var percentage = ((value / total) * 100).toFixed(2);
                                    return label + ': ' + value + ' (' + percentage + '%)';
                                }
                            }
                        }
                    }
                },
            });
        });
    });
});