/**
 * Created by sysofwan on 12/22/13.
 */

app.directive('trackHistory', function($document, $cookieStore) {
    "use strict";
    var lastIdx = 0;
    var maxCookie = false;

    var link = function(scope, element, attrs) {
        var rawElt = element[0];
        var seenElt;

        var updateSeen = function() {
            var content = $('.content');

            var heightPerContent = content.height();
            var widthPerContent = content.width();
            var contentContainerWidth = rawElt.clientWidth;
            var contentsPerRow = Math.floor(contentContainerWidth/widthPerContent);
            var seenHeight = screen.height + $document[0].body.scrollTop;
            var numEltSeen = Math.floor(seenHeight/heightPerContent) * contentsPerRow;

            for (; lastIdx < numEltSeen && lastIdx < scope.contents.length; ++lastIdx) {
                seenElt.push(scope.contents[lastIdx].id);
            }
            $cookieStore.put('view_history', seenElt);
        };

        var updateMaxCookie = function() {
            maxCookie = seenElt.length >= CONSTANTS.MAX_HISTORY();
        };

        var updateSeenElt = function() {
            seenElt = $cookieStore.get('view_history') || [];
        };

        $($document).on('scroll', function() {
            updateSeenElt();
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
    "use strict";
    var link = function(scope, element, attrs) {
        var imgUrl;

        var showImgOnLoad = function() {
             $('<img>').attr('src', function() {
                return imgUrl;
            }).on('load', function() {
                element.css('background-image', 'url(' + imgUrl + ')');
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

/*app.directive('infiniteScroll', function($window, $document) {
    var link = function(scope, element, attr) {
        $window = $($window);
        element = $(element[0]);

        $document.on('scroll', function() {
            if ($window.scrollTop() + $window.height() >= element.height()) {
                scope.$apply(attr.infiniteScroll)
            }
        });
    };
    return {
        link: link
    };
});*/
