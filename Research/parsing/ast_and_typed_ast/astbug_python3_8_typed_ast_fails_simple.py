# import ast
from typed_ast import ast3

"""
Proof that typed_ast.ast3 cannot handle Python 3.8 syntax.
Simplified test case.

This is as is expected.

NOTE: The official word on this is: https://github.com/python/typed_ast
typed_ast will not be updated to support parsing Python 3.8 and newer.
Instead, it is recommended to use the stdlib ast module there, which
has been augmented to support extracting type comments and has limited
support for parsing older versions of Python 3.
"""

source = """
variable = 'a'
x = 29
print(f'{variable=} and {x=}')
"""
node = ast3.parse(source)
print(node)
