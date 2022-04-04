import ast
from lexer import lexer
from myparser import parse
from interpreter import interpret

def main():
    # try:
    tokens = lexer(["tbmp.use", "compilertest.use", "parsertest.use"])
    ASTs = (parse(tokens))

    memory = dict(map(lambda x: (x.name, x), ASTs))
    interpret(memory['main'], memory)

if __name__ == "__main__":
    main()

# def sommig( n ):
#     result = 0
#     while ( n >= 1 ):
#         result += n
#         n=n-1
#     return result

# print(sommig(5))
