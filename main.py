from lexer import lexer
from myparser import parse
from interpreter import interpret
from mycompiler import compile

def main():
    # try:
    tokens = lexer(["compilertest.use",])
    ASTs = (parse(tokens))

    print(ASTs[0].blocks)

    memory = dict(map(lambda x: (x.name, x), ASTs))
    # interpret(memory['main'], memory)
    compile(ASTs)

if __name__ == "__main__":
    main()

# def sommig( n ):
#     result = 0
#     while ( n >= 1 ):
#         result += n
#         n=n-1
#     return result

# print(sommig(5))
