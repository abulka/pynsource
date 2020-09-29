import flask
from flask import request
from flask_cors import CORS  # pip install -U flask-cors (allow anyone to call this api)
import pprint
import sys
import json

sys.path.append("../../src")
pprint.pprint(sys.path)
from layout.overlap_removal import OverlapRemoval, LINE_NODE_OVERLAP_REMOVAL_ENABLED
from view.graph import Graph, GraphNode
# from data_testgraphs import *  # e.g. TEST_GRAPH1

"""
    Overlap remover as a server API. Send up JSON get back JSON.
    JSON we send up is a list of nodes and edges. See Research/overlap_removal_server/payload1.js 

    Start server:
        python -m flask run flask_main.py
        python -m flask run --no-reload flask_main.py

    Example of usage:
        POST to http://127.0.0.1:5000/overlaps
            {
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
            which as proper JSON is:
                {"nodes":[{"id":"a","label":"A","left":0,"top":0,"width":250,"height":250},{"id":"a1","label":"A1","left":0,"top":0},{"id":"a2","label":"A2","left":0,"top":0}],"edges":[{"from":"a","to":"a1"},{"from":"a","to":"a2"}]}

        Response contains the modified graph of nodes and edges with new left, top positions
        as well as some metadata e.g. JSON
            {
            "error": "none", 
            "graph": {
                "edges": [
                {
                    "from": "a", 
                    "to": "a1"
                }, 
                {
                    "from": "a", 
                    "to": "a2"
                }
                ], 
                "nodes": [
                {
                    "height": 60, 
                    "id": "a", 
                    "left": 0, 
                    "top": 0, 
                    "width": 60
                }, 
                {
                    "height": 60, 
                    "id": "a1", 
                    "left": 65, 
                    "top": 0, 
                    "width": 60
                }, 
                {
                    "height": 60, 
                    "id": "a2", 
                    "left": 130, 
                    "top": 0, 
                    "width": 60
                }
                ]
            }, 
            "graph_as_string": "# PynSource Version 1.2\n{'type':'meta', 'info1':'Lorem ipsum dolor sit amet, consectetur adipiscing elit is latin. Comments are saved.'}\n{'type':'', 'id':'a', 'x':0, 'y':0, 'width':60, 'height':60}\n{'type':'', 'id':'a1', 'x':65, 'y':0, 'width':60, 'height':60}\n{'type':'', 'id':'a2', 'x':130, 'y':0, 'width':60, 'height':60}\n{'type':'', 'id':'a_to_a1', 'source':'a', 'target':'a1'}\n{'type':'', 'id':'a_to_a2', 'source':'a', 'target':'a2'}\n", 
            "total_contractive_moves": 0, 
            "total_cycles": 4, 
            "total_expansive_moves": 3, 
            "total_overlaps_found": 5, 
            "total_postmove_fixes": 0, 
            "warning_msg": "", 
            "were_all_overlaps_removed": true
            }

    Test (postman):
        pm.test("Status code is 200", function () { pm.response.to.have.status(200); });
        pm.test("all overlaps removed", function () { 
            pm.response.to.have.status(200); 
            
            // check actual json payload, convert to dict
            var jsonData = JSON.parse(responseBody);
            
            pm.expect(jsonData.error).to.equal('none');
            pm.expect(_.get(jsonData, 'error')).to.equal('none');

            // ensure all overlaps were removed    
            pm.expect(jsonData.were_all_overlaps_removed).to.equal(true);

            // check specific values    
            let a = _.findNode('a', jsonData);
            pm.expect(a).to.have.property('height');
            pm.expect(a.left).to.equal(0);
            pm.expect(a.top).to.equal(0);
            
            pm.expect(_.findNode('a1', jsonData).left).to.equal(65);
        });

    Postman tip:
        Put common shared scripts in the collection pre-request scripts, 
        which is trickily accessed via the collections ... button then Edit / Pre-request Scripts.

        Define them on Object and then it will be available on any object including underscore _ object
        https://stackoverflow.com/questions/45673961/how-to-write-global-functions-in-postman 

        Object.prototype.sayHello = function(name){
            console.log(`Hello! ${name}`);
        };

        Object.prototype.findNode = function(id, jsonData) {
            if (id === undefined) {
                console.log('id is undefined');
                return;
            }
            for (let node of jsonData.graph.nodes)
                if (node.id == id)
                    return node;
            return undefined;
        };

"""

app = flask.Flask(__name__)
CORS(app)  # allow anyone to call this API https://stackoverflow.com/questions/20035101/why-does-my-javascript-code-receive-a-no-access-control-allow-origin-header-i
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site ANDY is a prototype API for distant reading of science fiction novels.</p>"


@app.route("/post/<int:post_id>")
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return "Post %d" % post_id


@app.route("/login", methods=["POST", "GET"])
def login():
    # If you return a dict from a view, it will be converted to a JSON response.
    error = None
    if request.method == "POST":
        return {
            "username": request.form["username"],
            "password": request.form["password"],
            "andy_extra": "hi there",
            "status": "good post, returning good info back!! :-)",
            "LINE_NODE_OVERLAP_REMOVAL_ENABLED": LINE_NODE_OVERLAP_REMOVAL_ENABLED,
        }
    else:  # GET
        return {"error": "GET not really supported, mate"}


