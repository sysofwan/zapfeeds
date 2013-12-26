app.controller('MainPageController', function($window, $scope, $cookieStore, contentFactory) {
    $scope.contents = [];
    var page = 0;
    var lastUpdate = (new Date()).getTime();

    $scope.loadContents = function(forceReload) {
        contentFactory.getContents(function(results) {
            $scope.contents = $scope.contents.concat(results);
        }, forceReload);
    };

    $scope.loadMore = function() {
        var currTime = (new Date()).getTime();

        if (currTime - CONSTANTS.MILLISECONDS_BEFORE_NEXT_REQUEST() > lastUpdate) {
            lastUpdate = currTime;
            $scope.loadContents(true);
        }
    };
    $scope.loadContents();
});
