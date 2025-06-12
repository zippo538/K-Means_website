import {colors} from './colors-chart.js';

function createBarChart(containerId, data, width = 600, height = 450) {
    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    const x = d3.scaleBand()
        .domain(data.labels)
        .range([0, innerWidth])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data.values)])
        .nice()
        .range([innerHeight, 0]);
    
    svg.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -margin.top /2 + 10)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Jumlah nilai 0 setiap kolom");

    svg.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.selectAll(".bar")
        .data(data.values)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => x(data.labels[i]))
        .attr("y", d => y(d))
        .attr("width", x.bandwidth())
        .attr("fill", (d, i) => colors[i % 3])
        .attr("height", d => innerHeight - y(d));

    svg.selectAll(".bar-label")
        .data(data.values)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", (d, i) => x(data.labels[i]) + x.bandwidth() / 2) // Posisi horizontal di tengah bar
        .attr("y", d => y(d) - 5) // Posisi vertikal di atas bar
        .attr("text-anchor", "middle","") // Teks di tengah
        .text(d => d); // Menampilkan nilai
}

// Fungsi untuk membuat Pie Chart
function createPieChart(containerId, data, width = 800, height = 400) {
    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const radius = Math.min(width, height) / 2;

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    

    const pie = d3.pie()
        .value(d => d);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius);

    svg.append("text")
        .attr("y", height / 2 + margin.bottom) 
        .attr("x", margin.left / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Jumlah Status Siswa terhadap kelulusan SKD");

    // Animasi untuk pie chart
    const arcs = svg.selectAll(".arc")
        .data(pie(data.values))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", (d, i) => colors[i%3])
        .transition() // Menambahkan animasi
        .duration(1000) // Durasi animasi (1 detik)
        .attrTween("d", function(d) {
            const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d); // Interpolasi dari 0 ke sudut akhir
            return function(t) {
                return arc(interpolate(t));
            };
        });

    // Menambahkan teks (nilai dan label) di setiap slice
    arcs.append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`) // Posisi teks di tengah slice
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em") // Penyesuaian vertikal
        .text(d => `${d.data} (${data.labels[d.index]})`) // Menampilkan nilai dan label
        .style("fill", "white") // Warna teks
        .style("font-size", "15px");
}

function createBoxPlot(containerId, data, width = 1600, height = 600) {
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Warna untuk setiap box

        // Skala dan sumbu
        const x = d3.scaleBand().range([0, innerWidth]).padding(0.1);
        const y = d3.scaleLinear().range([innerHeight, 0]);

        // SVG container
        const svg = d3.select(`#${containerId}`)
            .append("svg")
            .attr("width", innerWidth + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
        
        svg.append("text")
            .attr("x", innerWidth / 2)
            .attr("y", -margin.top / 2 + 10)
            .attr("text-anchor", "middle")
            .style("font-size", "20px")
            .text("Box Plot Nilai Try Out");

        // Fungsi untuk menggambar box plot
            // Hitung statistik untuk setiap kategori
        const categories = Object.keys(data);
        const boxPlotData = categories.map((category,index ) => {
            const values = data[category];
            const sortedValues = values.sort(d3.ascending);
            const q1 = d3.quantile(sortedValues, 0.25);
            const median = d3.quantile(sortedValues, 0.5);
            const q3 = d3.quantile(sortedValues, 0.75);
            const iqr = q3 - q1; // Interquartile range
            const min = Math.max(sortedValues[0], q1 - 1.5 * iqr);
            const max = Math.min(sortedValues[sortedValues.length - 1], q3 + 1.5 * iqr);
            const outliers = sortedValues.filter((v) => v < min || v > max);
            return { category, min, q1, median, q3, max, outliers, index: index + 1 }; 
            });

            // Update skala
        x.domain(boxPlotData.map((d) => d.index));
        y.domain([d3.min(boxPlotData, (d) => d.min), d3.max(boxPlotData, (d) => d.max)]);

        // Gambar box untuk setiap kategori
        const boxes = svg.selectAll(".box")
            .data(boxPlotData)
            .enter()
            .append("g")
            .attr("transform", (d) => `translate(${x(d.index)},0)`);

        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0)
            .style("position", "absolute")
            .style("background", "white")
            .style("border", "1px solid #ccc")
            .style("padding", "10px")
            .style("border-radius", "5px")
            .style("pointer-events", "none"); 
        

            // Gambar kotak (box)
        boxes.append("rect")
            .attr("class", "box")
            .attr("x", 0)
            .attr("y", (d) => y(d.q3))
            .attr("width", x.bandwidth())
            .attr("height", (d) => y(d.q1) - y(d.q3))
            .attr("fill", (d, i) => colors[i % 3])
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 0.7)
            

            // Gambar garis median
        boxes.append("line")
            .attr("class", "median")
            .attr("x1", 0)
            .attr("x2", x.bandwidth())
            .attr("y1", (d) => y(d.median))
            .attr("y2", (d) => y(d.median))
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 1);

            // Gambar garis whisker (min dan max)
        boxes.append("line")
            .attr("class", "whisker")
            .attr("x1", x.bandwidth() / 2)
            .attr("x2", x.bandwidth() / 2)
            .attr("y1", (d) => y(d.min))
            .attr("y2", (d) => y(d.max))
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 1);

            // Gambar garis horizontal di ujung whisker
        boxes.append("line")
            .attr("class", "whisker")
            .attr("x1", 0)
            .attr("x2", x.bandwidth())
            .attr("y1", (d) => y(d.min))
            .attr("y2", (d) => y(d.min))
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 1);

        boxes.append("line")
            .attr("class", "whisker")
            .attr("x1", 0)
            .attr("x2", x.bandwidth())
            .attr("y1", (d) => y(d.max))
            .attr("y2", (d) => y(d.max))
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 1);
        
            //outlier
        boxes.selectAll(".outlier")
            .data((d) => d.outliers)
            .enter()
            .append("circle")
            .attr("class", "outlier")
            .attr("cx", x.bandwidth() / 2)
            .attr("cy", (d) => y(d))
            .attr("r", 3)
            .attr("fill", "red")
            .attr("opacity", 0) // Mulai dengan opacity 0 untuk animasi
            .transition() // Animasi
            .duration(1000)
            .attr("opacity", 1);


            // Sumbu X
        svg.append("g")
            .attr("transform", `translate(0,${innerHeight})`)
            .call(d3.axisBottom(x));

            // Sumbu Y
        svg.append("g")
            .call(d3.axisLeft(y));
        
            const legend = svg.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(0, ${innerHeight + 40})`) // Posisi di bawah sumbu X
            .attr("height", 100); // Tinggi legenda

        

    
        const legendData = [
            { label: "Outlier", color: "red" },
        ];
    
        legend.selectAll(".legend-item")
            .data(legendData)
            .enter()
            .append("g")
            .attr("class", "legend-item")
            .attr("transform", (d, i) => `translate(0, ${i * 20})`)
            .each(function (d) {
                const g = d3.select(this);
                g.append("rect")
                    .attr("width", 18)
                    .attr("height", 18)
                    .attr("fill", d.color);
                g.append("text")
                    .attr("x", 24)
                    .attr("y", 9)
                    .attr("dy", "0.35em")
                    .text(d.label);
            });
}

function createElbowMethodChart(containerId, inertiaData, width = 800, height = 450) {
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    const data = inertiaData.distortions;
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Skala dan sumbu
    const x = d3.scaleLinear()
        .domain([1, data.length]) // Jumlah cluster dimulai dari 1
        .range([0, innerWidth]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data)]) // Nilai inertia
        .range([innerHeight, 0]);

    // SVG container
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Garis untuk elbow method
    const line = d3.line()
        .x((d, i) => x(i + 1)) // Jumlah cluster dimulai dari 1
        .y((d) => y(d));
    
    // tooltip
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("pointer-events", "none"); 



    // Gambar garis
    svg.append("path")
        .datum(data)
        .attr("class", "elbow-line")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", colors[0])
        .attr("stroke-width", 5);

    // Gambar titik-titik data
    svg.selectAll(".elbow-point")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "elbow-point")
        .attr("cx", (d, i) => x(i + 1)) // Jumlah cluster dimulai dari 1
        .attr("cy", (d) => y(d))
        .attr("r", 5)
        .attr("fill", colors[1])
        .attr("stroke-width", 4)
        .on("mouseover", (event, d) => {
            // Tampilkan tooltip
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
            tooltip.html(`distortions: ${d}`)
                .style("left", `${event.pageX + 5}px`)
                .style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", () => {
            // Sembunyikan tooltip
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
        ;

    // Sumbu X
    svg.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format("d")))
        .append("text")
        .attr("x", innerWidth / 2)
        .attr("y", 40)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .text("Number of Clusters (k)");

    // Sumbu Y
    svg.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -innerHeight / 2)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .text("Inertia (WCSS)");

    // Judul chart
    svg.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .text("Elbow Method for Optimal k");
}

function createScatterPlot(containerId, data, clusterCenters, width = 800, height = 450) {
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Skala dan sumbu
    const x = d3.scaleLinear()
        .domain([d3.min(data, (d) => d.x), d3.max(data, (d) => d.x)]) // Domain sumbu X
        .range([0, innerWidth])
        .nice(); // Menyesuaikan domain agar lebih rapi

    const y = d3.scaleLinear()
        .domain([d3.min(data, (d) => d.y), d3.max(data, (d) => d.y)]) // Domain sumbu Y
        .range([innerHeight, 0])
        .nice(); // Menyesuaikan domain agar lebih rapi

    // Warna untuk setiap cluster
    // const colors = d3.scaleOrdinal(d3.schemeCategory10);
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("pointer-events", "none");  

    // SVG container
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Clip path untuk membatasi area plot
    svg.append("defs")
        .append("clipPath")
        .attr("id", "plot-area")
        .append("rect")
        .attr("width", innerWidth)
        .attr("height", innerHeight);

    // Gambar lingkaran untuk setiap cluster
    clusterCenters.forEach((center, i) => {
        // Radius kecil (misalnya 20 piksel)
        const radius = 50;

        // Gambar lingkaran
        svg.append("circle")
            .attr("cx", x(center.x)) // Pusat X
            .attr("cy", y(center.y)) // Pusat Y
            .attr("r", radius) // Radius kecil
            .attr("fill", colors[i])
            .attr("opacity", 0.2) // Transparansi
            .attr("stroke", colors[i])
            .attr("stroke-width", 2);
    });

    // Gambar titik-titik data
    svg.selectAll(".point")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "point")
        .attr("cx", (d) => x(d.x)) // Posisi X
        .attr("cy", (d) => y(d.y)) // Posisi Y
        .attr("r", 5) // Radius titik
        .attr("fill", (d) => colors[d.cluster]) // Warna berdasarkan cluster
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("clip-path", "url(#plot-area)")
        .on("mouseover", (event, d) => {
            // Tampilkan tooltip
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
            tooltip.html(`Cluster: ${d.cluster}<br>Nama: ${d.name}<br> X : ${d.x} <br> Y : ${d.y}`)
                .style("left", `${event.pageX + 5}px`)
                .style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", () => {
            // Sembunyikan tooltip
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }); // Batasi titik data dalam area plot

    // Sumbu X
    svg.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .append("text")
        .attr("x", innerWidth / 2)
        .attr("y", 40)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text("X Axis");

    // Sumbu Y
    svg.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -innerHeight / 2)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text("Y Axis");

    // Judul chart
    svg.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .text("K-Means Clustering Result");
}


//silhoutte plot
function createSilhouettePlot(containerId, silhouetteScores, clusterLabels, width = 800, height = 450) {
    const margin = { top: 50, right: 150, bottom: 50, left: 50 }; // Margin kanan diperbesar untuk label
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Skala dan sumbu
    const x = d3.scaleLinear()
        .domain([-1, 1]) // Rentang nilai silhouette
        .range([0, innerWidth]);

    const y = d3.scaleBand()
        .domain(clusterLabels) // Label cluster
        .range([0, innerHeight])
        .padding(0.1);

    // Warna untuk setiap cluster
    // const colors = d3.scaleOrdinal(d3.schemeCategory10);

    // SVG container
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("pointer-events", "none");  



    // Gambar bar untuk setiap cluster
    silhouetteScores.forEach((scores, clusterIndex) => {
        // Hitung posisi Y untuk setiap cluster
        const clusterY = y(clusterLabels[clusterIndex]);

        // Gambar bar untuk setiap titik data dalam cluster
        svg.selectAll(`.bar-cluster-${clusterIndex}`)
            .data(scores)
            .enter()
            .append("rect")
            .attr("class", `bar-cluster-${clusterIndex}`)
            .attr("x", (d) => x(Math.min(0, d))) // Posisi X (mulai dari 0 atau nilai negatif)
            .attr("y", (d, i) => clusterY + (i * (y.bandwidth() / scores.length))) // Posisi Y
            .attr("width", (d) => Math.abs(x(d) - x(0))) // Lebar bar
            .attr("height", y.bandwidth() / scores.length - 1) // Tinggi bar
            .attr("fill", colors[clusterIndex]) // Warna cluster
            .attr("opacity", 0.7)// Transparansi
            .on("mouseover", (event, d) => {
                // Tampilkan tooltip
                tooltip.transition()
                    .duration(200)
                    .style("opacity", 0.9);
                tooltip.html(`Score : ${d}`)
                    .style("left", `${event.pageX + 5}px`)
                    .style("top", `${event.pageY - 28}px`);
            })
            .on("mouseout", () => {
                // Sembunyikan tooltip
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            }); // tooltip
             
    });

    // Garis vertikal di x = 0
    svg.append("line")
        .attr("x1", x(0))
        .attr("x2", x(0))
        .attr("y1", 0)
        .attr("y2", innerHeight)
        .attr("stroke", "black")
        .attr("stroke-width", 1);

    // Sumbu X (horizontal)
    svg.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .append("text")
        .attr("x", innerWidth / 2)
        .attr("y", 40)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text("Silhouette Score");

    // Sumbu Y (vertikal) di sebelah kanan
    svg.append("g")
        .attr("transform", `translate(${innerWidth},0)`)
        .call(d3.axisRight(y)) // Sumbu Y di sebelah kanan
        .selectAll("text")
        .attr("font-size", "15px")
        .attr("text-anchor", "start") // Label vertikal
        .attr("dx", "0.5em"); // Jarak dari sumbu

    // Judul chart
    svg.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .attr("font-size", "20px")
        .attr("font-weight", "bold")
        .text("Silhouette Plot");
}

// horizontal bar chart
function createTopScoreBarChart(containerId, data, width = 800, height = 500) {
    // Set margin
    const margin = {top: 40, right: 150, bottom: 60, left: 100};
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const values = data.values ;

    
     // 2. Ubah array numbers menjadi array objects 
    // (karena bar chart biasanya butuh label + value)
    const chartData = values.map((values, index) => ({
        labels: data.labels[index],
        values: values
    }));
    
    // 3. Urutkan
    const sortedData = [...chartData].sort((a, b) => b.score - a.score);

    // Create SVG
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales
    const x = d3.scaleLinear()
        .domain([0, d3.max(sortedData, d => d.values )]) // Handle jika score tidak ada
        .range([0, innerWidth]);

    const y = d3.scaleBand()
        .domain(sortedData.map(d => d.labels )) // Handle jika name tidak ada
        .range([0, innerHeight])
        .padding(0.3);

    // Add bars
    svg.selectAll(".bar")
        .data(sortedData)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("y", (d) => y(d.labels))
        .attr("width", (d) => x(d.values))
        .attr("height", y.bandwidth())
        .attr("fill", (d, i) => colors[i % 3])
        

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .append("text")
        .attr("x", innerWidth / 2)
        .attr("y", 35)
        .attr("text-anchor", "middle")
        .text("Skor Try Out")
        .style("font-size", "15px")
        ;

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .attr("dx", "-0.5em")
        .attr("dy", "0.15em")
        .style("text-anchor", "end")
        .style("font-size", "15px") // Ukuran font
        ;

    // Add title
    svg.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Top nilai nol terbanyak");
    
    svg.selectAll(".bar-label")
        .data(sortedData)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", (d) => x(d.values) + 5) // Posisi horizontal di tengah bar
        .attr("y", (d) => y(d.labels) + y.bandwidth() / 2) // Posisi vertikal di tengah bar
        .attr("dy", "0.35em") // Penyesuaian vertikal
        .attr("text-anchor", "start") // Teks di tengah
        .text((d) => d.values); // Menampilkan nilai

  
}

export { createBarChart, createPieChart, createBoxPlot, createElbowMethodChart, createScatterPlot,createSilhouettePlot,createTopScoreBarChart};