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
angular.module('configuration', [])
    .constant("URL", (function () {
        return {
            GRAPH: "http://172.16.141.14:8601/app/kibana#/visualize/edit/60c53300-8e7e-11e8-b8af-93be2ebb3ebd?embed=true&_g=(refreshInterval:('$$hashKey':'object:1283',display:'5+seconds',pause:!t,section:1,value:5000),time:(from:now-15m,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(language:lucene,query:''),uiState:(vis:(legendOpen:!f)),vis:(aggs:!((enabled:!t,id:'1',params:(),schema:metric,type:count),(enabled:!t,id:'2',params:(field:balance,missingBucket:!f,missingBucketLabel:Missing,order:desc,orderBy:'1',otherBucket:!f,otherBucketLabel:Other,size:15),schema:segment,type:terms)),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!f,categoryAxes:!((id:CategoryAxis-1,labels:(filter:!f,rotate:0,show:!t,truncate:100),position:bottom,scale:(type:linear),show:!t,style:(),title:(),type:category)),grid:(categoryLines:!t,style:(color:%23eee),valueAxis:!n),legendPosition:right,seriesParams:!((data:(id:'1',label:Count),drawLinesBetweenPoints:!t,interpolate:linear,mode:normal,show:true,showCircles:!t,type:area,valueAxis:ValueAxis-1)),times:!(),type:area,valueAxes:!((id:ValueAxis-1,labels:(filter:!f,rotate:0,show:!t,truncate:100),name:LeftAxis-1,position:left,scale:(defaultYExtents:!f,mode:normal,setYExtents:!f,type:linear),show:!t,style:(),title:(text:Count),type:value))),title:Balance-Count,type:area))",

            GAUGE: "http://172.16.141.14:8601/app/kibana#/visualize/edit/0a33b8c0-8e80-11e8-b8af-93be2ebb3ebd?embed=true&_g=(refreshInterval:('$$hashKey':'object:1283',display:'5+seconds',pause:!t,section:1,value:5000),time:(from:now-15m,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(language:lucene,query:''),uiState:(vis:(defaultColors:('0+-+50':'rgb(0,104,55)','50+-+75':'rgb(255,255,190)','75+-+100':'rgb(165,0,38)'),legendOpen:!f)),vis:(aggs:!((enabled:!t,id:'1',params:(),schema:metric,type:count)),params:(addLegend:!t,addTooltip:!t,gauge:(backStyle:Full,colorSchema:'Green+to+Red',colorsRange:!((from:0,to:50),(from:50,to:75),(from:75,to:100)),extendRange:!t,gaugeColorMode:Labels,gaugeStyle:Full,gaugeType:Arc,invertColors:!f,labels:(color:black,show:!t),orientation:vertical,percentageMode:!f,scale:(color:%23333,labels:!f,show:!t),style:(bgColor:!f,bgFill:%23eee,bgMask:!f,bgWidth:0.9,fontSize:60,labelColor:!t,mask:!f,maskBars:50,subText:'',width:0.9),type:meter,verticalSplit:!f),isDisplayWarning:!f,type:gauge),title:Events-Count,type:gauge))",

            PIE: "http://172.16.141.14:8601/app/kibana#/visualize/edit/df3d4f70-8e82-11e8-b8af-93be2ebb3ebd?embed=true&_g=(refreshInterval:('$$hashKey':'object:1283',display:'5+seconds',pause:!t,section:1,value:5000),time:(from:now-15m,mode:quick,to:now))&_a=(filters:!(),linked:!f,query:(language:lucene,query:''),uiState:(vis:(colors:('39':%233F6833),legendOpen:!f)),vis:(aggs:!((enabled:!t,id:'1',params:(),schema:metric,type:count),(enabled:!t,id:'2',params:(field:age,missingBucket:!f,missingBucketLabel:Missing,order:desc,orderBy:'1',otherBucket:!f,otherBucketLabel:Other,size:5),schema:segment,type:terms)),params:(addLegend:!t,addTooltip:!f,isDonut:!f,labels:(last_level:!f,show:!f,truncate:200,values:!t),legendPosition:right,type:pie),title:'Age-Pie+Chart',type:pie))"
        }
    })());
