let enablePhysicsDuringDrag = true
let drawCartesianGrid = false
let emitGeogebraPositions = false  // paste into https://www.geogebra.org/calculator 
let debugPayloads = false

function to_node_centrexy(node) {
    // visjs moves a node to x,y to the centrepoint - not the left, top - so convert
    let x = node.left + node.width / 2
    let y = node.top + node.height / 2
    return [x, y]
}