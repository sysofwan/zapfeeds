/**
 * Created by sysofwan on 12/24/13.
 */
/* jshint undef: true, unused: false */
/* global CONSTANTS: true */
var CONSTANTS = (function() {
    "use strict";
    var maxHistory = 360;
    var millisecondsBeforeNextRequest = 1500;
    return {
        MAX_HISTORY: function() {return maxHistory;},
        MILLISECONDS_BEFORE_NEXT_REQUEST: function() {
            return millisecondsBeforeNextRequest;
        }
    };
})();
