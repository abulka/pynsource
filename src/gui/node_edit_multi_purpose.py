from gui.uml_shapes import CommentShape
from typing import List, Set, Dict, Tuple, Optional


def node_edit_multi_purpose(shape, app):
    """
    Edit a uml class node or a comment node

    Main menu calls this from pynsourcegui or
    Or uml shape handler (above) calls this when right click on a shape

    Args:
        shape:
        app:

    Returns: -

    """
    # node is a regular node, its the node.shape that is different for a comment
    from gui.uml_shapes import DividedShape

    if isinstance(shape, DividedShape):
        app.run.CmdEditUmlClass(shape)
    elif isinstance(shape, CommentShape):
        app.run.CmdEditComment(shape)
    else:
        print("Unknown Shape", shape)
