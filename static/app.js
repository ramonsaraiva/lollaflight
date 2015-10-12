'use strict';

var app = angular.module('app', [
	'ngRoute',
	'controllers',
	'services'
]);

app.config(['$routeProvider', function($routeProvider) {
	$routeProvider
		.when('/home/', {
			templateUrl: 'partials/home.tpl.html',
			controller: 'home_controller'
		})
		.when('/', {
			redirectTo: '/home/'
		})
		.otherwise({
			redirectTo: '/home/'
		});
}]);
