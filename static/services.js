'use strict';

var services = angular.module('services', []);

services.factory('Flight', function($http, $q) {
});

services.factory('spinner', function() {
	function spinner()
	{
		this.spinning = false;
		$('.spin').append(new Spinner(spinner_options).spin().el);
	}

	spinner.prototype.start = function() {
		this.spinning = true;
	};

	spinner.prototype.stop = function() {
		this.spinning = false;
	};

	return spinner;
});
