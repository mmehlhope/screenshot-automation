var WebPage = require('webpage'),
    page    = WebPage.create();

page.onError = function(msg, trace) {
    var msgStack = ['ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
        });
    }
    // uncomment to log into the console
    // console.error(msgStack.join('\n'));
};

module.exports = page;