@app.route("/overlaps-ping", methods=["POST"])
def remove_overlaps_ping():
    # just prove the python code is accessible and working, no payload accepted
    class FakeGui:
        def mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
            pass

    g = Graph()
    overlap_remover = OverlapRemoval(g, margin=5, gui=FakeGui())
    if request.method == "POST":
        # g.AddNode(GraphNode("A", 0, 0, 250, 250))
        a = GraphNode("A", 0, 0, 250, 250)
        a1 = GraphNode("A1", 0, 0)
        a2 = GraphNode("A2", 0, 0)
        g.AddEdge(a, a1)
        g.AddEdge(a, a2)

        were_all_overlaps_removed = overlap_remover.RemoveOverlaps()
        basic_info = {
            "error": "none",
            "were_all_overlaps_removed": were_all_overlaps_removed,
        }
        return {**basic_info, **(overlap_remover.GetStats())}
    else:  # GET
        return {"error": "GET not really supported, mate"}


def overlap_remover_core(data):
    class FakeGui:
        def mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
            pass

    g = graph_fromDict(data)
    print('got incoming graph', g.GraphToString())
    overlap_remover = OverlapRemoval(g, margin=5, gui=FakeGui())
    were_all_overlaps_removed = overlap_remover.RemoveOverlaps()
    print('graph after overlap removal', g.GraphToString(), overlap_remover.GetStats())

    basic_info = {
        "error": "none",
        "were_all_overlaps_removed": were_all_overlaps_removed,
        "graph_as_string": g.GraphToString(),
        "graph": graph_toDict(g),
    }
    return {**basic_info, **(overlap_remover.GetStats())}


def graph_fromDict(data: dict) -> Graph:
    # should be a method on Graph called .fromJSON() but this takes a dict so maybe don't bother
    g = Graph()
    nodes_created = {}
    if "nodes" in data.keys():
        for node in data["nodes"]:
            id = node["id"]
            # label = node["label"]  # not used

            # if you don't supply 'width' and 'height' but do supply 'right' and 'bottom' 
            # then 'width' and 'height' will be calculated for you. 
            width = node.get("width", None)
            height = node.get("height", None)
            if not width:
                if node.get("right") is not None:
                    width = node["right"] - node["left"]
                else:
                    width = 60
            if not height:
                if node.get("bottom") is not None:
                    height = node["bottom"] - node["top"]
                else:
                    height = 60

            # gnode = GraphNode(id, node["left"], node["top"], width, height)  # or
            gnode = g.create_new_node(id, node["left"], node["top"], width, height)

            g.AddNode(gnode)
            nodes_created[id] = gnode
    if "edges" in data.keys():
        for edge in data["edges"]:
            # ah have to get the references to the nodes created and add edges
            from_node_id, to_node_id = edge["from"], edge["to"]
            from_node = nodes_created[from_node_id]
            to_node = nodes_created[to_node_id]
            g.AddEdge(from_node, to_node)
    return g


def graph_toDict(g: Graph) -> dict:
    # should be a method on Graph called .fromJSON() but this returns a dict so maybe don't bother
    data = {"nodes": [], "edges": []}

    for node in g.nodes:
        data["nodes"].append(
            {
                "id": node.id,
                # "label": node.id,   # not used
                "left": node.left,
                "top": node.top,
                "right": node.right,
                "bottom": node.bottom,
                "width": node.width,
                "height": node.height,
            }
        )
    for edge in g.edges:
        data["edges"].append(
            {"from": edge["source"].id, "to": edge["target"].id,}
        )
    return data


@app.route("/echo", methods=["POST"])
def json_echo():
    # echo same JSON payload out
    if request.method == "POST":
        json_dict = request.get_json()
        if not json_dict:
            return {"error": "could not decode any json, sorry - got None"}
        pprint.pprint(json_dict)
        return request.get_json()  # just send it straight back


@app.route("/overlaps", methods=["POST"])
def remove_overlaps():
    # the real thing, JSON payload in and out
    if request.method == "POST":
        json_dict = request.get_json()
        if not json_dict:
            return {"error": "could not decode any json, sorry - got None"}
        json_result = overlap_remover_core(json_dict)
        return json_result


@app.route("/test-graph1", methods=["GET"])
def get_test_graph1():
    # {"nodes": [{"id": "D25", "left": 7, "top": 6, "width": 159, "height": 106}, {"id": "D13", "left": 6, "top": 119, "width": 119, "height": 73}, {"id": "m1", "left": 171, "top": 9, "width": 139, "height": 92}]}
    data = {
        "nodes": [
            {"id": "D25", "left": 7, "top": 6, "width": 159, "height": 106},
            {"id": "D13", "left": 6, "top": 119, "width": 119, "height": 73},
            {"id": "m1", "left": 171, "top": 9, "width": 139, "height": 92},
        ]
    }
    # generate payload for test1_1MoveLeftPushedBackHorizontally01
    # {"nodes": [{"id": "D25", "left": 7, "top": 6, "width": 159, "height": 106}, {"id": "D13", "left": 6, "top": 119, "width": 119, "height": 73}, {"id": "m1", "left": 150, "top": 9, "width": 139, "height": 92}]}
    data["nodes"][2]["left"] = 150
    data["nodes"][2]["top"] = 9
    print(json.dumps(data))

    return data


app.run()
