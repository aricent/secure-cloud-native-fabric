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
var dataID = '';
var finalObj = [];
var comp_array = [];
var itemsMainDiv = ('.MultiCarousel');
var itemsDiv = ('.MultiCarousel-inner');
var itemWidth = "";

$(document).ready(function () {
	// loadComponentTree();
	createBlueprint('');
	$(".tabsDiv").tabs();

	// page scrolling handler 
	$('.panelBox').on('click', function (e) {
		$('.panelBox').removeClass('active');
		$(this).addClass('active');
		var id = '#' + $(this).attr('data-set');
		var ind = $(id).index();
		$("#goalsCarousel").carousel(ind);
		if (id == '#step-1') {
			populateBaseline();
		}
		else if (id == '#step-2') {
			$('input.postureName').show().val('');
			$('span.postureName').text('').hide();
			$("#tabs-3").flowchart("setData", {});
			$('.deleteBase,#step-2 .addBase').attr('disabled', true);
			loadComponentTree();
		}
		else if (id == '#step-3') {
			populateBaseline();
			populateCloudList();
			$('.applyStepsDiv,.backBtn').hide();
			$('#selCloudDiv').show();
			$('.stepProgress-item').removeClass('current');
			$('.stepProgress-item[data-page="selCloud"]').addClass('current');
		}
	});

	$('.nextBtn').on('click', function () {
		if ($('li[data-page="selCloud"]').hasClass('current')) {
			if ($('#cloudName').val() == '') {
				$('#cloudName').focus();
			}
			else {
				nextAction();
			}
		}
		else {
			nextAction();
		}
	});

	// add new baseline
	$('.addBase').on('click', function (e) {
		$("#goalsCarousel").carousel(1);
		$('.panelBox').removeClass('active');
		$('.panelBox').eq(1).addClass('active');
		$('input.postureName').show().val('');
		$('span.postureName').text('').hide();
		$("#tabs-3").flowchart("setData", {});
		$('.deleteBase,#step-2 .addBase').attr('disabled', true);
		loadComponentTree();
	});

	// edit saved baseline
	$('.editBase').on('click', function (e) {
		var txt = $('#step-1 .MultiCarousel-inner .item.selected').text().trim();
		$("#goalsCarousel").carousel(1);
		$('.panelBox').removeClass('active');
		$('.panelBox').eq(1).addClass('active');
		populateSaveBaseline(txt, 'design');
		$('input.postureName').hide().val(txt);
		$('span.postureName').text(txt).show();
		$('.deleteBase,#step-2 .addBase').attr('disabled', false);
		loadComponentTree();
		setTimeout(function () {
			$('.flowchart-operator').append('<button type="button" class="close cancelNode" aria-hidden="true">×</button>');
		}, 500);
	})

	// save new baseline
	$('#save_button').click(function () {
		if ($('.postureName').val() != '') {
			saveFlowChart();
		}
		else if (Object.keys($("#tabs-3").flowchart("getData")['operators']).length == 0) {
			// bootbox.alert({
			// 	message: '<img class="boot-img" src="../static/scf_static/images/error_img.png" /><p class="boot-para">Please define the baseline.</p>',
			// 	size: 'small'
			// });
			swal({
				title: "",
				text: "Please define the baseline.",
				icon: "error",
				button: "Ok",
			});
		}
		else {
			$('.postureName').focus();
		}
	});

	$('#search').keyup(function () {
		$('#ajaxTree').jstree('search', $(this).val());
	});

	// components tray handling 
	$('.editList').on('click', function (e) {
		initJsTree(finalObj);
	});

	$(document).on('click', '.addNewNode', function (e) {
		e.stopPropagation();
		demo_create();
	});

	$(document).on('click', '.renNode', function (e) {
		e.stopPropagation();
		demo_rename();
	});

	$(document).on('click', '.deleteNode', function (e) {
		e.stopPropagation();
		demo_delete();
	});

	$('#searchCat').keyup(function () {
		$('#ajaxTreeCrud').jstree('search', $(this).val());
	});
	/* tray handling ends */

	// Delete the particular node
	$(document).on('click', '.cancelNode', function (e) {
		$('#tabs-3').flowchart('deleteOperator', dataID);
		var data = $('#tabs-3').flowchart('getData');
		$('#src_code').val(JSON.stringify(data, null, 2));
	});

	populateBaseline();

	$(document).on('click', '#step-1 .MultiCarousel-inner .item', function (e) {
		$('#step-1 .MultiCarousel-inner .item').removeClass('selected');
		$(this).addClass('selected');
		var txtBase = $(this).text().trim();
		if (txtBase != 'No baselines available') {
			populateSaveBaseline(txtBase, 'view');
		}
	});

	$(document).on('click', '#step-3 .MultiCarousel-inner .item', function (e) {
		$('#step-3 .MultiCarousel-inner .item').removeClass('selected');
		$(this).addClass('selected');
	});

	$('.createPolicy').on('click', createPolicyInstance);

	$('.backBtn').on('click', backAction);

	$('#goalsCarousel').carousel({
		interval: false
	});

	$('.leftLst, .rightLst').click(function () {
		var condition = $(this).hasClass("leftLst");
		if (condition)
			click(0, this);
		else
			click(1, this)
	});

	ResCarouselSize();

	$(window).resize(function () {
		ResCarouselSize();
	});
});

