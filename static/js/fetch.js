import {createBarChart,createPieChart,createBoxPlot,createElbowMethodChart} from "./chart-d3.js";
    //DOM Elements 
    const ctx_data_missing_or_null = 'data_missing_or_null';
    const ctx_sum_status_siswa = 'sum_status_siswa';
    const ctx_boxplot = 'boxplot';
    const ctx_elbow_method = 'elbow_method';
    

    // Data for the chart
fetch("/api/data/visualization")
    .then(response=> response.json())
    .then(data => {
        //bar chart missing value
        const missing_value =  data.missing_value
        createBarChart(ctx_data_missing_or_null, missing_value);

        // pie chart sum_status_siswa
        const sum_status = data.sum_status
        createPieChart(ctx_sum_status_siswa, sum_status);

        // elbow method 
        const distortion = data.elbow_method
        console.log(distortion.distortions)
        createElbowMethodChart(ctx_elbow_method, distortion);


    })
fetch("/api/data/boxplot")
    .then(response=> response.json())
    .then(data => {
        //boxplot
        const boxplot = data.data
        createBoxPlot(ctx_boxplot, boxplot);
    })
// Fungsi untuk membuat Bar Chart
