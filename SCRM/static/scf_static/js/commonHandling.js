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