//this function define the size of the items
function ResCarouselSize() {
	var incno = 0;
	var dataItems = ("data-items");
	var itemClass = ('.item');
	var id = 0;
	var btnParentSb = '';
	var itemsSplit = '';
	var sampwidth = $(itemsMainDiv).width();
	var bodyWidth = $('body').width();
	$(itemsDiv).each(function () {
		id = id + 1;
		var itemNumbers = $(this).find(itemClass).length;
		btnParentSb = $(this).parent().attr(dataItems);
		itemsSplit = btnParentSb.split(',');
		$(this).parent().attr("id", "MultiCarousel" + id);


		if (bodyWidth >= 1200) {
			incno = itemsSplit[3];
			itemWidth = sampwidth / incno;
		}
		else if (bodyWidth >= 992) {
			incno = itemsSplit[2];
			itemWidth = sampwidth / incno;
		}
		else if (bodyWidth >= 768) {
			incno = itemsSplit[1];
			itemWidth = sampwidth / incno;
		}
		else {
			incno = itemsSplit[0];
			itemWidth = sampwidth / incno;
		}
		$(this).css({ 'transform': 'translateX(0px)', 'width': itemWidth * itemNumbers });
		$(this).find(itemClass).each(function () {
			$(this).outerWidth(itemWidth);
		});

		$(".leftLst").addClass("over");
		$(".rightLst").removeClass("over");

	});
}

//this function used to move the items
function ResCarousel(e, el, s) {
	var leftBtn = ('.leftLst');
	var rightBtn = ('.rightLst');
	var translateXval = '';
	var divStyle = $(el + ' ' + itemsDiv).css('transform');
	var values = divStyle.match(/-?[\d\.]+/g);
	var xds = Math.abs(values[4]);
	if (e == 0) {
		translateXval = parseInt(xds) - parseInt(itemWidth * s);
		$(el + ' ' + rightBtn).removeClass("over");

		if (translateXval <= itemWidth / 2) {
			translateXval = 0;
			$(el + ' ' + leftBtn).addClass("over");
		}
	}
	else if (e == 1) {
		var itemsCondition = $(el).find(itemsDiv).width() - $(el).width();
		translateXval = parseInt(xds) + parseInt(itemWidth * s);
		$(el + ' ' + leftBtn).removeClass("over");

		if (translateXval >= itemsCondition - itemWidth / 2) {
			translateXval = itemsCondition;
			$(el + ' ' + rightBtn).addClass("over");
		}
	}
	$(el + ' ' + itemsDiv).css('transform', 'translateX(' + -translateXval + 'px)');
}

//It is used to get some elements from btn
function click(ell, ee) {
	var Parent = "#" + $(ee).parent().attr("id");
	var slide = $(Parent).attr("data-slide");
	ResCarousel(ell, Parent, slide);
}

