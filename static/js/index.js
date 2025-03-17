const urls = [bar_chart_previw_data]

Promise.all(urls.map(url => fetch(url).then(response => response.json()))).then(run);

function run(data){
    barChart(data[0]);
}

