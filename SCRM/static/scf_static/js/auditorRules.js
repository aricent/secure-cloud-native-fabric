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
var setAuditTimer;
var tableResp = '';
$(document).ready(function () {
    clearInterval(setAuditTimer);
    auditTableInit();
    // $('.sweet-alert').parent().remove();

    $('#auditorList').on('change', function (e) {
        var auditorName = $(this).val();
        yamlAuditFetch(auditorName, '');
    });

    $('#createAuditor').click(function () {
        createAuditor();
    });

    $(document).on('click', '.editAudit', function (e) {
        e.stopImmediatePropagation();
        // console.log($(this).parents('.footable-detail-row').index())
        var ind = $(this).parents('.footable-detail-row').index() - 1;
        var auditorInst = $('#auditorTable tbody tr').eq(ind).find('td:first').text();
        yamlAuditFetch(auditorInst, 'view');
    });

    $(document).on('click', '.viewReport', function (e) {
        e.stopImmediatePropagation();
        var ind = $(this).parents('.footable-detail-row').index() - 1;
        var cluster = $('#auditorTable tbody tr').eq(ind).find('td').eq(1).text();
        var auditType = $('#auditorTable tbody tr').eq(ind).find('td').eq(2).text();
        populateReport(cluster, auditType);
    })
});

// to populate all auditors
function auditTableInit(flag) {
    $.ajax({
        "url": '/auditors/',
        "type": 'GET',
        "cache": false,
        "success": function (data) {
            if (flag == 'check') {
                var len = (data.length >= tableResp.length) ? data.length : tableResp.length;
                if (data.length != tableResp.length) {
                    calNeo4jGraph('KUBERNETES', '#neo4jd3');
                    auditTableInit();
                    return false;
                }
                else {
                    for (var i = 0; i < len; i++) {
                        if (data[i].runState != tableResp[i].runState) {
                            calNeo4jGraph('KUBERNETES', '#neo4jd3');
                            auditTableInit();
                            return false;
                        }
                    }
                }
            }
            else {
                tableResp = data;
                clearInterval(setAuditTimer);
                setAuditTimer = setInterval(function () {
                    auditTableInit('check');
                }, 15000);
                var ind = 0;
                if ($('#auditorTable').length > 0) {
                    $('#auditorTable').footable({
                        "showToggle": true,
                        "toggleColumn": "last",

                        "columns": [{ "name": "auditor_name", "title": "Name", "style": { "maxWidth": 100, "overflow": "hidden", "textOverflow": "ellipsis", "wordBreak": "keep-all", "whiteSpace": "nowrap" } }, { "name": "cluster", "title": "Cluster", "style": { "maxWidth": 70, "overflow": "hidden", "textOverflow": "ellipsis", "wordBreak": "keep-all", "whiteSpace": "nowrap" } }, { "name": "auditor_type", "title": "Type", "style": { "maxWidth": 100, "overflow": "hidden", "textOverflow": "ellipsis", "wordBreak": "keep-all", "whiteSpace": "nowrap" } }, { "name": "runState", "title": "Status" }, { "name": "config", "title": "Configuration", "breakpoints": "all", "style": { "maxWidth": 100, "overflow": "hidden", "textOverflow": "ellipsis", "wordBreak": "keep-all", "whiteSpace": "nowrap" } }, {
                            "name": "actions", "title": "Actions", "formatter": function (value) {
                                if (data[ind].runState == 'REPORT_AVAILABLE') {
                                    return '<span class="editAudit">View <i class="fa fa-eye"></i></span><span class="delAudit" onclick="deleteAudit(this)">Delete <i class="fa fa-trash-o"></i></span><span class="viewReport">View Report <i class="fa fa-file"></i></span>';
                                }
                                else {
                                    return '<span class="editAudit">View <i class="fa fa-eye"></i></span><span class="delAudit" onclick="deleteAudit(this)">Delete <i class="fa fa-trash-o"></i></span>';
                                }
                                ind++;
                            },
                            "breakpoints": "all"
                        }],

                        "rows": data
                    });
                }
            }
        },
        "error": function (xhr) {

        }
    });
}

