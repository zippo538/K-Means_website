const options_bar_chart = {
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                font: {
                    size: 14, // Ukuran font untuk ticks sumbu Y
                    family: 'Arial', // Keluarga font
                    style: 'normal', // Gaya font (normal, italic, bold, dll.)
                    lineHeight: 1.2 // Tinggi garis
                }
            }
        },
        x: {
            ticks: {
                font: {
                    size: 14, // Ukuran font untuk ticks sumbu X
                    family: 'Arial',
                    style: 'normal',
                    lineHeight: 1.2
                }
            }
        }
    },
    plugins: {
        legend: {
            labels: {
                // This more specific font property overrides the global property
                font: {
                    size: 15,
                    family : 'Arial',
                }
            }
        }
    }
};

const options_pie_chart = {
    animation: {
        animateRotate: true
    },
    plugins: {
        legend: {
            labels: {
                // This more specific font property overrides the global property
                font: {
                    size: 15
                }
            }
        }
    }
    
};