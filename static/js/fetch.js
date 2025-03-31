import {createBarChart,createPieChart,createBoxPlot,createElbowMethodChart, createScatterPlot,createSilhouettePlot,createTopScoreBarChart} from "./chart-d3.js";
    //DOM Elements 
    const ctx_data_missing_or_null = 'data_missing_or_null';
    const ctx_top_zero_student = 'top_zero_student';
    const ctx_boxplot = 'boxplot';
    const ctx_elbow_method = 'elbow_method';
    const ctx_kmeans_cluster = 'kMeansCluster';
    const ctx_silhouttePlot ='silhouttePlot'
    

    // Data for the chart
// fetch.js
document.addEventListener("DOMContentLoaded", function() {
    const path = window.location.pathname;

    if (path === "/") {
        // Halaman index.html (Understanding Data)
        fetch("/api/data/visualization")
            .then(response => response.json())
            .then(data => {
                // Bar chart missing value
                const missing_value = data.missing_value;
                createBarChart(ctx_data_missing_or_null, missing_value,);

                // Pie chart sum_status_siswa
                const top_zero_student = data.top_student_with_zero_;
                console.log(top_zero_student)
                createTopScoreBarChart(ctx_top_zero_student, top_zero_student);

                // Boxplot
                fetch("/api/data/boxplot")
                    .then(response => response.json())
                    .then(data => {
                        const boxplot = data.data;
                        createBoxPlot(ctx_boxplot, boxplot);
                    });
            });
    } else if (path === "/data") {
        // Halaman data.html (Normalization)
        fetch("/api/data/elbowMethod")
            .then(response => response.json())
            .then(data => {
                const distortion = data.elbow_method;
                createElbowMethodChart(ctx_elbow_method, distortion);
            });
    } else if (path === "/result") {
        // Halaman result.html (Result)
        fetch("/api/data/kmeans")
            .then(response => response.json())
            .then(data => {
                // KMeans clustering
                const kmeans = data.kmeans;
                const data_kmeans = kmeans.data;
                const cluster = kmeans.cluster;
                const cluster_center = kmeans.cluster_centers;
                const data_name = kmeans.name;
                const json_kmeans = get_data_kmeans(data_kmeans, cluster, data_name);
                const json_cluster_center = get_cluster_center(cluster_center);

                createScatterPlot(ctx_kmeans_cluster, json_kmeans, json_cluster_center);

                // Silhouette plot
                const silhouette_score = get_silhoutte_score(kmeans.silhouette_per_cluster);
                const numClusters = silhouette_score.length;
                const labels = Array.from({ length: numClusters }, (_, i) => `Cluster ${i}`);

                createSilhouettePlot(ctx_silhouttePlot, silhouette_score, labels);
            });
    }
});
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

