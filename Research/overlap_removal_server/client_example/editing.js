$(document).ready(function () {


    // my attempt at in place editing

    lastEditedNodeId = undefined;

    network.on("clickXXInplaceEdit", function (params) {
        // Get the node ID
        var nodeId = params.nodes[0];

        // save the last edit session value
        if (!nodeId && lastEditedNodeId) {
            let lastEditedNodeCurrentValue = this.body.nodes[lastEditedNodeId].options.label  // not just nodes[]
            let lastTextEditValue = $('#popup').val()
            if (lastEditedNodeCurrentValue != lastTextEditValue) {
                console.log(`updating node ${lastEditedNodeId} with value ${lastTextEditValue}`)
                nodes.update({ id: lastEditedNodeId, label: lastTextEditValue });
            }
        }

        // remember
        lastEditedNodeId = nodeId

        if (nodeId) {
            // Get the node title to show in the popup
            // var popup = this.body.nodes[nodeId].options.title; // undefined
            var label = this.body.nodes[nodeId].options.label;
            // console.log(`popup=${popup} label=${label}`)

            // Get the node coordinates nodeX, nodeY - translated into DOM coordinates (not accounting for visjs area offset)
            var { x: nodeX, y: nodeY } = network.canvasToDOM(network.getPositions([nodeId])[nodeId]);
            // console.log(nodeX, nodeY)

            // Get the node bounds nodeLeft, nodeTop, nodeRight, nodeBottom
            let boundsNode = network.getBoundingBox(nodeId)
            var { x: nodeLeft, y: nodeTop } = network.canvasToDOM({ x: boundsNode.left, y: boundsNode.top })
            var { x: nodeRight, y: nodeBottom } = network.canvasToDOM({ x: boundsNode.right, y: boundsNode.bottom })
            // console.log(bounds, nodeLeft, nodeTop, nodeRight, nodeBottom)

            // Calculate nodeWidth, nodeHeight - or should this be done after the translation into DOM coords? No!
            // TODO Need to clip to visjs bounding area 
            let nodeWidth = nodeRight - nodeLeft
            let nodeHeight = nodeBottom - nodeTop

            // adjust all node coords to be relative to visjs area
            var rect = document.getElementById("mynetwork").getBoundingClientRect();
            // console.log(rect.top, rect.right, rect.bottom, rect.left);
            nodeTop += rect.top
            nodeLeft += rect.left


            // andy inserted
            //make sure we have a valid div, either clear it or generate one.
            if ($('#popup').length) {
                // $('div#popup').empty(); // should set the contents accordingly - andy

            }
            else {
                // $('<div id="popup">aa</div>').click(function () {
                $('<textarea id="popup">aa</textarea>').click(function () {
                    //clicking the popup hides it again.
                    // $(this).empty().hide();

                }).css('position', 'absolute').appendTo("body");
            }
            $('#popup').val(label)
            /// END


            // Show the tooltip in a div
            // document.getElementById("popup").style.display = "block";
            // Place the div
            // document.getElementById("popup").style.position = "absolute";

            // works ok - remember to scroll up to see it if you need to
            // document.getElementById("popup").style.top = 0 + "px";
            // document.getElementById("popup").style.left = 0 + "px";

            // works ok
            // document.getElementById("popup").style.top = nodeY + "px";
            // document.getElementById("popup").style.left = nodeX + "px";

            document.getElementById("popup").style.top = nodeTop + "px";
            document.getElementById("popup").style.left = nodeLeft + "px";
            // adjust size of this div
            document.getElementById("popup").style.width = nodeWidth + "px";
            document.getElementById("popup").style.height = nodeHeight + "px";
            document.getElementById("popup").style.display = "block"

        }
        else {
            console.log('nothing clicked on?')
            document.getElementById("popup").style.display = "none"
        }
    });


})
