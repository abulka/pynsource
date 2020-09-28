/*
how to represent 
        a = GraphNode("A", 0, 0, 250, 250)
        a1 = GraphNode("A1", 0, 0)
        a2 = GraphNode("A2", 0, 0)
        g.AddEdge(a, a1)
        g.AddEdge(a, a2)
as a data structure - well let's convert it to JSON
*/

let default_width = 60
let default_height = 60
let payload = {
    nodes: [
        { id: "a", label: "A", left: 0, top: 0, width: 250, height: 250 },
        { id: "a1", label: "A1", left: 0, top: 0 },
        { id: "a2", label: "A2", left: 0, top: 0 }
    ],
    edges: [
        { from: "a", to: "a1" },
        { from: "a", to: "a2" },
    ]
}

console.log(JSON.stringify(payload))

/*
{"nodes":[{"id":"a","label":"A","left":0,"top":0,"width":250,"height":250},{"id":"a1","label":"A1","left":0,"top":0},{"id":"a2","label":"A2","left":0,"top":0}],"edges":[{"from":"a","to":"a1"},{"from":"a","to":"a2"}]}
*/
