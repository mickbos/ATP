from lexer import lexer
from parser import parse

def main():
    tokens = lexer("tbmp.useless")
    ASTs = (parse(tokens))
    for i in (ASTs[1].blocks):
        print(i)
if __name__ == "__main__":
    main()