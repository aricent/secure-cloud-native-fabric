$(document).ready(function () {
	$('#sidebar-menu ul a').on('click', function () {
		if ((typeof timeClearSet != 'undefined') && (typeof setTimerInter != 'undefined')) {
			clearInterval(setTimerInter);
			clearInterval(timeClearSet);
		}
		sessionStorage.setItem('activeLink', $(this).attr('href'));
	});

	/*handling tabs */
	$(document).on('click', '.headTxt', function () {
		$('.headTxt').removeClass('active');
		$(this).addClass('active');
		var path = $(this).parent().attr('data-href');
		$('.nodeDiv').hide();
		$('.' + path).show();
	});
});

window.onload = function () {
	var hrefLink = sessionStorage.getItem('activeLink') == null ? '#!/scrm/dashboard' : sessionStorage.getItem('activeLink');
	setTimeout(function () {
		$('.subMenuItem').each(function (k, val) {
			if ($(this).attr('href') == $.trim(hrefLink)) {
				$(this).parent('li').addClass('active');
			}
		});
	}, 1000);

}