
    //DOM Elements 
    const ctx_data_missing_or_null = document.getElementById('data_missing_or_null');
    const ctx_sum_status_siswa = document.getElementById('sum_status_siswa');

    // Data for the chart
fetch("/api/data/visualization")
    .then(response=> response.json())
    .then(data => {
        //bar chart missing value
        const missing_value =  data.missing_value
        const data_missing_or_null = {
            x: null,
            y: missing_value.values,
            type : 'bar', 
            name : 'Missing Value'
        };
        console.log(missing_value.labels);
        Plotly.newPlot(ctx_data_missing_or_null,[data_missing_or_null]);
        // pie chart sum_status_siswa
        const sum_status = data.sum_status
        const data_sum_status = {
            values : sum_status.values,
            labels : sum_status.labels,
            type : 'pie'   
        }
        Plotly.newPlot(ctx_sum_status_siswa,[data_sum_status],{heigth: 400, width: 400});
    })