function nextAction() {
	selectedNodesArr = [];
	$('.backBtn').show();
	var page = $('.stepProgress-item.current').next().attr('data-page');
	$('.applyStepsDiv').hide();
	$('#' + page + 'Div').show();
	$('.stepProgress-item').removeClass('current');
	$('.stepProgress-item[data-page="' + page + '"]').addClass('current');
	if (page == 'auditorTemp') {
		$('.nextBtn').hide();
		calNeo4jGraph('KUBERNETES', '#neo4jd3');
		setTimeout(function () {
			populateLabels();
		}, 2000);
	}
	else if (page == 'policyTemp') {
		calNeo4jGraph('KUBERNETES', '#policyNeo4jd3');
		setTimeout(function () {
			populateLabels();
		}, 2000);
	}
}

function backAction() {
	selectedNodesArr = [];
	$('.nextBtn').show();
	var page = $('.stepProgress-item.current').prev().attr('data-page');
	$('.applyStepsDiv').hide();
	$('#' + page + 'Div').show();
	$('.stepProgress-item').removeClass('current');
	$('.stepProgress-item[data-page="' + page + '"]').addClass('current');
	if (page == 'selCloud') {
		$('.backBtn').hide();
	}
	else if (page == 'auditorTemp') {
		calNeo4jGraph('KUBERNETES', '#neo4jd3');
		setTimeout(function () {
			populateLabels();
		}, 2000);
	}
	else if (page == 'policyTemp') {
		calNeo4jGraph('KUBERNETES', '#policyNeo4jd3');
		setTimeout(function () {
			populateLabels();
		}, 2000);
	}
}

function populateSaveBaseline(txtBase, displayPage) {
	$.ajax({
		url: '/policypostures/?posturename=' + txtBase + '&orgname=Aricent',
		type: 'GET',
		cache: false,
		success: function (data) {
			if (displayPage == 'design') {
				$("#tabs-3").flowchart("setData", data);
			}
			else {
				$("#tabs-1").flowchart("setData", data);
			}
		},
		error: function (xhr) {

		}
	});
}

function populateCloudList() {
	$.ajax({
		url: "/clouds/",
		type: 'GET',
		cache: false,
		async: false,
		success: function (data) {
			var optionHtml = "<option value=''>Please Select</option>";
			$.each(data, function (k, v) {
				optionHtml += '<option value="' + v.Id + '" data-cloudtype= "' + $.trim(v.CloudType) + '">' + v.CloudName + '</option>'
			});
			$('#cloudName').empty().html(optionHtml);
		},
		error: function () {

		}
	});
}

function populateBaseline() {
	$.ajax({
		url: '/policypostures/?postureNames=true&orgname=Aricent',
		type: 'GET',
		cache: false,
		success: function (data) {
			if (typeof data[0] == 'object') {
				var htmlStr = '<div class="item selected"><div class="pad15"><p class="lead">No baselines available</p></div></div>';
				$('.rightLst,.leftLst').hide();
				$('.editBase,.deleteBase').attr('disabled', true);
			}
			else {
				//	var data = data.sort();
				var htmlStr = '';
				$.each(data, function (k, val) {
					if (k == 0) {
						htmlStr += '<div class="item selected"><div class="pad15"><p class="lead">' + val + '</p></div></div>';
					}
					else {
						htmlStr += '<div class="item"><div class="pad15"><p class="lead">' + val + '</p></div></div>';
					}
				});
				$('.rightLst,.leftLst').show();
				$('.editBase,.deleteBase').attr('disabled', false)
			}
			$('.MultiCarousel-inner').empty().append(htmlStr);
			populateSaveBaseline($('#step-1 .MultiCarousel-inner .item.selected').text().trim(), 'view');
		},
		error: function (xhr) {

		}
	});

}

function createBlueprint(displayFlowChart) {
	$('#tabs-3,#tabs-1').flowchart({
		data: displayFlowChart,
		onOperatorSelect: function (operatorId) {
			var opData = $('#tabs-3').flowchart('getOperatorData', operatorId);
			dataID = opData.properties.dataId;
			return true;
		},
		linkWidth: 5,
		multipleLinksOnInput: true,
		multipleLinksOnOutput: true,
		defaultLinkColor: "#000"
	});
}

