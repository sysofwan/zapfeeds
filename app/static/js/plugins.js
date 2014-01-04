// Avoid `console` errors in browsers that lack a console.
/* jshint undef: true, unused: false */
/* global g: true */
(function() {
    'use strict';
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

//  Extends Date object to make fetching date and time easier.
//  For today's date;
Date.prototype.today = function(){
    'use strict';
    return ((this.getDate() < 10)?"0":"") + this.getDate() +"/"+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"/"+ this.getFullYear();
};
//  For the time now
Date.prototype.timeNow = function(){
    'use strict';
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
};

//  Global object for custom functions, etc
var g = (function() {
    'use strict';
    var lib = {};
    function forEachSorted(obj, iterator, context) {
        var keys = sortedKeys(obj);
        for (var i = 0; i < keys.length; i++) {
            iterator.call(context, obj[keys[i]], keys[i]);
        }
        return keys;
    }

    function sortedKeys(obj) {
        var keys = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                keys.push(key);
            }
        }
        return keys.sort();
    }

    function buildUrl(url, params) {
        if (!params) {
            return url;
        }
        var parts = [];
        forEachSorted(params, function (value, key) {
            if (value === null || value === undefined) {
                return;
            }
            if (angular.isObject(value)) {
                value = angular.toJson(value);
            }
            parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
        });
        return url + ((url.indexOf('?') === -1) ? '?' : '&') + parts.join('&');
    }

    lib.urlBuilder = function(url, params) {
        return buildUrl(url, params);
    };
    return lib;
})();

// Place any jQuery/helper plugins in here.
