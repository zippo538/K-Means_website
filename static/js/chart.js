
var ctx = document.getElementById("myChart").getContext('2d');
function barChart() {
    var label = bar_chart_data.labels;
    var mins = bar_chart_data.mins;
    var means = bar_chart_data.means;
    var maxs = bar_chart_data.maxs;
console.log(label)
console.log(maxs)
console.log(means)
console.log(mins)
new Chart(ctx, {
        type: "bar",
        responsive: true,
        maintainAspectRatio: false,
        data: {
            labels: label,
            datasets: [
                {
                label: "Min",
                data: mins,
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 1
            },
            {
                label: "Mean",
                data: means,
                backgroundColor: "rgba(255, 206, 86, 0.2)",
                borderColor: "rgba(255, 206, 86, 1)",
                borderWidth: 1
            },
            {
                label: "Max",
                data: maxs,
                backgroundColor:"rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }
        ]
        },
        options: {
            scales: {
                xAxes: [{ stacked: true }],
                yAxes: [{ stacked: true}]
            }
        }
    });
}