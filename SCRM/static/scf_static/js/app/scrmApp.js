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