function saveFlowChart() {
	var postureName = $('.postureName').val().trim();
	var data = $('#tabs-3').flowchart('getData');
	$.ajax({
		url: '/policypostures/',
		type: 'POST',
		cache: false,
		contentType: 'application/json',
		data: JSON.stringify({ "posturename": postureName, "orgname": "Aricent", "jsondoc": data }),
		success: function (res) {
			// bootbox.alert({
			// 	'message': '<img class="boot-img" src="../static/scf_static/images/CheckMark.png" /><p class="boot-para">Goal Baseline has been saved successfully.</p>'
			// });
			swal({
				title: "",
				text: "Goal Baseline has been saved successfully.",
				icon: "success",
				button: "Ok",
			});
		},
		error: function (xhr) {

		}
	});
}

function loadComponentTree() {
	$.ajax({
		url: '/policypostures/?catalog=true&orgname=Aricent',
		type: 'GET',
		cache: false,
		datatype: 'json',
		success: function (response) {
			var childArr = [];
			finalObj = [];
			$.each(response, function (key, val) {
				if (val.sequence != undefined) {
					var ind = Number(val.sequence) - 1;
					finalObj[ind] = val;
				}
				else {
					childArr.push(val);
				}
			});
			$.merge(finalObj, childArr);
			$("#ajaxTree").jstree("destroy");
			$('#ajaxTree').jstree({
				'core': {
					"multiple": false,
					'themes': {
						'responsive': true
					},
					'data': finalObj
				},
				"types": {
					"default": {
						"icon": "fa fa-clone"
					},
					"root": {
						"icon": "fa fa-folder-open"
					},
					"level1": {
						"icon": "fa fa-shopping-basket"
					},
					"level2": {
						"icon": "fa fa-clone"
					}

				},
				"search": {
					"case_insensitive": true,
					"show_only_matches": true
				},
				"plugins": ["search", "types", "wholerow"]
			});

			$("#ajaxTree").bind("select_node.jstree", function (evt, ref_node) {
				ajaxTreeClicked(evt, ref_node.node);
			});

			$("#ajaxTree").bind("loaded.jstree", function (event, data) {
				$('#ajaxTree').jstree("open_node", "#topLevel");
			});
		},
		error: function (xhr) {

		}
	});
	$(".tabsDiv").tabs();
}

function demo_create() {
	var ref = $('#ajaxTreeCrud').jstree(true);
	var sel = ref.get_selected('full', true);
	if (!sel.length) { return false; }
	sel = sel[0].id;
	var nodeLen = $('#' + sel + '> ul > li').length + 1;
	var nodeType = $('#' + sel + '> a').text();
	if (sel == 'topLevel') {
		var type = "level1";
		var nodeID = 'node_' + nodeLen;
	}
	else {
		var type = "level2";
		var nodeID = 'node_' + sel + '.' + nodeLen;
	}
	sel = ref.create_node(sel, { "id": nodeID, "text": "New Node", "description": "New Node", "nodeType": nodeType, "type": type, "data": { "action": "new" } });
	ref.edit(sel);
}

function demo_rename() {
	var ref = $('#ajaxTreeCrud').jstree(true),
		sel = ref.get_selected('full', true);
	if (!sel.length) { return false; }
	if (sel[0].data.action == 'new') {
		sel[0].data.action = 'upd';
	}
	sel = sel[0];
	ref.edit(sel);
}

function demo_delete() {
	var ref = $('#ajaxTreeCrud').jstree(true),
		sel = ref.get_selected('full', true);
	if (!sel.length) { return false; }
	sel[0].data.action = 'del';
	sel = sel[0];
	ref.delete_node(sel);
}

