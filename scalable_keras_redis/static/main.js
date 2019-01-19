(function () {

  'use strict';

  angular.module('BrandSafetyApp', [])
  .controller('BrandSafetyController', ['$scope', '$log', '$http', '$timeout', '$interval',
    function($scope, $log, $http, $timeout, $interval) {

    $scope.submitButtonText = 'Submit';
    $scope.loading = false;    
    $scope.urlerror = false;    
    $scope.conclusion = false;
    $scope.showResultPanel = false;
    var default_info = 'Spent 0 seconds';
    $scope.checkInterval = default_info;
    var terminate = false;
    $scope.getResults = function() {

      $log.log('test');

      // get the URL from the input
      var userInput = $scope.url;
      var includeGambling = $scope.includeGambling;
      var includeAlcohol = $scope.includeAlcohol;
      var includeNudity = $scope.includeNudity;
      var runImage = $scope.runImage;
      var runText = $scope.runText;
      $scope.showResultPanel = true;
      $scope.results = null;
      $scope.loading = true;
      $scope.submitButtonText = 'Analyzing...';
      $scope.urlerror = false;
      $scope.conclusion = false;
	  
	  $scope.textalcohol = -1;
      $scope.textgambling = -1;
      $scope.textnudity = -1;
      
	  if(runText=='yes'){
		  $http({method : 'GET', url: 'http://ec2-18-236-117-209.us-west-2.compute.amazonaws.com:5001/alcohol?url=' + $scope.url})
      .then(function successCallback(response){
          var data = response.data;
          $log.log(data);
          $scope.textalcohol = (1-data.combine_score).toPrecision(3);
      }, function errorCallback(response){
        $log.log(response);
      });
	  }
      

      
      var index = 0;
//      $scope.checkInterval = index.toString();
      var promise = $interval(callAtinterval, 1000);
      
      $http({method : 'POST', url: '/predict', data : {'website' : userInput, 'runImage': runImage, 'runText': runText, 'includeGambling' : includeGambling, 'includeAlcohol' : includeAlcohol, 'includeNudity' : includeNudity}})
      .then(function successCallback(response){
    	  $log.log(results);
    	  $interval.cancel(promise);
    	  $timeout(callAtTimeout, 500);
    	  $http({method : 'POST', url: '/finalresults', data:{'website_folder' : response.data['website_folder'], 'runImage': $scope.runImage, 'runText': $scope.runText}})
          .then(function successCallback(response){
        	$scope.conclusion = true;
        	$scope.finalResults = response.data;
          });
      }, function errorCallback(response){
    	  $log.log(response);
      });
    $scope.checkInterval = default_info;
      function callAtTimeout(){    	  
    	  getBrandSafety(userInput, includeGambling, includeAlcohol, includeNudity, true);
      }
      
      function callAtinterval() {
    	  index +=1;
    	  $scope.checkInterval = "Spent " + index.toString() + " seconds";
    	  if(index % 2 ==0){
    		  getBrandSafety(userInput, includeGambling, includeAlcohol, includeNudity, false);
    	  }      	
      }
      
    };
    
    

    function getBrandSafety(userInput, includeGambling, includeAlcohol, includeNudity, reset) {

      var timeout = '';

      var poller = function() {
        // fire another request
        $http({method : 'POST', url: '/result', data:{'web' : userInput, 'includeGambling' : includeGambling, 'includeAlcohol' : includeAlcohol, 'includeNudity' : includeNudity}})
        .then(function successCallback(response){
        	  $scope.loading = !reset;
              $scope.submitButtonText = reset ? "Submit" : "Analyzing...";
              $scope.results = null;
              $scope.results = response.data;
              $scope.urlerror = false;
        }, function errorCallback(response){
      	  $log.log(response);
        }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            
          );
      };

      poller();

    }

  }])

}());