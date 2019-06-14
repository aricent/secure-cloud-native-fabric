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