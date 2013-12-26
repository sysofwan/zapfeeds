var app = angular.module('app', ['ngRoute', 'ngCookies', 'infinite-scroll']);

app.config(function($routeProvider) {
   $routeProvider
       .when('/', {
           controller: 'MainPageController',
           templateUrl: 'static/partials/cardView.html'
       })
       .when('/list', {
           controller: 'MainPageController',
           templateUrl: 'static/partials/listView.html'
       })
       .otherwise({redirectTo:'/'})
});
