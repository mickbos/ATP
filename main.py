import ast
from lexer import lexer
from myparser import parse
from interpreter import interpret
import sys

def main():
    # try:
    # tokens = lexer(["parsertest.use", "tbmp.use"])
    tokens = lexer(["errorhandling.use", ])
    ASTs = (parse(tokens))
    errors = list(map(lambda x: x.error, ASTs))

    memory = dict(map(lambda x: (x.name, x), ASTs))
    l = interpret(memory['main'], memory)

    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()

# def sommig( n ):
#     result = 0
#     while ( n >= 1 ):
#         result += n
#         n=n-1
#     return result

# print(sommig(5))