var count = 0;
function ajaxTreeClicked(obj, node) {
	if (node.id.indexOf('.') != -1) {
		count++;
		var comp_id = node.id + '-' + count;
		if ($('#tabs-3').flowchart('getData').operators[comp_id] != undefined) {
			// bootbox.alert({
			// 	message: '<img class="boot-img" src="../static/scf_static/images/error_img.png"><p class="boot-para">"' + node.text + '" node of Node ID: ' + comp_id + ' already exists.<p>',
			// 	size: 'small'
			// });
			swal({
				title: "",
				text: "'" + node.text + " ' node of Node ID: '" + comp_id + " 'already exists. ",
				icon: "error",
				button: "Ok",
			});
		}
		else {
			var comp_name = node.text;
			var parentType = node.original.nodeType;
			var selDesc = node.original.description;
			if (parentType == 'Security Configurations') {
				var cloudType = node.original.classLabels;
				createOperator(comp_name, comp_id, parentType, selDesc, cloudType);
			}
			else {
				createOperator(comp_name, comp_id, parentType, selDesc);
			}
		}
	}
}

function createOperator(comp_name, comp_id, parentName, selDesc, cloudType) {
	var topX = Math.floor(Math.random() * 31) + 50;
	var leftX = Math.floor(Math.random() * 41) + 90;
	var operatorId = comp_id;

	// $('#src_code').val('');
	var data = {
		top: topX,
		left: leftX,
		nodeType: parentName,
		properties: {
			title: comp_name,
			dataId: comp_id,
			name: comp_name,
			description: selDesc,
			class: comp_id,
			inputs: {
				input_1: {
					label: ''
				}
			},
			outputs: {
				output_1: {
					label: ''
				}
			}
		}
	};
	if (parentName == 'Security Configurations') {
		data['classLabels'] = cloudType;
	}
	$('#tabs-3').flowchart('createOperator', operatorId, data);
	$('.flowchart-operator .cancelNode').remove();
	$('.flowchart-operator').append('<button type="button" class="close cancelNode" aria-hidden="true">×</button>');
}

function initJsTree(finalObjTemp) {
	$("#ajaxTreeCrud").jstree("destroy");
	$('#ajaxTreeCrud').jstree({
		'core': {
			//"multiple": false,
			"check_callback": function (operation, node, parent, position, more) {
				if (operation === "copy_node" || operation === "move_node") {
					return false;
				}
			},
			'themes': {
				'responsive': true
			},
			'data': finalObjTemp
		},
		"types": {
			"default": {
				"icon": "fa fa-clone"
			},
			"root": {
				"icon": "fa fa-folder-open"
			},
			"level1": {
				"icon": "fa fa-shopping-basket"
			},
			"level2": {
				"icon": "fa fa-clone"
			}
		},
		"search": {
			"case_insensitive": true,
			"show_only_matches": true
		},
		"plugins": ["search", "types", "wholerow"]
	});

	$("#ajaxTreeCrud").on("click.jstree", function (evt) {
		var id = evt.target.id;
		if ($('#' + id).hasClass('jstree-disabled')) {
			$('.addNewNode,.renNode,.deleteNode').hide();
		}
		else {
			if (id.indexOf('.') != -1) {
				$('.renNode,.deleteNode').show();
				$('.addNewNode').hide();
			}
			else if (id == 'topLevel_anchor') {
				$('.renNode,.deleteNode').hide();
				$('.addNewNode').show();
			}
			else {
				$('.addNewNode,.renNode,.deleteNode').show();
			}
		}

	});

	$("#ajaxTreeCrud").bind("loaded.jstree", function (event, data) {
		$('#ajaxTreeCrud').jstree("open_node", "#topLevel");
	});
}

function populateSelectedConfig(tempName) {
	var cloudType = $('#cloudName option:selected').attr('data-cloudtype').trim().toLowerCase();
	var cloudName = $('#cloudName option:selected').text().trim();

	if (cloudType == 'aws') {
		$('#policyAWSModal').modal('show');
		$('#tempName').val(tempName);
		$('#cloud').val(cloudName);
		// source.setValue(data);
		populateAWSCluster();
	}
	else {
		$.ajax({
			url: "/clouds/?cloudId=" + $('#cloudName').val() + "&labels=True",
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				$('#policyKubModal').modal('show');
				$('#tempKubName').val(tempName);
				$('#cloudKub').val(cloudName);
				var optionHtml = "<option value=''>Please Select</option>";
				$.each(data, function (k, v) {
					optionHtml += '<option value="' + v + '">' + v + '</option>'
				});
				$('#labelsList').empty().html(optionHtml);
				populateNamespace();
			},
			error: function (msg) {
				// bootbox.alert({
				// 	message: '<img class="boot-img" src="../static/scf_static/images/error_img.png" /><div class="boot-para">' + JSON.parse(msg.responseText).reason + '" </div>'
				// });
				swal({
					title: "",
					text: "" + JSON.parse(msg.responseText).reason,
					icon: "error",
					button: "Ok",
				});
			}
		});

	}
}

