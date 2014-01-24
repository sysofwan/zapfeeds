app.factory('contentFactory', function($http, $cookieStore) {
    'use strict';
    var rootUrl = '/rest/content';
    var factory = {};

    var updatePageNo = function() {
        var page = $cookieStore.get('page') || 0;
        var history = $cookieStore.get('view_history') || [];
        if (history.length >= CONSTANTS.MAX_HISTORY()) {
            $cookieStore.put('page', ++page);
        } else {
            $cookieStore.put('page', 0);
        }
    };

    factory.getContents = function(callback) {
        updatePageNo();
        $http.get(rootUrl + '/topcontent')
            .success(function(contents) {
                callback(contents.results);
            })
            .error(function(errMsg) {
                console.log('Error with rest API: ' + errMsg);
            });
    };

    factory.filter = function(callback, page, filter) {
        var url = g.urlBuilder(rootUrl + '/filter/' + page, filter);
        $http.get(url)
            .success(function(result) {
                callback(result.results);
            })
            .error(function(errMsg) {
                console.log('Error with rest API:' + errMsg);
            });
    };

    return factory;
});

app.factory('contentMetaFactory', function($http) {
    'use strict';
    var rootUrl = '/rest/meta';
    var factory = {};

    factory.getAllTags = function(callback) {
        $http.get(rootUrl + '/alltags')
            .success(function(result) {
                callback(result.results);
            })
            .error(function(errMsg) {
                console.log('Error with rest API:' + errMsg);
            });
    };
    return factory;
});