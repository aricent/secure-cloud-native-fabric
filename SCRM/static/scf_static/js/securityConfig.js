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
var policyCrud = {
	intialVars: function () {
		cloudType = $('#cloudType'),
			parentPolicy = $('#policyDelTable'),
			policyModal = $("#sgActions"),
			tempModal = $('#sgTempActions'),
			groupIdKub = '',
			tempTable = $('#policyTempTable')
	},
	populateAllPolicies: function () {
		$.ajax({
			url: "/policyinstances/",
			type: 'GET',
			cache: false,
			async: true,
			success: function (data) {
				var trHtml = '';
				if (data.length > 0) {
					$.each(data, function (key, value) {
						if (value.cloudType == 'AWS') {
							trHtml += '<tr data-id="' + value.name + '">' + '<td>' + value.cloudType + '</td>' + '<td>' + value.name + '</td>' + '<td>' + value["id"] + '</td>' + '<td>' + value["cluster"] + '</td>' + '<td>' + value.cloudId + '</td>' + '<td>' + value.description + '</td>' + '</tr>';
						}
						else {
							trHtml += '<tr data-id="' + value.name + '">' + '<td>' + value.cloudType + '</td>' + '<td>' + value.name + '</td>' + '<td>' + value["id"] + '</td>' + '<td>' + '' + '</td>' + '<td>' + value.cloudId + '</td>' + '<td>' + '' + '</td>' + '</tr>';
						}
					});
				}
				else {
					trHtml = '<tr><td colspan="6">No records found</td></tr>';
				}
				parentPolicy.find('tbody').empty().append(trHtml);
			},
			error: function (xhr) {

			}
		});
	},

	populateAllTemplates: function () {
		$.ajax({
			url: "/policytemplates/",
			type: 'GET',
			cache: false,
			async: true,
			success: function (data) {
				var trHtml = '';
				if (data.length > 0) {
					$.each(data, function (key, value) {
						if (value.cloudType == 'AWS') {
							trHtml += '<tr data-id="' + value.id + '">' + '<td>' + value.cloudType + '</td>' + '<td>' + value.name + '</td>' + '<td>' + value.description + '</td>' + '<td>' + ' ' + '</td>' + '<td>' + ' ' + '</td>' + '</tr>';
						}
						else {
							trHtml += '<tr data-id="' + value.id + '">' + '<td>' + value.cloudType + '</td>' + '<td>' + value.name + '</td>' + '<td>' + '' + '</td>' + '<td>' + ' ' + '</td>' + '<td>' + ' ' + '</td>' + '</tr>';
						}
					});
				}
				else {
					trHtml = '<tr><td colspan="5">No records found</td></tr>';
				}
				tempTable.find('tbody').empty().append(trHtml);
			},
			error: function (xhr) {

			}
		});
	},

	createTemplate: function () {
		$('#sgTempForm')[0].reset();
		$("#sgTempActions .modal-title").text('Create Template');
		$('.createTemp').text('Create').removeClass('editTemp');
		cloudType.find('option[value="aws"]').attr('selected', true);
		cloudType.attr('disabled', false);
	},
	createPolicy: function () {
		$('#sgForm')[0].reset();
		$("#sgActions .modal-title").text('Associate Policy');
		$('.createPolicy').text('Create').removeClass('editPolicy');
		cloudType.find('option[value="aws"]').attr('selected', true);
		cloudType.attr('disabled', false);
	},

	operatingTemplates: function (action) {
		var selCloud = cloudType.find('option:selected').val().toUpperCase().trim();
		var dataString = yamlTextStr;
		var contentType = 'text/plain';
		var datatype = 'text';
		if (action == 'edit') {
			var typeStr = 'PUT';
			var urlName = "/policytemplates/?id=" + groupIdKub;;
		}
		else {
			var typeStr = 'POST';
			var urlName = "/policytemplates/?cloudType=" + selCloud;
		}
		$.ajax({
			url: urlName,
			type: typeStr,
			data: dataString,
			cache: false,
			async: true,
			contentType: contentType,
			dataType: datatype,
			success: function (data) {
				//data = JSON.parse(data);
				// bootbox.alert({
				// 	message: '<img class="boot-img" src="../static/scf_static/images/CheckMark.png" /><div class="boot-para">The policy has been ' + action + 'ed successfully.</div>'
				// });
				swal({
					title: "",
					text: "The policy has been " + action + "ed successfully.",
					icon: "success",
					button: "Ok",
				});

				setTimeout(function () {
					policyCrud.populateAllTemplates();
				}, 800);
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
					text: "" + msg,
					icon: "error",
					button: "Ok",
				});
			}
		});
		tempModal.modal('hide');
	},

	addingPolicy: function (action) {
		if (action == 'create') {
			var cloudType = $('#cloudType option:selected').val();
			if (cloudType == 'aws') {
				var region = $('#clusterList option:selected').attr('data-region');
				var vpcId = $('#clusterList').val();
				var cloudId = $('#cloudName').val();
				var templateId = $('#tempName').val();
				var dataString = { 'region': region, 'vpcId': vpcId, 'cloudId': cloudId, 'templateId': templateId }
			}
			$.ajax({
				url: "/policyinstances/",
				type: 'POST',
				cache: false,
				async: false,
				data: dataString,
				success: function (data) {
					// bootbox.alert({
					// 	message: '<img class="boot-img" src="../static/scf_static/images/CheckMark.png" /><div class="boot-para">The policy has been ' + action + 'ed successfully.</div>'
					// });
					swal({
						title: "",
						text: "The policy has been " + action + "ed successfully.",
						icon: "success",
						button: "Ok",
					});

					setTimeout(function () {
						policyCrud.populateAllPolicies();
					}, 800);
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
						text: "" + msg,
						icon: "error",
						button: "Ok",
					});
				}
			});
		}
		policyModal.modal('hide');
	},

	editTemplate: function (policyDelIndex) {
		$('#sgTempForm')[0].reset();
		groupIdKub = '';
		tempModal.modal('show');
		$("#sgTempActions .modal-title").text('Edit Template');
		$('.createTemp').text('Modify');
		$('.createTemp').hasClass('editTemp') ? $('.createTemp').addClass('') : $('.createTemp').addClass('editTemp');
		var grpID = tempTable.find('tbody tr').eq(policyDelIndex).attr('data-id');
		var cloudTypeSel = tempTable.find('tbody tr').eq(policyDelIndex).find('td:first').text().toLowerCase();
		$.ajax({
			url: "/policytemplates/?id=" + grpID,
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				cloudType.find('option[value="' + cloudTypeSel + '"]').attr('selected', true);
				cloudType.attr('disabled', true);
				groupIdKub = grpID;
				source.setValue(data);
			},
			error: function () {

			}
		});
	},

	editPolicy: function (policyDelIndex) {
		$('#sgForm')[0].reset();
		groupIdKub = '';
		policyModal.modal('show');
		$("#sgActions .modal-title").text('Edit Policy');
		$('.createPolicy').text('Modify');
		$('.createPolicy').hasClass('editPolicy') ? $('.createPolicy').addClass('') : $('.createPolicy').addClass('editPolicy');
		var grpID = parentPolicy.find('tbody tr').eq(policyDelIndex).attr('data-id');
		var cloudTypeSel = parentPolicy.find('tbody tr').eq(policyDelIndex).find('td:first').text().toLowerCase();
		$.ajax({
			url: "/policyinstances/?policyId=" + grpID,
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				cloudType.find('option[value="' + cloudTypeSel + '"]').attr('selected', true);
				cloudType.attr('disabled', true);
				groupIdKub = grpID;
				source.setValue(data);
			},
			error: function () {

			}
		});
	},
	deleteTemplate: function (ind) {
		var grpID = tempTable.find('tbody tr').eq(ind).attr('data-id');
		if (grpID != undefined) {
			swal({
				title: "",
				text: "Are you sure you want to delete the template?",
				icon: "warning",
				buttons: true,
				dangerMode: true,
				showCancelButton: true,
				closeOnConfirm: true,
				confirmButtonText: "Yes"
			})
				.then(function (willDelete) {
					if (willDelete) {
						$.ajax({
							url: "/policytemplates/?id=" + grpID,
							type: 'DELETE',
							cache: false,
							async: false,
							success: function (data) {
								setTimeout(function () {
									policyCrud.populateAllTemplates();
								}, 800);
							},
							error: function () {
							}
						});

					}
				});
		}
	},

	deletePolicy: function (ind) {
		var grpID = parentPolicy.find('tbody tr').eq(ind).attr('data-id');
		if (grpID != undefined) {
			swal({
				title: "",
				text: "Are you sure you want to delete the groupID:'" + grpID + "'?",
				icon: "warning",
				buttons: true,
				dangerMode: true,
				showCancelButton: true,
				closeOnConfirm: true,
				confirmButtonText: "Yes"
			})
				.then(function (willDelete) {
					if (willDelete) {
						$.ajax({
							url: "/policyinstances/?policyId=" + grpID,
							type: 'DELETE',
							cache: false,
							async: false,
							success: function (data) {
								setTimeout(function () {
									policyCrud.populateAllPolicies();
								}, 800);
							},
							error: function () {
							}
						});

					}
				});
		}
	},
	handleCloud: function (sel) {
		source.setValue('');
	},
	resetState: function () {
		$('.editSG,.deleteSG,.editSGTemp,.deleteSGTemp').attr('disabled', true);
		policyDelIndex = '';
		$('#policyDelTable > tbody > tr, #policyTempTable > tbody > tr').removeClass('table-info');
	},
	populateTemplateNames: function (cloudType) {
		$.ajax({
			url: "/policytemplates/?cloudType=" + cloudType,
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				var optionHtml = "<option value=''>Please Select</option>";
				$.each(data, function (k, v) {
					optionHtml += '<option value="' + v.id + '">' + v.name + '</option>'
				});
				$('#tempName').empty().html(optionHtml);
			},
			error: function () {

			}
		});
	},
	populateCloudList: function (clType, tempId) {
		$.ajax({
			url: "/policytemplates/?id=" + tempId,
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				source.setValue(data);
			},
			error: function () {

			}
		});

		$.ajax({
			url: "/clouds/?cloudType=" + clType,
			type: 'GET',
			cache: false,
			async: false,
			success: function (data) {
				var optionHtml = "<option value=''>Please Select</option>";
				$.each(data, function (k, v) {
					optionHtml += '<option value="' + v.Id + '">' + v.CloudName + '</option>'
				});
				$('#cloudName').empty().html(optionHtml);
			},
			error: function () {

			}
		});
	},
	populateClusters: function (cloudID) {
		$.ajax({
			url: "/clouds/?cloudId=" + cloudID + "&clusters=True",
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
				$('#clusterList').empty().html(optionHtml);
			},
			error: function () {

			}
		});
	}
};