function populateNamespace() {
	$.ajax({
		url: "/clouds/?cloudId=" + $('#cloudName').val() + "&namespaces=True",
		type: 'GET',
		cache: false,
		async: false,
		success: function (data) {
			var optionHtml = "<option value=''>Please Select</option>";
			$.each(data, function (k, v) {
				optionHtml += '<option value="' + v + '">' + v + '</option>'
			});
			$('#namespace').empty().html(optionHtml);
		},
		error: function (msg) {
			// bootbox.alert({
			// 	message: '<img class="boot-img" src="../static/scf_static/images/error_img.png" /><div class="boot-para">' + JSON.parse(msg.responseText).reason + '" </div>'
			// });
			swal({
				title: "",
				text: "" + JSON.parse(msg.responseText).reason,
				icon: "error",
				button: "Ok",
			});
		}
	});
}

function populateAWSCluster() {
	$.ajax({
		url: "/clouds/?cloudId=" + $('#cloudName').val() + "&clusters=True",
		type: 'GET',
		cache: false,
		async: false,
		success: function (data) {
			var optionHtml = "<option value=''>Please Select</option>";
			$.each(data, function (k, v) {
				for (var i = 0; i < v.clusters.length; i++) {
					optionHtml += '<option value="' + v.clusters[i] + '" data-region="' + v.region + '">' + v.clusters[i] + '</option>'
				}
			});
			$('#assetList').empty().html(optionHtml);
		},
		error: function () {

		}
	});
}

function createPolicyInstance() {
	var cloudType = $('#cloudName option:selected').attr('data-cloudtype').trim().toLowerCase();
	var cloudId = $('#cloudName').val();
	if (cloudType == 'aws') {
		var region = $('#assetList option:selected').attr('data-region');
		var vpcId = $('#assetList').val().toString();
		var templateId = $('#tempName').val();
		var dataString = { 'region': region, 'vpcId': vpcId, 'cloudId': cloudId, 'templateId': templateId }
	}
	else {
		var namespace = $('#namespace').val();
		var templateId = $('#tempKubName').val();
		var podSelectorLabels = $('#labelsList').val();
		var dataString = { "namespace": namespace, "podSelectorLabels": podSelectorLabels, "templateId": templateId, 'cloudId': cloudId }
	}
	$.ajax({
		url: "/policyinstances/",
		type: 'POST',
		cache: false,
		async: false,
		data: JSON.stringify(dataString),
		contentType: 'application/json',
		success: function (data) {
			// bootbox.alert({
			// 	message: '<img class="boot-img" src="../static/scf_static/images/CheckMark.png" /><div class="boot-para">The policy has been ' + action + 'ed successfully.</div>',
			// 	size: 'small'
			// });
			swal({
				title: "",
				text: 'The policy has been ' + action + 'ed successfully.',
				icon: "success",
				button: "Ok",
			});
		},
		error: function (xhr) {
			var xhrJSON = JSON.parse(xhr.responseText);
			var msg = '';
			$.each(xhrJSON.reasons, function (k, v) {
				$.each(v, function (ind, val) {
					msg += '<p><strong>' + ind + '</strong> : ' + val + '</p>';
				});
			});
			// bootbox.alert({
			// 	message: '<img class="boot-img" src="../static/scf_static/images/error_img.png" /><div class="boot-para">' + msg + '</div>'
			// });
			swal({
				title: "",
				text: '' + msg,
				icon: "error",
				button: "Ok",
			});
		}
	});
}