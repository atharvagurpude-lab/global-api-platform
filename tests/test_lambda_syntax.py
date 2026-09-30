import ast
from pathlib import Path

def test_lambda_source_is_valid_python():
    source = Path("lambda/lambda_function.py").read_text()
    ast.parse(source)

