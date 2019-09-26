/* 
*  Copyright 2019 Altran. All rights reserved.
* 
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
* 
*      http://www.apache.org/licenses/LICENSE-2.0
* 
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
* 
*/
// ************** Generate the tree diagram	 *****************
function update(source) {
	$('.evaMap').empty();
	var margin = { top: 20, right: 120, bottom: 20, left: 250 },
		width = 1200 - margin.right - margin.left,
		height = 500 - margin.top - margin.bottom;

	var i = 0;

	var tree = d3.layout.tree()
		.size([height, width]);

	var diagonal = d3.svg.diagonal()
		.projection(function (d) { return [d.y, d.x]; });

	var svg = d3.select("div.evaMap").append("svg")	// .attr("width", width + margin.right + margin.left)
		.attr("width", '100%')
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + (margin.left - 80) + "," + margin.top + ")");
	// Compute the new tree layout.
	var nodes = tree.nodes(root).reverse(),
		links = tree.links(nodes);

	// Normalize for fixed-depth.
	nodes.forEach(function (d) { d.y = d.depth * 180; });

	// Declare the nodes…
	var node = svg.selectAll("g.node")
		.data(nodes, function (d) { return d.id || (d.id = ++i); });

	// Enter the nodes.
	var nodeEnter = node.enter().append("g")
		//  .attr("class", "node")
		.attr("transform", function (d) {
			return "translate(" + d.y + "," + d.x + ")";
		})
		.attr('class', function (d) {
			if (d.nodeType == 'Auditors') {
				return 'auditorClass node';
			}
		});

	nodeEnter.append("circle")
		.attr("r", "14") //function (d) { return d.value; })
		.style("stroke", function (d) { return d.type; })
		.style("fill", function (d) { return d.type; });
	nodeEnter.append("text")
		.attr("x", function (d) {
			return d.children || d._children ?
				(d.value + 4) * -1 : d.value + 4
		})
		.attr("y", function (d) {
			return d.children || d._children ?
				(d.value + 15) : d.value + 15
		})
		.attr('width', '200')
		.attr('class', 'wrapme')
		.attr("dy", "0em")
		.attr("text-anchor", "middle")
		.text(function (d) { return d.name; })
		.style({ "fill-opacity": "1", "fill": "#247a49", "font": "italic 14px serif", "font-weight": "bolder" });

	svg.selectAll('g.auditorClass').append("image")
		.attr("xlink:href", '/static/assets/images/document_magnify-512.png')
		.attr("width", 30)
		.attr("height", 22)
		.attr("x", -13)
		.attr("y", -13)
		.style('cursor', 'pointer');

	// Declare the links…
	var link = svg.selectAll("path.link")
		.data(links, function (d) { return d.target.id; });

	// Enter the links.
	link.enter().insert("path", "g")
		.attr("class", "link")
		.style("stroke", function (d) { return d.target.level; })
		.attr("d", diagonal);
	d3.selectAll('.wrapme').call(wrap);
	$('.wrapme > tspan').css({ "fill-opacity": "1", "fill": "#247a49", "font": "italic 14px serif", "font-weight": "bolder" });
}

/* for wrapping the graph text */
function wrap(text) {
	text.each(function () {
		var text = d3.select(this);
		var words = text.text().split(/\s+/).reverse();
		var lineHeight = 15;
		var width = parseFloat(text.attr('width'));
		var y = parseFloat(text.attr('y'));
		var x = text.attr('x');
		var anchor = text.attr('text-anchor');

		var tspan = text.text(null).append('tspan').attr('x', x).attr('y', y).attr('text-anchor', anchor);
		var lineNumber = 0;
		var line = [];
		var word = words.pop();

		while (word) {
			line.push(word);
			tspan.text(line.join(' '));
			if (tspan.node().getComputedTextLength() > width) {
				lineNumber += 1;
				line.pop();
				tspan.text(line.join(' '));
				line = [word];
				tspan = text.append('tspan').attr('x', x).attr('y', y + lineNumber * lineHeight).attr('anchor', anchor).text(word);
			}
			word = words.pop();
		}
	});

}

