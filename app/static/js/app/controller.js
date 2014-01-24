app.controller('MainController', function($scope, $cookieStore, $location) {
    'use strict';
    var templateUrlGenerator = function() {
        var preferred = $cookieStore.get('view');
        if (preferred && preferred === 'list') {
            $scope.list = true;
            return '/static/partials/listView.html';
        }
        $scope.list = false;
        return '/static/partials/cardView.html';
    };

    $scope.query = null;

    $scope.templateUrl = templateUrlGenerator();

    $scope.setView = function(type) {
        $cookieStore.put('view', type);
        $scope.templateUrl = templateUrlGenerator();
    };

    $scope.tagSearch = function() {
        $location.url('/filter/?tag=' + $scope.query);
    };

    $scope.textSearch = function() {
        $location.url('/filter/?query=' + $scope.query);
    };
});

app.controller('ContentController', function($scope, contentFactory) {
    'use strict';
    $scope.contents = [];
    var lastUpdate = (new Date()).getTime();

    var loadContents = function() {
        $scope.updating = true;
        contentFactory.getContents(function(results) {
            $scope.contents = $scope.contents.concat(results);
            $scope.updating = false;
        });
    };

    $scope.loadMore = function() {
        var currTime = (new Date()).getTime();

        if (currTime - CONSTANTS.MILLISECONDS_BEFORE_NEXT_REQUEST() > lastUpdate) {
            lastUpdate = currTime;
            loadContents();
        }
    };

    loadContents();
});

app.controller('FilterController', function($scope, contentFactory, $routeParams) {
    'use strict';
    var page = 0;
    var lastPage = false;
    var type = $routeParams.type;
    var tag = $routeParams.tag;
    var query = $routeParams.query;
    $scope.contents = [];
    var lastUpdate = (new Date()).getTime();

    var loadContents = function() {
        $scope.updating = true;
        ++page;
        contentFactory.filter(function(results) {
            $scope.updating = false;
            if (!results.length) {
                lastPage = true;
                return;
            }
            $scope.contents = $scope.contents.concat(results);
        }, page, {tag: tag, type: type, query:query});
    };

    $scope.loadMore = function() {
        var currTime = (new Date()).getTime();

        if (currTime - CONSTANTS.MILLISECONDS_BEFORE_NEXT_REQUEST() > lastUpdate && !lastPage) {
            lastUpdate = currTime;
            loadContents();
        }
    };
    loadContents();
});