function populateSelectedAuditors(auditType) {
    $('#auditType').val(auditType);
    var getAjaxHeader;
    getAjaxHeader = $.ajax({
        url: "/auditors/?auditortype=" + auditType,
        cache: false,
        type: 'GET',
        success: function (data) {
            $('#auditorModal').modal('show');
            var auditorArr = getAjaxHeader.getResponseHeader('auditors').split(',');
            var htmlStr = '';
            $.each(auditorArr, function (key, value) {
                if (value.indexOf('_default') != -1) {
                    htmlStr += '<option value="' + value + '" selected>' + value + '</option>';
                }
                else {
                    htmlStr += '<option value="' + value + '">' + value + '</option>';
                }
            });
            $('#auditorList').empty().append(htmlStr);
            source.setValue(data);
        },
        error: function (msg) {
            // bootbox.alert({
            //     message: '<img class="boot-img" src="../static/scf_static/images/error_img.png"><p class="boot-para">' + msg.responseJSON.message + '<p>'
            // });
            swal({
                title: "",
                text: "" + msg.responseJSON.message,
                icon: "error",
                button: "Ok",
            });
        }
    });
    clusterList(responseData);
}

function yamlAuditFetch(auditorName, type) {
    var getAjaxHeader = $.ajax({
        url: "/auditors/?auditorname=" + auditorName,
        cache: false,
        type: 'GET',
        success: function (data) {
            if (type == 'view') {
                $('#auditorModalView').modal('show');
                var auditorName = getAjaxHeader.getResponseHeader('auditorname');
                var auditorType = getAjaxHeader.getResponseHeader('auditortype');
                var clusterName = auditorName.replace(auditorType + '_', '');
                $('.viewAuditType').val(auditorType);
                $('.viewAuditName').val(auditorName);
                $('.clusterName').val(clusterName);
            }
            setTimeout(function () {
                source.setValue(data);
            }, 200)

        },
        error: function () {

        }
    });
}

function selectAuditTableRow(auditName) {
    $('#auditorTable > tbody > tr').removeClass('selectedRow');
    $.each(tableResp, function (key, value) {
        if (value.auditor_name == auditName) {
            $('#auditorTable > tbody > tr:not(".footable-detail-row")').eq(key).addClass('selectedRow');
            $('#auditorTable > tbody > tr.selectedRow').trigger('click');
            return false;
        }
    });
}

function createAuditor() {
    //console.log('yamlTextStr  ' + yamlTextStr);
    var auditType = $('#auditType').val();
    $.ajax({
        url: '/auditors/',
        type: 'POST',
        cache: false,
        data: yamlTextStr,
        contentType: 'text/plain',
        dataType: 'text',
        headers: {
            'auditortype': auditType,
            'clusters': $('#clusterList').val().toString(),
            'posturename': $('.postureList').val() != undefined ? $('.postureList').val() : $('#step-3 .MultiCarousel-inner .item.selected').text().trim()
        },
        success: function (data) {
            // bootbox.alert({
            //     message: '<img class="boot-img" src="../static/scf_static/images/CheckMark.png"><p class="boot-para">Auditor instance has been created successfully.<br/>You can <strong>Run</strong> the auditor from CRISP.<p>'
            // });
            swal({
                title: "",
                text: "Auditor instance has been created successfully.You can start the auditor from CRISP.",
                icon: "success",
                button: "Ok",
            });
            calNeo4jGraph('KUBERNETES', '#neo4jd3');
            $('#auditorModal').modal('hide');
            setTimeout(function () {
                auditTableInit();
                populateLabels();
            }, 1000)
        },
        error: function (msg) {
            // console.log(JSON.stringify(msg));
            // bootbox.alert({
            //     message: '<img class="boot-img" src="../static/scf_static/images/error_img.png"><p class="boot-para">' + JSON.parse(msg.responseText).reason + '<p>'
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

function clusterList(responseData) {
    var clusterHtml = '';
    $.each(responseData[0].nodes, function (key, val) {
        var labelTxt = $.trim(val.labels[0]);
        if (labelTxt == 'Cluster') {
            clusterHtml += '<option value="' + val.properties.name + '">' + val.properties.name + '</option>';
        }
    });
    $('#clusterList').empty().html(clusterHtml);
}