$(document).ready(function () {

    // Simple click detection
    network.on('clickXX', function (properties) {
        alert('clicked node ' + properties.nodes);
    });

    // Works - pops up a prompt
    network.on("doubleClickXX", function (params) {
        // params.event = "[original event]";
        let nodeId = params.nodes[0]
        let label = nodes.get(nodeId).label

        console.log(nodes.get(nodeId).size)

        // window.open("/myurl/?id="params.nodes[0], '_blank');
        // alert("/myurl/?id=" + params.nodes[0], '_blank');
        var person = prompt("Please enter node info", label);
        if (person != null) {
            // var newColor = '#' + Math.floor((Math.random() * 255 * 255 * 255)).toString(16);
            // console.log(newColor)
            // nodes.update([{id:1, color:{background:newColor}}]);
            // nodes.update({ id: params.nodes[0], label: person, color: { background: newColor } });
            nodes.update({ id: nodeId, label: person });
            nodes.update({ id: nodeId, size: 50 }); // only works on square shape cos others depend on text inside it

        }
    });

    // works well, uses help from jquery
    // https://stackoverflow.com/questions/48150985/vis-js-network-fixed-position-for-tooltip-popup
    network.on('clickXX', function (properties) {
        var nodeID = properties.nodes[0];
        if (nodeID) {

            var sNodeLabel = this.body.nodes[nodeID].options.label
            var sToolTip = this.body.nodes[nodeID].options.title;

            //use JQUERY to see where the canvas is on the page.
            var canvasPosition = $('.vis-network').position();

            //the properties give x & y relative to the edge of the canvas, not to the whole document.
            var clickX = properties.pointer.DOM.x + canvasPosition.top;
            var clickY = properties.pointer.DOM.y + canvasPosition.left;

            //make sure we have a valid div, either clear it or generate one.
            if ($('#cellBatchAttrPopUp').length) {
                $('div#cellBatchAttrPopUp').empty();
            }
            else {
                $('<div id="cellBatchAttrPopUp"></div>').click(function () {
                    //clicking the popup hides it again.
                    $(this).empty().hide();
                }).css('position', 'absolute').appendTo("body");
            }

            // put the div over the node, display the tooltip and show it.
            $('div#cellBatchAttrPopUp').append(sNodeLabel)
                .append('<br/>')
                .append(sToolTip)
                .css('top', clickY).css('left', clickX)
                .show();

        }
    });

    // works ok too, needs work to change the popup label content
    // https://stackoverflow.com/questions/58251051/vis-js-network-incorrect-node-coordinates-with-getpositions
    network.on("clickXX", function (params) {
        // Get the node ID
        var nodeId = params.nodes[0];
        if (nodeId) {
            // Get the node title to show in the popup
            var popup = this.body.nodes[nodeId].options.title;

            // Get the node coordinates
            var { x: nodeX, y: nodeY } = network.canvasToDOM(
                network.getPositions([nodeId])[nodeId]
            );

            // andy inserted
            //make sure we have a valid div, either clear it or generate one.
            if ($('#popup').length) {
                // $('div#popup').empty(); // should set the contents accordingly - andy
            }
            else {
                $('<div id="popup">aaa</div>').click(function () {
                    //clicking the popup hides it again.
                    $(this).empty().hide();
                }).css('position', 'absolute').appendTo("body");
            }
            /// END


            // Show the tooltip in a div
            document.getElementById("popup").style.display = "block";
            // Place the div
            document.getElementById("popup").style.position = "absolute";
            document.getElementById("popup").style.top = nodeY + "px";
            document.getElementById("popup").style.left = nodeX + "px";
        }
    });


})
