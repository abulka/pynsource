import sys

"""
Proof that typed_ast.ast3 cannot handle Python 3.8 syntax.
This models what Pynsource src/parsing/core_parser_ast.py does

This is as is expected.

NOTE: The official word on this is: https://github.com/python/typed_ast
typed_ast will not be updated to support parsing Python 3.8 and newer.
Instead, it is recommended to use the stdlib ast module there, which
has been augmented to support extracting type comments and has limited
support for parsing older versions of Python 3.
"""

# lookup tables e.g. BOOLOP_SYMBOLS in a more general way e.g. 'And'
import ast as ast_native  # native ast of the Python that is running

if sys.version_info >= (3, 0):
    import typed_ast.ast27  # py2 (requires Python 3 to be running)
    import typed_ast.ast3  # py3 (requires Python 3 to be running)

source = """
variable = 'a'
x = 29
print(f'{variable=} and {x=}')
"""
ast = typed_ast.ast3
node = ast.parse(source)
print(node)
