// function createChart(elementId, title) {
//     var options = {
//         series: [{
//             data: []
//         }],
//         chart: {
//             id: elementId,
//             height: 250,
//             type: 'area',
//             animations: {
//                 enabled: false,
//                 easing: 'linear',
//                 dynamicAnimation: {
//                     speed: 10
//                 }
//             },
//             toolbar: {
//                 show: false
//             },
//             zoom: {
//                 enabled: false
//             },
//         },
//         dataLabels: {
//             enabled: false
//         },
//         stroke: {
//             curve: 'smooth'
//         },
//         title: {
//             text: title,
//             align: 'left'
//         },
//         markers: {
//             size: 0
//         },
//         xaxis: {
//             type: 'datetime',
//             range: 300000, // 5 minutes
//         },
//         yaxis: {
//             max: 100
//         },
//         legend: {
//             show: false
//         },
//     };

//     return new ApexCharts(document.querySelector("#" + elementId), options);
// }

// document.addEventListener("DOMContentLoaded", function () {
//     if (window.ApexCharts) {
//         var cpuChart = createChart("cpu_usage_chart", "CPU Usage");
//         var ramChart = createChart("ram_usage_chart", "RAM Usage");
//         var storageChart = createChart("disk_usage_chart", "Storage Usage");

//         cpuChart.render();
//         ramChart.render();
//         storageChart.render();


//         function updateCharts() {
//             fetch(system_statistics_url)
//                 .then(response => response.json())
//                 .then(data => {
//                     cpuChart.updateSeries([{ data: data.cpu }]);
//                     ramChart.updateSeries([{ data: data.ram }]);
//                     storageChart.updateSeries([{ data: data.storage }]);
//                 });
//         }

//         // Update charts every 5 seconds
//         setInterval(updateCharts, 1000);
//         // Initial update
//         updateCharts();
//     }
// });

// console.log("system_statistics_url", system_statistics_url);












function createCombinedChart(elementId, title) {
    var options = {
        series: [
            { name: 'CPU', data: [] },
            { name: 'RAM', data: [] },
            { name: 'Storage', data: [] }
        ],
        chart: {
            id: elementId,
            height: 330,
            type: 'area',
            animations: {
                enabled: false,
                easing: 'linear',
                dynamicAnimation: {
                    speed: 10
                }
            },
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth'
        },
        title: {
            // text: title,
            align: 'left'
        },
        markers: {
            size: 0
        },
        xaxis: {
            type: 'datetime',
            range: 300000, // 5 minutes
            title: {
                text: "",
                style: {
                  color: 'var(--tblr-body-color)'
                }
            },
            labels: {
                style: {
                  colors: 'var(--tblr-body-color)',
                }
            },
        },
        yaxis: {
            max: 100,
            min: 0,
            title: {
                text: "Percent",
                style: {
                    fontSize: '14px',
                    fontFamily: 'var(--tblr-font-sans-serif)',
                    color: 'var(--tblr-body-color)'
                }
            },
            labels: {
                style: {
                  colors: 'var(--tblr-body-color)',
                }
            },
        },
        legend: {
            show: true,
            fontSize: '14px',
            fontFamily: 'var(--tblr-font-sans-serif)',
            labels: {
                colors: 'var(--tblr-body-color)',
            },
        },
    };

    return new ApexCharts(document.querySelector("#" + elementId), options);
}

document.addEventListener("DOMContentLoaded", function () {
    if (window.ApexCharts) {
        var combinedChart = createCombinedChart("combined_usage_chart", "System Resource Usage");
        combinedChart.render();

        function updateChart() {
            fetch(system_statistics_url)
                .then(response => response.json())
                .then(data => {
                    combinedChart.updateSeries([
                        { name: 'CPU', data: data.cpu },
                        { name: 'RAM', data: data.ram },
                        { name: 'Storage', data: data.storage }
                    ]);
                });
        }

        // Update chart every 5 seconds
        setInterval(updateChart, 2000);
        // Initial update
        updateChart();
    }
});

console.log("system_statistics_url", system_statistics_url);