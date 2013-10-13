app.factory('contentFactory', function($http) {
    var rootUrl = '/rest/content';
    var factory = {};
    factory.getFrontPage = function() {
        return $http.get(rootUrl + '/topcontent');
    };
    factory.getNextContent = function(startIdx, endIdx) {
        return $http.get(rootUrl + '/topcontent', {
            params: {
                start_idx: startIdx,
                end_idx: endIdx
            }
        });
    };
    return factory;
});