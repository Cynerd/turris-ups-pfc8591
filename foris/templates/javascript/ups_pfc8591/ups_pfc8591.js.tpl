function graph_init(field) {
	var graph_config = {
		type: 'line',
		data: {
			labels: graph_labels[field],
			datasets: [
				{
					label: field,
					data: graph_data[field],
				},
			],
			fill: false,
			steppedLine: false,
		},
		options: {
			responsive: true,
			title: {
				display:true,
				text:'{{ trans("Sample") }}'
			},
			tooltips: {
				mode: 'index',
				intersect: false,
			},
			hover: {
				mode: 'nearest',
				intersect: true
			},
			scales: {
				xAxes: [{
					display: true,
					scaleLabel: {
						display: true,
						labelString: '{{ trans("Time") }}'
					}
				}],
				yAxes: [{
					display: true,
					scaleLabel: {
						display: true,
						labelString: '{{ trans("Value") }}'
					}
				}],
			},
		},
	};
	if (field == "voltage") {
		graph_config.options.scales.yAxes[0].ticks = { min: 10, max: 15 }
	} else if (field == "light" || field == "temperature") {
		graph_config.options.scales.yAxes[0].ticks = { min: 0, max: 250 }
	} else if (field == "light" || field == "temperature") {
		graph_config.options.scales.yAxes[0].ticks = { min: 0, max: 100 }
	}
	var graph_ctx = document.getElementById("canvas-" + field).getContext("2d");
	Foris.lineChart[field] = new Chart(graph_ctx, graph_config);
	Foris.lineChartData[field] = graph_config.data;
}

$(document).ready(function() {
	Foris.lineChart = [];
	Foris.lineChartData = [];
	graph_init("voltage");
	graph_init("light");
	graph_init("temperature");
	graph_init("trimmer");
});

/*
Foris.WS["ups-pfc8591"] = function (data) {
	for (d in data) {
		Foris.lineChartData[d].datasets[0].data.push(data[d][0]);
		Foris.lineChartData[d].datasets[0].data.shift();
		Foris.lineChartData[d].labels.push(data[d][1]);
		Foris.lineChartData[d].labels.shift();
		Foris.lineChart[d].update();
	}
};
*/
