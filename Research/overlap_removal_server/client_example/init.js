
// create an array with nodes
var nodes = new vis.DataSet([
    { id: 1, label: 'Node 1' },
    { id: 2, label: 'Node 2' },
    { id: 3, label: 'Node 3' },
    { id: 4, label: 'Node 4' },
    { id: 5, label: 'Node 5' },
    // { id: 7, label: 'square shape', shape: "square" },

    {
        id: 8,
        label: [
            "8 I'm an alligator,",
            "I'm a mama-papa coming for you.",
            "I'm the space invader,",
            "I'll be a rock 'n' rollin' bitch for you.",
        ].join("\n"),
        shape: "box",
        // x: 0,
        // y: 0,
    },
    {
        id: 9,
        font: { multi: true },
        label:
            "9 <b>This</b> is a\n<i>default</i> <b><i>multi-</i>font</b> <code>label</code>",
        // x: -40,
        // y: -40,
        shape: "box",
    },
    {
        id: 10,
        font: { multi: "md", face: "georgia" },
        label: "10 *This* is a\n_markdown_ *_multi-_ font* `label`",
        // x: 120,
        // y: 120,
        shape: "box",
    },

    // {
    //   id: 37,
    //   label: "FIELD---my value",
    //   shape: "custom",
    //   group: "a",
    //   ctxRenderer: ({
    //     ctx,
    //     x,
    //     y,
    //     state: { selected, hover },
    //     style,
    //     label,
    //   }) => {
    //     const splittedLabel = label.split("---");
    //     ctx.save();
    //     ctx.restore();
    //     const labelText = splittedLabel[0];
    //     const valueText = splittedLabel[1];
    //     const r = 5;

    //     const labelWidth = ctx.measureText(labelText).width;
    //     const valueWidth = ctx.measureText(valueText).width;

    //     const wPadding = 10;
    //     const hPadding = 10;

    //     const w = 200;
    //     const h = 60;
    //     const drawNode = () => {
    //       const r2d = Math.PI / 180;
    //       if (w - 2 * r < 0) {
    //         r = w / 2;
    //       } //ensure that the radius isn't too large for x
    //       if (h - 2 * r < 0) {
    //         r = h / 2;
    //       } //ensure that the radius isn't too large for y

    //       const top = y - h / 2;
    //       const left = x - w / 2;

    //       ctx.lineWidth = 2;
    //       ctx.beginPath();
    //       ctx.moveTo(left + r, top);
    //       ctx.lineTo(left + w - r, top);
    //       ctx.arc(left + w - r, top + r, r, r2d * 270, r2d * 360, false);
    //       ctx.lineTo(left + w, top + h - r);
    //       ctx.arc(left + w - r, top + h - r, r, 0, r2d * 90, false);
    //       ctx.lineTo(left + r, top + h);
    //       ctx.arc(left + r, top + h - r, r, r2d * 90, r2d * 180, false);
    //       ctx.lineTo(left, top + r);
    //       ctx.arc(left + r, top + r, r, r2d * 180, r2d * 270, false);
    //       ctx.closePath();
    //       ctx.save();
    //       ctx.fillStyle = style.color || "#56CCF2";
    //       ctx.fill();
    //       ctx.strokeStyle = "#FFFFFF";
    //       ctx.stroke();

    //       // label text
    //       ctx.font = "normal 12px sans-serif";
    //       ctx.fillStyle = "grey";
    //       ctx.textAlign = "center";
    //       ctx.textBaseline = "middle";
    //       const textHeight1 = 12;
    //       ctx.fillText(
    //         labelText,
    //         left + w / 2,
    //         top + textHeight1 + hPadding,
    //         w
    //       );

    //       // value text
    //       ctx.font = "bold 14px sans-serif";
    //       ctx.fillStyle = "black";
    //       const textHeight2 = 12;

    //       ctx.fillText(
    //         valueText,
    //         left + w / 2,
    //         top + h / 2 + hPadding,
    //         w
    //       );
    //     };

    //     ctx.save();
    //     ctx.restore();
    //     return {
    //       drawNode,
    //       nodeDimensions: { width: w, height: h },
    //     };
    //   },
    // },


]);

// create an array with edges
var edges = new vis.DataSet([
    { from: 1, to: 3 },
    { from: 1, to: 2 },
    { from: 2, to: 4 },
    { from: 2, to: 5 },
    { from: 3, to: 3 },

    // { from: 7, to: 37 },
    // { from: 7, to: 1 },

    // { from: 1, to: 9 },
    { from: 8, to: 9 },
    { from: 9, to: 10 },
]);


// Testing 2 - simpleExample
let simpleExample = false
if (simpleExample) {

    var nodes = new vis.DataSet([
        { id: 1, label: 'Node 1' },
        { id: 2, label: 'Node 2' },
    ])
    // create an array with edges
    var edges = new vis.DataSet([
    ]);
}

if (drawCartesianGrid) {

    var nodes = new vis.DataSet([
        { id: 1, label: '0,0' },
        { id: 2, label: '0,50' },
        { id: 3, label: '0,-50' },
        { id: 4, label: '50,0' },
        { id: 5, label: '-50,0' },
    ])
    var edges = new vis.DataSet([]);
}


// create a network
var container = document.getElementById('mynetwork');
var data = {
    nodes: nodes,
    edges: edges
};

var options = {
    interaction: {
        hover: true
    },
    manipulation: {
        addNode: function (nodeData, callback) {
            nodeData.label = 'hello world';
            callback(nodeData);
        },
        editNode: function (nodeData, callback) {
            // var r = confirm("Do you want to connect the node to itself?");
            var r = prompt("Please enter your name", "Harry Potter");
            nodeData.label = r;
            callback(nodeData);
        },
        controlNodeStyle: {
            borderWidth: 2,
            borderWidthSelected: 2
        }
    },

    // avoid overlap - but can cause constantly drifting nodes e.g. setting of 1 or even 0.6 - or sadly even 0.5
    physics: {
        barnesHut: {
            // springConstant: 0,
            avoidOverlap: 0.2
        }
    },

    // display interactive graph adjustment UI
    // configure: {
    //   enabled: true,
    //   showButton: true
    // },

    nodes: {
        shape: "box",
    },

    // if your data is not hierarchical then don't use this - cos a miswiring can send the algorithm nuts
    // layout: {
    //   hierarchical: {
    //     levelSeparation: 150, treeSpacing: 200, blockShifting: true, edgeMinimization: true, parentCentralization: true, direction: 'UD', nodeSpacing: 300, sortMethod: "directed" //directed,hubsize 
    //   }
    // }

};
if (drawCartesianGrid) {
    options.physics = false
}

// options.physics = false

var network = new vis.Network(container, data, options);

if (drawCartesianGrid) {
    network.moveNode(1, 0, 0)
    network.moveNode(2, 0, 50)
    network.moveNode(3, 0, -50)
    network.moveNode(4, 50, 0)
    network.moveNode(5, -50, 0)
}
