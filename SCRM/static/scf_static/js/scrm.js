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
	$('.headingTwo,.headingThree').hide();

	$(document).on('click', '.headStart > div', function () {
		var divID = $(this).attr('data-href');
		if (divID == 'headingTwo') {
			jQuery('#vmap').vectorMap(
				{
					map: 'world_en',
					backgroundColor: 'transparent',
					borderColor: '#818181',
					borderOpacity: 0.50,
					borderWidth: 1,
					color: '#ffffff',
					enableZoom: true,
					hoverColor: '#149b7e',
					hoverOpacity: null,
					normalizeFunction: 'linear',
					scaleColors: ['#b6d6ff', '#005ace'],
					selectedColor: '#149b7e',
					selectedRegions: ['VA','OH','CA','OR','IN'],
					showTooltip: true,
					multiSelectRegion: false 
				});
		}
	})
});