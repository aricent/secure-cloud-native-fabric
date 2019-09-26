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
	populatePostures();
	$('.postureList').on('change', function () {
		if ($(this).hasClass('evaListPosture')) {
			changeEvaPosture('map');
		}
		else if ($(this).hasClass('crispAuditGraph')) {
			calNeo4jGraph('KUBERNETES','#neo4jd3');
			$('.postureName > strong').text($(this).val());
		}
		else if ($(this).hasClass('compliancePage')) {
			changeEvaPosture('graph');
		}
	});
	setTimeout(function () {
		if ($('.postureList').hasClass('evaListPosture')) {
			changeEvaPosture('map');
		}
		else if ($('.postureList').hasClass('compliancePage')) {
			changeEvaPosture('graph');
		}
		$('#operator_title').val('').prop('readonly', true);
		$('.postureName > strong').text($('.postureList').val());
	}, 1000);

});

function populatePostures() {
	$.ajax({
		url: '/policypostures/?postureNames=true&orgname=Aricent',
		type: 'GET',
		cache: false,
		success: function (data) {
			if (typeof data[0] == 'object') {
				var htmlStr = '<option value="">No postures</option>';
			}
			else {
				//	var data = data.sort();
				var htmlStr = '';
				$.each(data, function (k, val) {
					htmlStr += '<option value="' + val + '">' + val + '</option>';
				});
			}
			$('.postureList').empty().append(htmlStr);
		},
		error: function (xhr) {

		}
	});
}

function changeEvaPosture(viewType) {
	$('#operator_title').val('').prop('readonly', true);
	var selPost = $('.postureList option:selected').val();
	//console.log('viewType  ' + viewType);
	//if (selPost == '' || typeof selPost == 'undefined') {
	$.ajax({
		url: '/policyposturemaps/?posturename=' + selPost + '&orgname=Aricent',
		type: 'GET',
		cache: false,
		success: function (data) {
			if (viewType == 'map') {
				var operators = [];
				var complianceArray = [];
				$.each(data.operators, function (key, value) {
					var operator = {};
					operator.id = key;
					operator.name = value.properties.title;
					operator.parent = null;
					operator.children = null;
					operator.type = "#ccc"; // node color
					operator.level = "#ccc"; // path color
					operator.value = 14;
					operator.nodeType = value.nodeType;
					operators.push(operator);
				});

				if (operators.length > 0) {
					$.each(operators, function (operatorKey, operatorValue) {
						$.each(data.links, function (linkKey, linkValue) {
							if (linkValue.fromOperator == operatorValue.id) {
								if (operatorValue.children == null) {
									operatorValue.children = [];
								}
								var childOp = getOperatorForId(linkValue.toOperator, operators);
								childOp.parent = operatorValue.name;
								operatorValue.children.push(childOp);
							}
						});
					});
					var lengthOp = operators.length - 1; // always be the last element of the array
					complianceArray.push(operators[lengthOp]);
					//console.log('Final EVA map ' + JSON.stringify(complianceArray));
					root = complianceArray[0];
					update(root);  // form EVA mapping
				}
			}
			else {
				$('.postNameSel').text(selPost);
				$("#tabs-3").flowchart("setData", data);
			}
		},
		error: function (xhr) {

		}
	});
	//}

}

function getOperatorForId(id, operators) {
	var selected;
	$.each(operators, function (opKey, opValue) {
		if (opValue.id == id) {
			selected = opValue;
			return false;
		}
	});
	return selected;
}
