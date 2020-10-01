/*Yes it is possible, though not documented. What you have to do is to fetch the original JavaScript event. Once you have it, you can deploy the usual tricks.
For a click event, as declared by, say network.on('click', function(e) {...}); you reach the original event with let oEvent = e.event.srcEvent;
Then you can test for oEvent.shiftKey, etc. within the callback.
This works also for doubleClick. Note that for hover events you access the original JS event with let oEvent = e.event; (no srcEvent).
In case of doubt, just open the JS console in your browser and explore e data structure.
By the way, I'd also like to recommend this post on how to decipher a click from a doubleClick in vis.js, as a doubleClick also triggers a click! I've included it in the following snippet.
Summary:
*/
/* DECLARING EVENTS */
network.on('doubleClick', function (e) { onDoubleClick(e) });
network.on('click', function (e) { onClick(e) });
network.on('hoverNode', function (e) { doOnHoverNode(e) });
network.on('blurNode', function (e) { doOnBlurNode(e) });
/* MANAGING DOUBLE VS SINGLE CLICK */
let doubleClickTime = 0;
const threshold = 200;
function onClick(e) {
    const t0 = new Date();
    if (t0 - doubleClickTime > threshold) {
        setTimeout(function () {
            if (t0 - doubleClickTime > threshold) {
                doOnClick(e);
            }
        }, threshold);
    }
}
function onDoubleClick(e) {
    doubleClickTime = new Date();
    doOnDoubleClick(e)
}
/* DEFINE CALLBACKS HERE */
function doOnClick(e) {
    // fetch id of node clicked upon
    let nodeId = e.nodes[0];
    // fetch original JS event
    let jsEvent = e.event.srcEvent;
    // match modifiers
    let shift = jsEvent.shiftKey;
    let alt = jsEvent.altKey;
    let meta = jsEvent.metaKey;
    // do callback
    if (meta) {
        if (shift) {
            // do stuff
        }
        else {
            // do stuff
        }
    }
    function doOnDoubleClick(e) {
        // don't delete the following line!
        doubleClickTime = new Date();
        // the rest just like click
        function doOnHoverNode(e) {
            // fetch id of node clicked upon
            let nodeId = e.nodes[0];
            // fetch original JS event
            let jsEvent = e.event;
            // the rest just like click
        }
        function doOnBlurNode(e) {
            // ditto doOnHoverNode
        }
    }
}

//Hope this helps.
