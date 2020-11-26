from lexer import lexer
from parser import parse

def main():
    tokens = lexer("tbmp.useless")
    ASTs = (parse(tokens))
    for ast in ASTs:
        print (ast.codeSequence)

if __name__ == "__main__":
    main()