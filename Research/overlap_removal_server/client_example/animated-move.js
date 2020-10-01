
let timer = null
let animatedMove = true

function moveNodeAnimated(node_ids, from_positions, to_positions) {
    console.log('moveNodeAnimated called', node_ids, from_positions, to_positions)
    if (!animatedMove) {
        // old jumping version
        let id = node_ids[0]
        // for .... TODO need to loop and do multiple moves
        network.moveNode(id, to_positions[id].x, to_positions[id].y)
        return
    }
    if (timer != null) {
        console.log('ABORT ANIMATION - timer still running on an old animation job!')

        // old jumping version
        let id = node_ids[0]
        network.moveNode(id, to_positions[id].x, to_positions[id].y)
        return
    }
    // old jumping version
    // let id = node_ids[0]
    // network.moveNode(id, to_positions[id].x, to_positions[id].y)
    // return

    // var k = 0, lambda = 0, tick = 10, totalTime = 500;
    var k = 0, lambda = 0, tick = 10, totalTime = 200;

    // toy example start x, y coordinates nodes
    // var x_start = 0, y_start = 0

    // nr of steps, given tick time and total animation time
    var nrOfSteps = Math.floor(totalTime / tick);

    // perform moveNode every tick nr of milliseconds
    timer = setInterval(function () {
        console.log('tick - animating', node_ids)

        // iteration counter
        k++;

        // lambda (for convex combination)
        var l = k / nrOfSteps;
        // let failsafe = 20

        // for (i = 1; i < nodes.length; i++) {
        for (let id of node_ids) {
            console.log('  animating...', id, 'of', node_ids)
            var x_start = from_positions[id].x;
            var y_start = from_positions[id].y;

            // get target positions 
            var x_target = to_positions[id].x;
            var y_target = to_positions[id].y;

            // compute the convex combination of x_start and x_target to find intermediate x and move node to it, same for y
            var xt = x_start * (1 - l) + x_target * l;
            var yt = y_start * (1 - l) + y_target * l;

            // move node
            network.moveNode(id, xt, yt);
        }
        console.log('  done animating...', node_ids)

        // stop if we have reached nr of steps
        if (k >= nrOfSteps) {
            console.log('failsafe - animation aborted')
            clearInterval(timer)
            timer = null
        }
    }, tick);
}
