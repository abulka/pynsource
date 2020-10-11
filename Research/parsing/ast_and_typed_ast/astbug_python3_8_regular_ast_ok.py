import ast

# Proof regular ast works ok in python 3.8

source = """
variable = 'a'
x = 29
print(f'{variable=} and {x=}')
"""
node = ast.parse(source)
print(node)
