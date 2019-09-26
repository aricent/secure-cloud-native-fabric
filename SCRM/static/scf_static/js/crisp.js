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
$(document).ready(function () {
	setTimeout(function () {
		$('.alarmEvents,.sunburstView').hide();
	}, 1000);
});

const width = window.innerWidth,
	height = window.innerHeight,
	maxRadius = (Math.min(width, height) / 2) - 5;

const formatNumber = d3.format(',d');

const x = d3.scaleLinear()
	.range([0, 2 * Math.PI])
	.clamp(true);

const y = d3.scaleSqrt()
	.range([maxRadius * .1, maxRadius]);

const color = d3.scaleOrdinal(d3.schemeCategory20);

const partition = d3.partition();

const arc = d3.arc()
	.startAngle(d => x(d.x0))
	.endAngle(d => x(d.x1))
	.innerRadius(d => Math.max(0, y(d.y0)))
	.outerRadius(d => Math.max(0, y(d.y1)));

const middleArcLine = d => {
	const halfPi = Math.PI / 2;
	const angles = [x(d.x0) - halfPi, x(d.x1) - halfPi];
	const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);

	const middleAngle = (angles[1] + angles[0]) / 2;
	const invertDirection = middleAngle > 0 && middleAngle < Math.PI; // On lower quadrants write text ccw
	if (invertDirection) { angles.reverse(); }

	const path = d3.path();
	path.arc(0, 0, r, angles[0], angles[1], invertDirection);
	return path.toString();
};

const textFits = d => {
	const CHAR_SPACE = 6;

	const deltaAngle = x(d.x1) - x(d.x0);
	const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);
	const perimeter = r * deltaAngle;

	return d.data.name.length * CHAR_SPACE < perimeter;
};

const svg = d3.select('.sunburstCrisp').append('svg')
	.style('width', 'calc(100vw - 40%)')
	.style('height', 'calc(100vh - 30%)')
	.attr('viewBox', `${-width / 2} ${-height / 2} ${width} ${height}`)
	.on('click', () => focusOn()); // Reset zoom on canvas click

d3.json('/static/json/sunburst.json', (error, root) => {
	if (error) throw error;

	root = d3.hierarchy(root);
	root.sum(d => d.size);

	const slice = svg.selectAll('g.slice')
		.data(partition(root).descendants());

	slice.exit().remove();

	const newSlice = slice.enter()
		.append('g').attr('class', 'slice')
		.on('click', d => {
			d3.event.stopPropagation();
			focusOn(d);
		});

	newSlice.append('title')
		.text(d => d.data.name + '\n' + formatNumber(d.value));

	newSlice.append('path')
		.attr('class', 'main-arc')
		.style('fill', d => color(d.data.color))
		.attr('d', arc);

	newSlice.append('path')
		.attr('class', 'hidden-arc')
		.attr('id', (_, i) => `hiddenArc${i}`)
		.attr('d', middleArcLine);

	const text = newSlice.append('text')
		.attr('display', d => textFits(d) ? null : 'none');

	text.append('textPath')
		.attr('startOffset', '50%')
		.attr('xlink:href', (_, i) => `#hiddenArc${i}`)
		.text(d => { return d.data.name + ' - ' + d.data.score });
});

function focusOn(d = { x0: 0, x1: 1, y0: 0, y1: 1 }) {
	// Reset to top-level if no data point specified

	const transition = svg.transition()
		.duration(750)
		.tween('scale', () => {
			const xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
				yd = d3.interpolate(y.domain(), [d.y0, 1]);
			return t => { x.domain(xd(t)); y.domain(yd(t)); };
		});

	transition.selectAll('path.main-arc').attrTween('d', d => () => arc(d));
	transition.selectAll('path.hidden-arc').attrTween('d', d => () => middleArcLine(d));
	transition.selectAll('text').attrTween('display', d => () => textFits(d) ? null : 'none');
	moveStackToFront(d);

	function moveStackToFront(elD) {
		svg.selectAll('.slice').filter(d => d === elD)
			.each(function (d) {
				this.parentNode.appendChild(this);
				if (d.parent) { moveStackToFront(d.parent); }
			})
	}
}