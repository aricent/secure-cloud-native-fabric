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
var scrmApp = angular.module('scrmApp', ['ui.router', 'configuration']);

scrmApp.config(function ($stateProvider, $urlRouterProvider) {

	$urlRouterProvider.otherwise('/scrm/dashboard');

	$stateProvider

		// HOME STATES AND NESTED VIEWS ========================================
		.state('homeScrm', {
			url: '/scrm/dashboard',
			templateUrl: '../../static/mainContainer/crisp/dashboardCrisp.html'
		})
		.state('operations_mananagement', {
			url: '/scrm/operations_mananagement',
			templateUrl: '../../static/mainContainer/scrm/operationsManagement.html'
		})
		.state('policy_administration', {
			url: '/scrm/policy_administration',
			templateUrl: '../../static/mainContainer/scrm/policyAdministration.html'
		})

		.state('homeCrisp', {
			url: '/crisp/dashboard',
			templateUrl: '../../static/mainContainer/scrm/dashboardScrm.html'
		})
		.state('policyComplianceMapping', {
			url: '/crisp/policy_compliance_mapping',
			templateUrl: '../../static/mainContainer/crisp/complianceMapping.html'
		})
		.state('auditor_rules', {
			url: '/crisp/auditor_rules',
			templateUrl: '../../static/mainContainer/crisp/auditor_rules.html'
		});;

});

scrmApp.run(function ($transitions, $rootScope) {
	$transitions.onStart({}, function (trans) {
		$rootScope.showLoader = true;
	});
	$transitions.onSuccess({}, function () {
		$rootScope.showLoader = false;
	});
});

scrmApp.controller('crispWidgetController', function ($scope, URL) {
	$scope.pieUrl = URL.PIE;
	$scope.graphUrl = URL.GRAPH;
	$scope.gaugeUrl = URL.GAUGE;
});