function gaugeFormation() {
	var opts = {
		angle: 0.02,
		lineWidth: 0.20,// The line thickness
		radiusScale: 1,
		pointer: {
			length: 0.5,
			strokeWidth: 0.035,
			color: '#000000'
		},
		limitMax: 'false',  // !!!!
		strokeColor: '#E0E0E0',
		generateGradient: true,
		highDpiSupport: true,
		staticZones: [
			{ strokeStyle: "rgb(144,238,144)", min: 0, max: 350, height: 1.2 },
			{ strokeStyle: "rgb(255,165,0)", min: 350, max: 650, height: 1.2 },
			{ strokeStyle: "rgb(255,69,0)", min: 650, max: 1000, height: 1.2 }
			// {strokeStyle: "rgb(150,250,0)", min: 750, max: 1000, height: 1.2}
		],
		staticLabels: {
			font: "12px sans-serif",  // Specifies font
			labels: [0, 350, 650, 1000],  // Print labels at these values
			color: "#000000",  // Optional: Label text color
			fractionDigits: 0  // Optional: Numerical precision. 0=round off.
		}
	};
	var target = document.getElementById('foo');
	var gauge = new Gauge(target).setOptions(opts);
	gauge.maxValue = 1000;
	gauge.setMinValue(0);
	gauge.animationSpeed = 32;
	gauge.set(150);

	var target1 = document.getElementById('foo1');
	var gauge1 = new Gauge(target1).setOptions(opts);
	gauge1.maxValue = 1000;
	gauge1.setMinValue(0);
	gauge1.animationSpeed = 32;
	gauge1.set(150);
}

function pieChartFormation() {
	/* pie chart*/
	var oilCanvas = document.getElementById("oilChart");
	var oilCanvas1 = document.getElementById("oilChartEve");
	Chart.defaults.global.defaultFontSize = 12;

	var oilData = {
		labels: [
			"Container Cluster Policies",
			"Network Security Policies",
			"Monitoring"
		],
		datasets: [
			{
				data: [200, 444, 500],
				backgroundColor: [
					"#97CD7A",
					"#39A7F0",
					"#29CBA9"
				]
			}]
	};
	var pieChart = new Chart(oilCanvas, {
		type: 'doughnut',
		data: oilData,
		options: {
			legend:{
				display: false
			}
		}
	});

	var pieChart1 = new Chart(oilCanvas1, {
		type: 'doughnut',
		data: oilData,
		options: {
			legend:{
				display: false
			}
		}
	});
}

//Line Chart
function initLineCharts() {
	var ctx = document.getElementById("lineChart");
	var ctx2 = document.getElementById("lineChart1");
	var dataObj = {
		labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"],
		datasets: [{
			label: 'Trends',
			backgroundColor: "rgba(38, 185, 154, 0.31)",
			borderColor: "rgba(38, 185, 154, 0.7)",
			pointBorderColor: "rgba(38, 185, 154, 0.7)",
			pointBackgroundColor: "rgba(38, 185, 154, 0.7)",
			pointHoverBackgroundColor: "#fff",
			pointHoverBorderColor: "rgba(220,220,220,1)",
			pointBorderWidth: 1,
			data: [250, 600, 150, 130, 80, 200, 100, 90, 300, 150]
		}]
	};

	var option = {
		responsive: true,
		maintainAspectRatio: false,
		legend: {
			display: false
		}
	};
	var lineChart = new Chart(ctx, {
		type: 'line',
		data: dataObj,
		options: option
	});
	var lineChart1 = new Chart(ctx2, {
		type: 'line',
		data: dataObj,
		options: option
	});
}

$(document).ready(function () {
	initLineCharts();
	gaugeFormation();
	pieChartFormation();

	$(document).on('click', 'g.auditorClass > image', function () {
		$(this).parent().removeClass('auditorClass').addClass('processing');
		$(this).remove();
		svg.selectAll('g.processing').append("image")
			.attr("xlink:href", '/static/assets/images/ThoughtfulEvergreenAddax.gif')
			.attr("width", 20)
			.attr("height", 20)
			.attr("x", -10)
			.attr("y", -10)
	});
});

