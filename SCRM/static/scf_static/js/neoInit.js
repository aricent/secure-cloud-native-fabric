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
var neo4jFormatData = {
  "results": [
    {
      "data": [
        {
          "graph": {

          }
        }
      ]
    }
  ],
  "errors": []
};
var nodeDict = {};
var sortedLabels = [];
var responseData = '';
var selectedNodesArr = [];
var timeClearSet, setTimerInter;
var counter = 0;
var cloudSel = 'KUBERNETES';
$(document).ready(function () {
  if ($('#goalsCarousel').length <= 0) {
    calNeo4jGraph(cloudSel, '#neo4jd3');
  }
  /* handling right click actions for neo4J garph on pod */
  $(document).on('mousedown', '#neo4jd3[data-graph="crispNeo"] .node.node-image', function (e) {
    if (e.which == 3) {
      var podName = e.target.__data__.properties.name;
      var alarmTxt = e.target.__data__.properties.alarmText;
      if (alarmTxt != undefined) {
        contextualMenuInit(podName, alarmTxt);
      }
    }
  });

  $(document).off('click', '.nodeBtn').on('click', '.nodeBtn', function () {
    var id = '#' + $('div.neo4jd3:visible').attr('id');
    $(this).toggleClass('selectedBtn');
    selectedNodeFunc(id);
    clearInterval(timeClearSet);
    if ($('.sliderCheckbox').is(':checked')) {
      timeClearSet = setInterval(function () {
        calNeo4jGraph(cloudSel, id);
      }, 20000);
    }
    else {
      counter = 0;
      clearInterval(setTimerInter);
    }
  });
  // setTimerInter = setInterval(setTimer, 1000);
  // timeClearSet = setInterval(function(){
  //   calNeo4jGraph(cloudSel);
  // }, 20000);
  //  calNeo4jGraph(cloudSel);
  $('.timeCounterSpan').hide();
  $('.cloudSel').on('change', function () {
    cloudSel = $(this).val();
    calNeo4jGraph(cloudSel, '#neo4jd3');
    setTimeout(function () {
      populateLabels();
    }, 1000);
  });

  $('.sliderCheckbox').on('change', function () {
    if ($(this).is(':checked')) {
      setTimerInter = setInterval(setTimer, 1000);
      timeClearSet = setInterval(function () {
        calNeo4jGraph(cloudSel, '#neo4jd3');
      }, 20000);
      $('.timeCounterSpan').fadeIn(500);
    }
    else {
      counter = 0;
      clearInterval(timeClearSet);
      clearInterval(setTimerInter);
      $('.timeCounterSpan').fadeOut(500);
    }
  });

  $('.fullSrnBtn').on('click', function () {
    $('.neoDivCard').addClass('neofullGraph');
    $('.smallSrnBtn,.fullSrnBtn').toggle();
  });

  $('.smallSrnBtn').hide();

  $('.smallSrnBtn').on('click', function () {
    $('.neoDivCard').removeClass('neofullGraph');
    $('.smallSrnBtn,.fullSrnBtn').toggle();
  });

  $(document).on('shown.bs.collapse', '.collapse', function () {
    var id = $(this).attr('id');
    $('.accDiv[href="#' + id + '"]').find(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
  }).on('hidden.bs.collapse', function () {
    var id = $(this).attr('id');
    $('.accDiv[href="#' + id + '"]').find(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
  });

  setTimeout(function () {
    populateLabels();
  }, 2000);

});

function setTimer() {
  $('.timeCounterSpan').text((20 - counter) + ' sec'); //20 sec timer
  counter++;
}

function selectedNodeFunc(id) {
  selectedNodesArr = [];
  var $selectednode = $('.nodeBtn.selectedBtn');
  if ($selectednode.length > 0) {
    $selectednode.each(function (key, value) {
      selectedNodesArr.push($.trim($(this).text()));
    });
  }
  calNeo4jGraph(cloudSel, id);
}

function calNeo4jGraph(cloudSel, id) {
  nodeDict = {};
  counter = 0;
  if ($('#neo4jd3').attr('data-graph') == 'crispNeo') {
    var url = '/vpc/?cloudType=' + cloudSel + '&viewType=crisp'
  }
  else if ($('#neo4jd3').attr('data-graph') == 'auditNeo') {
    var url = '/vpc/?cloudType=' + cloudSel + '&viewType=crisp'
  }
  else {
    var url = '/vpc/?cloudType=' + cloudSel
  }
  $.ajax({
    type: 'GET',
    url: url,
    datatype: 'json',
    success: function (data) {
      if (data.length > 0) {
        responseData = data;
        if (selectedNodesArr.length > 0) {
          var newNodesGraph = [];
          var newRelationArr = [];
          var newNodeIdArr = [];
          $.each(data[0].nodes, function (key, val) {
            var labelTxt = $.trim(val.labels[0]);
            if ($.inArray(labelTxt, selectedNodesArr) != -1) {
              newNodesGraph.push(val);
              newNodeIdArr.push(val.id);
            }
          });
          neo4jFormatData.results[0].data[0].graph.nodes = newNodesGraph;
          if (selectedNodesArr.length == 1) {
            neo4jFormatData.results[0].data[0].graph.relationships = [];
          }
          else {
            $.each(data[1].relationships, function (key, val) {
              if (($.inArray(val.startNode, newNodeIdArr) != -1) && ($.inArray(val.endNode, newNodeIdArr) != -1)) {
                newRelationArr.push(val);
              }
            });
            //  console.log(' relation length  ' + newRelationArr.length + '  newRelationArr ' + JSON.stringify(newRelationArr));
            neo4jFormatData.results[0].data[0].graph.relationships = newRelationArr;
          }
        }
        else {
          neo4jFormatData.results[0].data[0].graph.nodes = data[0].nodes;
          neo4jFormatData.results[0].data[0].graph.relationships = data[1].relationships;
        }
        sortedLabels = [];
        $.each(data[0].nodes, function (key, val) {
          nodeDict[val.id] = val;
          if (sortedLabels.indexOf(val.labels[0]) == -1) {
            sortedLabels.push(val.labels[0])
          }
        });
        sortedLabels.sort();
      }
      else {
        neo4jFormatData.results[0].data[0].graph.relationships = [];
        neo4jFormatData.results[0].data[0].graph.nodes = [];
      }
      initNeoGraph(id);
      populateEventTable(data);
    }
  });
}

function populateEventTable(data) {
  var key = 1;
  var cloudTypeSel = $('.cloudSel').length > 0 ? $('.cloudSel option:selected').text() : 'Kubernetes';
  $('#alarmTable tbody').empty();
  var trHtml = '';
  $.each(data[0].nodes, function (k, v) {
    if (v.labels[0].toLowerCase() == 'alarm') {
      trHtml += '<tr>' + '<td>' + key + '</td>' + '<td>' + cloudTypeSel + '</td>' + '<td>' + v.properties.alarmState + '</td>' + '<td>' + v.properties.name + '</td>' + '<td>' + v.properties.alarmText + '</td>' + '<td>' + v.properties.alarmClass + '</td>' + '</tr>';
      key++;
    }
  });
  if (trHtml.length <= 0) {
    trHtml = '<tr>' + '<td colspan="2">No Alarms found</td>' + '</tr>';
  }
  $('#alarmTable tbody').append(trHtml);
}


function contextualMenuInit(pName, aTxt) {
  context.init({
    fadeSpeed: 100,
    above: 'auto',
    left: 'auto',
    preventDoubleContext: true,
    compress: true
  });
  context.attach('.node.node-image', [
    {
      text: 'Delete',
      action: function (e) {
        e.preventDefault();
        podActions(pName, aTxt, 'delete');
      }
    },
    {
      text: 'Isolate',
      action: function (e) {
        e.preventDefault();
        podActions(pName, aTxt, 'isolate');
      }
    },
    {
      text: 'Isolate and Delete',
      action: function (e) {
        e.preventDefault();
        podActions(pName, aTxt, 'isolate_delete');
      }
    }
  ]);
}

function podActions(podName, alarmTxt, action) {
  $.ajax({
    url: '/monitoredobject/?action=' + action,
    type: 'POST',
    cache: false,
    data: { "objectName": podName, "alarmText": alarmTxt },
    success: function (data) {
      calNeo4jGraph(cloudSel, '#neo4jd3');
      // bootbox.alert({
      //   message: '<img class="boot-img" src="../static/scf_static/images/CheckMark.png" /><div class="boot-para">Action has been completed successfully on Pod "' + podName + '" .</div>'
      // });
      swal({
        title: "",
        text: "Action has been completed successfully on Pod '" + podName + "' .",
        icon: "success",
        button: "Ok",
      });
    },
    error: function (xhr) {
      // bootbox.alert({
      //   message: '<img class="boot-img" src="../static/scf_static/images/error_img.png" /><div class="boot-para">Action has not been completed successfully on Pod "' + podName + '" .</div>'
      // });
      swal({
        title: "",
        text: "Action has not been completed successfully on Pod '" + podName + "' .",
        icon: "error",
        button: "Ok",
      });
    }
  });
}

function initNeoGraph(id) {
  if ($(id).attr('data-graph') == 'auditNeo') {
    var auditImg = '/static/scf_static/images/file_add.png';
  }
  else {
    var auditImg = '';
  }
  if (id == '#policyNeo4jd3') {
    var policyImg = '/static/scf_static/images/file_add.png';
  }
  else {
    var policyImg = '';
  }
  var neo4jd3 = new Neo4jd3(id, {
    nodeRadius: 20,
    neo4jData: neo4jFormatData,
    zoomFit: false,
    images: {
      'Auditor': auditImg,
      'SecurityConfigurations': policyImg,
      'WorkLoad|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',
      'Namespace|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',
      'Cluster|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',
      'Nodes|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',
      'Component|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',
      'Policy|alarms|alarmClass|Critical': '/static/scf_static/images/emergency.svg',

      'WorkLoad|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',
      'Namespace|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',
      'Cluster|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',
      'Nodes|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',
      'Component|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',
      'Policy|alarms|alarmClass|Alert': '/static/scf_static/images/warn.png',

      'WorkLoad|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',
      'Namespace|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',
      'Cluster|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',
      'Nodes|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',
      'Component|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',
      'Policy|alarms|alarmClass|Error': '/static/scf_static/images/warn.png',

      'WorkLoad|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',
      'Namespace|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',
      'Cluster|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',
      'Nodes|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',
      'Component|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',
      'Policy|alarms|alarmClass|Warning': '/static/scf_static/images/warn.png',

      'WorkLoad|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',
      'Namespace|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',
      'Cluster|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',
      'Nodes|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',
      'Component|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',
      'Policy|alarms|alarmClass|Emergency': '/static/scf_static/images/danger.png',

      'AuditorInstance|state|TRIGGERED': '/static/scf_static/images/triggered.png',
      'AuditorInstance|state|REPORT_AVAILABLE': '/static/scf_static/images/report.png',
    },
    icons: iconLabelMaps,
    onNodeClick: function (node) {
      if ($(id).attr('data-graph') == 'auditNeo') {
        if (node.labels[0] == 'Auditor') {
          populateSelectedAuditors(node.properties.name);
        }
        if (node.labels[0] == 'AuditorInstance') {
          selectAuditTableRow(node.properties.name);
        }
      }
      if (id == '#policyNeo4jd3') {
        if (node.labels[0] == 'SecurityConfigurations') {
          populateSelectedConfig(node.properties.displayName);
        }
      }
    },
    onNodeDoubleClick: function (node) {
      if (selectedNodesArr.length > 0) {
        var neoData = { "results": [{ "data": [{ "graph": { "nodes": [], "relationships": [] } }] }], "errors": [] };
        var nodeID = node.id;
        var visibleNodes = [];
        var newNodes = [];
        $('.node.node-icon').each(function (ind, val) {
          visibleNodes.push($(this).attr('data-id'));
        });

        $.each(responseData[1].relationships, function (key, val) {
          if (val.startNode == nodeID) {
            if ($.inArray(val.endNode, visibleNodes) == -1) {
              newNodes.push(val.endNode)
              neoData.results[0].data[0].graph.relationships.push(val);
            }
          }
          else if (val.endNode == nodeID) {
            if ($.inArray(val.startNode, visibleNodes) == -1) {
              newNodes.push(val.startNode)
              neoData.results[0].data[0].graph.relationships.push(val);
            }
          }
        });

        $.each(responseData[0].nodes, function (key, val) {
          if ($.inArray(val.id, newNodes) != -1) {
            neoData.results[0].data[0].graph.nodes.push(val);
          }
        });
        neo4jd3.updateWithNeo4jData(neoData);
      }
    },
    onNodeMouseEnter: function (node) {
      if (node.labels[0] == 'AuditorInstance') {
        var clusterName = '';
        $('.node[data-id="' + node.id + '"]').addClass('auditorNode');
        if ($(id).attr('data-graph') == 'auditNeo') {
          $.each(responseData[1].relationships, function (key, val) {
            if (val.startNode == node.id && val.type.toLowerCase() == 'audits') {
              var clusterObj = nodeDict[val.endNode];
              clusterName = clusterObj.properties.name;
            }
          });
          if (node.properties.state == 'IDLE' || node.properties.state == 'REPORT_AVAILABLE') {
            auditContextMenuStart(node.properties.name, clusterName);
          }
        }
      }
      if (node.labels[0] == 'Auditor') {
        $('.node[data-id="' + node.id + '"]').addClass('auditorTypeNode');
      }
    }
  });
}

function populateLabels() {
  var liList = '';
  var count = 0;
  $.each(classesColors, function (key, val) {
    liList += '<li class="list-inline-item"><button type="button" style="background-color:' + val + ';" class="btn nodeBtn">' + key + '<i class="fa ' + 'fa-' + iconLabelMaps[key] + ' "></i></button></li>';
    count++;
  });
  $('.labelsList').empty().html(liList);
}

function auditContextMenuStart(auditInstName, cluster) {
  var auditType = auditInstName.split('_')[0];
  context.init({
    fadeSpeed: 100,
    above: 'auto',
    left: 'auto',
    preventDoubleContext: true,
    compress: true
  });
  context.attach('.node.auditorNode', [
    {
      text: 'Start Audit',
      action: function (e) {
        e.preventDefault();
        $.ajax({
          url: '/runauditor/',
          data: { "auditortype": auditType, "cluster": cluster },
          type: 'POST',
          cache: false,
          success: function (data) {
            //auditTableInit();
            calNeo4jGraph('KUBERNETES', '#neo4jd3');
            populateLabels();
          },
          error: function (xhr) { }
        });
      }
    },
    {
      text: 'View Report',
      action: function (e) {
        e.preventDefault();
        populateReport(cluster, auditType);
      }
    }
  ]);
}

function populateReport(cluster, auditType) {
  $.ajax({
    url: '/auditors/?reports=true&cluster=' + cluster + '&auditor_type=' + auditType,
    type: 'GET',
    cache: false,
    success: function (data) {
      var resp = data[0];
      $('#auditorReportModal').modal('show');
      $('.clusterName').text(resp.cluster);
      $('.auditorName').text(resp.auditor_type);
      var htmlStr = '';
      $.each(resp.audit_result, function (key, val) {
        var collapseHtml = '';
        $.each(val.items, function (k, value) {
          var tableStr = '';
          var theadStr = '';
          $.each(value.audit_issues, function (ind, term) {
            theadStr = '<tr class="tableHeading"><th colspan="2">' + value.objectName + '</th></tr>' + '<tr>' + '<th class="text-center">Criticality</th><th class="text-center">Description</th></tr>'
            tableStr += '<tr>' + '<td>' + term.criticality + '</td>' + '<td>' + term.description + '</td></tr>';
          });
          collapseHtml += '<table class="table table-hover table-bordered auditReportTable"><thead>' + theadStr + '</thead><tbody>' + tableStr + '</tbody></table>';
        });
        htmlStr += collapseHtml;
      });
      $('.reportList').empty().html(htmlStr);
      var d = new Date(0); // The 0 there is the key, which sets the date to the epoch
      d.setUTCSeconds(resp.timestamp);
      $('.timestampSpan').text(d);
    },
    error: function (xhr) { }
  });
}

