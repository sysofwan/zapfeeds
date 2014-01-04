/* global app: true */
var app = angular.module('app', ['ngRoute', 'ngCookies', 'ngAnimate', 'infinite-scroll', 'ui.bootstrap']);

app.config(function($routeProvider, $locationProvider) {
    'use strict';

   $routeProvider
       .when('/', {
           controller: 'ContentController',
           templateUrl: '/static/partials/main.html'
       })
       .when('/filter/', {
           controller: 'FilterController',
           templateUrl: '/static/partials/main.html'
       })
       .otherwise({redirectTo:'/'});

    $locationProvider.html5Mode(true).hashPrefix('!');
});
