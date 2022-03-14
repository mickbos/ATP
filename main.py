import ast
from lexer import lexer
from myparser import parse
from interpreter import interpret
import sys

def main():
    # try:
    tokens = lexer(["tbmp.useless", "plusplus.useless"])
    print(tokens)
    ASTs = (parse(tokens))
    errors = list(map(lambda x: x.error, ASTs))
    
    print(ASTs[0].blocks)
    memory = dict(map(lambda x: (x.name.text, x), ASTs))
    l = interpret(memory['main'], memory)

    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()