/**
 * Created by sysofwan on 12/22/13.
 */

app.directive('trackHistory', function($document, $cookieStore) {
    var lastIdx = 0;
    var maxCookie = false;

    var link = function(scope, element, attrs) {
        var rawElt = element[0];
        var seenElt = $cookieStore.get('view_history') || [];

        var updateSeen = function() {
            var content = $('.content');

            var heightPerContent = content.height();
            var widthPerContent = content.width();
            var contentContainerWidth = rawElt.clientWidth;
            var contentsPerRow = Math.floor(contentContainerWidth/widthPerContent);
            var seenHeight = screen.height + $document[0].body.scrollTop;
            var numEltSeen = Math.floor(seenHeight/heightPerContent) * contentsPerRow;

            for (; lastIdx < numEltSeen && lastIdx < scope.contents.length; ++lastIdx) {
                seenElt.push(scope.contents[lastIdx]['id']);
            }
            $cookieStore.put('view_history', seenElt);
        };

        var updateMaxCookie = function() {
            if (seenElt.length >= CONSTANTS.MAX_HISTORY()) {
                maxCookie = true;
            }
        };

        $($document).on('scroll', function() {
            updateMaxCookie();
            if (!maxCookie) {
                updateSeen();
            }
        });
    };

    return {
        link : link
    };
});

app.directive('imgFadeIn', function() {
    console.log('called');
    var link = function(scope, element, attrs) {
        var imgUrl;

        var showImgOnLoad = function() {
             $('<img>').attr('src', function() {
                return imgUrl;
            }).on('load', function() {
                element.addClass('make_opaque');
            });
        };
        scope.$watch(attrs.imgFadeIn, function(value) {
            imgUrl = value;
            showImgOnLoad();
        });
    };
    return {
        link: link
    };
});
