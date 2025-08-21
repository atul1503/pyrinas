import tokenize
from io import BytesIO

def get_tokens(code: str):
    """
    Tokenizes the given Python code.
    """
    code_bytes = code.encode('utf-8')
    return list(tokenize.generate_tokens(BytesIO(code_bytes).readline))

if __name__ == '__main__':
    with open('examples/hello.pyr', 'r') as f:
        code = f.read()
    
    for token in get_tokens(code):
        print(token)
