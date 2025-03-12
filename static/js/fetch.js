import {createBarChart,createPieChart,createBoxPlot,createElbowMethodChart, createScatterPlot,createSilhouettePlot} from "./chart-d3.js";
    //DOM Elements 
    const ctx_data_missing_or_null = 'data_missing_or_null';
    const ctx_sum_status_siswa = 'sum_status_siswa';
    const ctx_boxplot = 'boxplot';
    const ctx_elbow_method = 'elbow_method';
    const ctx_kmeans_cluster = 'kMeansCluster';
    const ctx_silhouttePlot ='silhouttePlot'
    

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
        createElbowMethodChart(ctx_elbow_method, distortion);

        // kmeans cluster
        const kmenas = data.kmeans
        const data_kmeans = kmenas.data
        const cluster = kmenas.cluster
        const cluster_center = kmenas.cluster_centers
        const data_name = kmenas.name 
        const json_kmeans = get_data_kmeans(data_kmeans,cluster,data_name)
        const json_cluster_center = get_cluster_center(cluster_center)

        createScatterPlot(ctx_kmeans_cluster, json_kmeans, json_cluster_center);

        console.log('nilai silhoutte per score',kmenas.silhouette_per_cluster)

        // silhoutte plot
        const silhoutte_score = get_silhoutte_score(kmenas.silhouette_per_cluster);

        // Hitung jumlah cluster dan buat array labels
        const numClusters = silhoutte_score.length;
        const labels = Array.from({ length: numClusters }, (_, i) => `Cluster ${i + 1}`);

        createSilhouettePlot(ctx_silhouttePlot,silhoutte_score,labels)
        
        

    })
fetch("/api/data/boxplot")
    .then(response=> response.json())
    .then(data => {
        //boxplot
        const boxplot = data.data
        createBoxPlot(ctx_boxplot, boxplot);
    })
// Fungsi untuk membuat Bar Chart

function get_data_kmeans(data, cluster_centroid,name) {
    const json_kmeans = [];
    for (let i = 0; i < data.length; i++) {
        const subArray = data[i];
        json_kmeans.push({ x: subArray[0], y: subArray[1], cluster: cluster_centroid[i], name : name[i], isCenter: false });
    }
    return json_kmeans;
}

function get_cluster_center(cluster_center) {
    const json_cluster_center = [];
    for (let i = 0; i < cluster_center.length; i++) {
        const subArray = cluster_center[i];
        json_cluster_center.push({ x: subArray[0], y: subArray[1], cluster: i, isCenter: true });
    }
    return json_cluster_center;
}

function get_silhoutte_score(data) {
    const json_silhoutte = [];
    for (let i = 0; i < data.length; i++) {
        json_silhoutte.push(data[i]);
    }
    return json_silhoutte;
}

