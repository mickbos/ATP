from lexer import lexer
from parser import parse
from interpreter import interpret
import sys

def main():
    # try:
    tokens = lexer(["tbmp.useless", "plusplus.useless"])
    ASTs = (parse(tokens))
    memory = dict(map(lambda x: (x.name.text, x), ASTs))
    l = interpret(memory['main'], memory)

    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()