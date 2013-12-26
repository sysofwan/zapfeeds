app.factory('contentFactory', function($http, $cookieStore) {
    var rootUrl = '/rest/content';
    var factory = {};
    var contentCache;
    var page = $cookieStore.get('page') || 0;

    var updatePageNo = function() {
        var history = $cookieStore.get('view_history') || [];
        if (history.length > CONSTANTS.MAX_HISTORY()) {
            $cookieStore.put('page', ++page);
            console.log(page);
        }
    };

    factory.getContents = function(callback, forceRefresh) {
        forceRefresh = forceRefresh || false;

        if (!contentCache || forceRefresh) {
            updatePageNo();
            $http.get(rootUrl + '/topcontent')
                .success(function(contents) {
                    contentCache = contents.results;
                    callback(contentCache);
                })
                .error(function(errMsg) {
                    console.log('Error with rest API: ' + errMsg)
                });
        }
        else {
            callback(contentCache);
        }
    };
    return factory;
});