$(document).ready(function () {
	$("#sgActions").on('show.bs.modal', function () {
		$('#awsDetailsCarousel').carousel({
			interval: false
		});
		$('.panelBox:eq(1),.panelBox:eq(2),.panelBox:eq(3)').removeClass('active filled');
		$('.panelBox:eq(0)').removeClass('filled');
	});

	$('.awsSelects').on('change', function () {
		var ind = $(this).parents('.carousel-item').index();
		var id = $(this).attr('id');
		if (id == 'cloudTypeSel') {
			source.setValue('');
			$('.panelBox:eq(1),.panelBox:eq(2),.panelBox:eq(3)').removeClass('active filled');
		}
		else if (id == 'tempName') {
			$('.panelBox:eq(2),.panelBox:eq(3)').removeClass('active filled');
		}
		else if (id == 'cloudName') {
			$('.panelBox:eq(3)').removeClass('active filled');
		}
		if ($(this).val() != '') {
			if (id == 'cloudTypeSel') {
				policyCrud.populateTemplateNames($(this).val().toUpperCase());
			}
			else if (id == 'tempName') {
				var cloudType = $('#cloudTypeSel').val().toUpperCase();
				policyCrud.populateCloudList(cloudType, $(this).val());
			}
			else if (id == 'cloudName') {
				policyCrud.populateClusters($(this).val());
			}
			$('.panelBox').removeClass('active');
			$('.panelBox').eq(ind).addClass('filled');
			$('.panelBox').eq(ind + 1).addClass('active');
			$('#awsDetailsCarousel').carousel("next");
		}
		else {
			$(this).focus();
		}
	});

	$(document).on('click', '.panelBox.filled', function (e) {
		var ind = Number($(this).text().trim());
		$('.panelBox').removeClass('active');
		$('.panelBox').eq(ind - 1).addClass('active');
		$("#awsDetailsCarousel").carousel(ind - 1);
	});

	$('.headTxt').on('click', function () {
		$('.headTxt').removeClass('active');
		$(this).addClass('active');
		var path = $(this).parent().attr('data-href');
		$('.nodeDiv').hide();
		$('.' + path).show();
		policyCrud.resetState();
	});

	$('.headingTwo,.headingThree').hide();
	policyCrud.intialVars();
	var policyDelIndex = '';
	policyCrud.populateAllPolicies();
	policyCrud.populateAllTemplates();

	$('.editSG,.deleteSG,.editSGTemp,.deleteSGTemp').attr('disabled', true);

	$(document).on('click', '#policyDelTable > tbody > tr, #policyTempTable > tbody > tr', function (e) {
		$('#policyDelTable > tbody > tr, #policyTempTable > tbody > tr').removeClass('table-info');
		$(this).addClass('table-info');
		if ($(this).parents('table').attr('id') == 'policyTempTable') {
			$('.editSGTemp,.deleteSGTemp').attr('disabled', false);
		}
		else {
			$('.editSG,.deleteSG').attr('disabled', false);
		}
		policyDelIndex = $(this).index();
	});

	$('#cloudType, #cloudTypeSel').on('change', function () {
		policyCrud.handleCloud($(this).val());
	});

	$('.createPolicy').on('click', function () {
		if ($(this).hasClass('editPolicy')) {
			policyCrud.addingPolicy('edit');
		}
		else {
			policyCrud.addingPolicy('create');
		}
	});

	$('.createTemp').on('click', function () {
		if ($(this).hasClass('editTemp')) {
			policyCrud.operatingTemplates('edit');
		}
		else {
			policyCrud.operatingTemplates('create');
		}
	});

	$('.addSG').on('click', function () {
		policyCrud.createPolicy();
	});

	$('.editSG').on('click', function () {
		policyCrud.editPolicy(policyDelIndex);
	});

	$('.deleteSG').on('click', function () {
		policyCrud.deletePolicy(policyDelIndex);
	});

	$('.addSGTemp').on('click', function () {
		policyCrud.createTemplate();
	});

	$('.editSGTemp').on('click', function () {
		policyCrud.editTemplate(policyDelIndex);
	});

	$('.deleteSGTemp').on('click', function () {
		policyCrud.deleteTemplate(policyDelIndex);
	});

	$(document).on('click', '.headStart >div[data-href="headingThree"]', function () {
		initNeoGraph('#neo4jd3');
	});
});