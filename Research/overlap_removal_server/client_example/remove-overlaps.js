// The list of node ids to animate move, with info on from and to in the other dicts below
let node_ids = []

// These use the same dict as we get from network.getPositions([id])
// e.g.  [id]: { x: x, y: y } 
let from_positions = {}
let to_positions = {}

function remove_overlaps() {
    // convert current nodes and edges into a payload for the overlap removal server
    data = { nodes: [], edges: [] }
    // geogebra = []
    for (let id of nodes.getIds()) {
        label = nodes.get(id).label  // all the text of the node, can be large
        bounds = network.getBoundingBox(id) // {top: 26, left: -323, right: -256, bottom: 62}
        // console.log(bounds)
        data.nodes.push({
            id: id,
            left: bounds.left,
            top: bounds.top,
            width: null,
            height: null,
            // right and bottom are derived by the server coming back, not going in
            // but I'm changing this now... so that if you supply them then width and height 
            // will be calculated for you
            right: bounds.right,
            bottom: bounds.bottom,
        })
        /*
         A  B
         D  C
         Polygon({(left, top),(right,top),(right,bottom),(left,bottom)})
         Note to visulise in geogebra I have to invert the y since visjs and pynsource use +y going down south whereas geogebra
         have a more normal math coordinate system where +y goes up north
        */
        if (emitGeogebraPositions)
            console.log(`node${id}=Polygon({(${Math.trunc(bounds.left)},${-Math.trunc(bounds.top)}),(${Math.trunc(bounds.right)},${-Math.trunc(bounds.top)}),(${Math.trunc(bounds.right)},${-Math.trunc(bounds.bottom)}),(${Math.trunc(bounds.left)},${-Math.trunc(bounds.bottom)})})`)
    }
    for (let id of edges.getIds()) {
        var edge = edges.get(id)
        // console.log(`edge ${id} from ${edge.from} to ${edge.to}`)
        data.edges.push({
            from: edge.from,
            to: edge.to,
        })
    }
    if (debugPayloads)
        console.log('payload is', data)

    // call server
    $.ajax({
        url: 'http://127.0.0.1:5000/overlaps',
        type: "POST",
        data: JSON.stringify(data),
        // dataType: 'json',
        contentType: 'application/json',
        success: function (result) {
            if (debugPayloads)
                console.log(`overlap removal analysis ${result.total_overlaps_found} overlaps, were_all_overlaps_removed ${result.were_all_overlaps_removed}`, result)

            let any_moves_scheduled = false
            for (let node_new of result.graph.nodes) {
                // apply the changes
                let id = node_new.id
                let move_needed = false
                let node_old = nodes.get(id)
                if (node_old == undefined)
                    throw (`could not find old node id ${id} in ${nodes}`)
                node_old_bounds = network.getBoundingBox(id)
                if (node_old_bounds.left != node_new.left) {
                    move_needed = true
                    let amount = node_old_bounds.left - node_new.left
                    // console.log(`node ${id} left coord changed by ${amount} from ${node_old_bounds.left} to ${node_new.left}`)
                }
                if (node_old_bounds.top != node_new.top) {
                    move_needed = true
                    let amount = node_old_bounds.top - node_new.top
                    // console.log(`node ${id} top coord changed by ${amount} from ${node_old_bounds.top} to ${node_new.top}`)
                }
                if (move_needed) {

                    console.log(`  scheduling a move of node ${node_new.id} to left: ${node_new.left} top: ${node_new.top}`)
                    if (emitGeogebraPositions)
                        console.log(`after${node_new.id}=Polygon({(${Math.trunc(node_new.left)},${-Math.trunc(node_new.top)}),(${Math.trunc(node_new.right)},${-Math.trunc(node_new.top)}),(${Math.trunc(node_new.right)},${-Math.trunc(node_new.bottom)}),(${Math.trunc(node_new.left)},${-Math.trunc(node_new.bottom)})})`)

                    let [x, y] = to_node_centrexy(node_new)
                    node_ids.push(id)
                    from_positions = {...from_positions, ...network.getPositions([id]) } // combine two dicts
                    to_positions[id] = { x: x, y: y }

                    any_moves_scheduled = true
                }
            }
            if (!any_moves_scheduled)
                console.log('all good, no overlaps')
            else {
                // turn off physics otherwise another layout will occur as soon as we move any nodes
                options.physics.enabled = false
                network.setOptions(options)
                moveNodeAnimated(node_ids, from_positions, to_positions)

                // reset for next time
                node_ids = []
                from_positions = {}
                to_positions = {}

                console.log('all good, overlaps removal phase complete')
            }


        },
        error: function (error) {
            console.log(`Error ${error}`)
        }
    })

}
