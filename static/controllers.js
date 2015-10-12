'use strict';

var controllers = angular.module('controllers', []);

controllers.controller('home_controller', function($scope, $http, spinner) {
	$scope.data = [];
	$scope.spinner = new spinner();

	$scope.check = function()
	{
		$scope.spinner.start();
		
		$http.post('/check/')
			.success(function(data) {
				$scope.data.unshift(data);
				$scope.spinner.stop();
			})
			.error(function(err) {
				console.log(err);
				$scope.spinner.stop();
			});
	}

	$scope.spinner.start();

	$http.get('/surveys/')
		.success(function(data) {
			$scope.data = data;
			$scope.spinner.stop();
		})
		.error(function(err) {
			console.log(err);
			$scope.spinner.stop();
		});
});
