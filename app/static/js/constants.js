/**
 * Created by sysofwan on 12/24/13.
 */

var CONSTANTS = (function() {
    var max_history = 360;
    var milliseconds_before_next_request = 3000;
    return {
        MAX_HISTORY: function() {return max_history;},
        MILLISECONDS_BEFORE_NEXT_REQUEST: function() {
            return milliseconds_before_next_request;
        }
    };
})();
