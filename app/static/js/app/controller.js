app.controller('MainPageController', function($scope, contentFactory) {
    $scope.contents = [];
    var endIdx;

    init();

    function init() {
        contentFactory.getFrontPage()
            .success(function(content) {
                $scope.contents = $scope.contents.concat(content.results);
                console.log($scope.contents);
                endIdx = content.endIdx;
            })
            .error(function(errMsg) {
                console.log('Error with rest API: ' + errMsg)
            });
    }
});
