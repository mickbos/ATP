from collections import namedtuple
import re
from functools import reduce
from typing import List, Tuple
import operator

def LexerErrorDecorator(func) :
    def inner(string):
        if(type(string) == TBMPError):
            return Token("ERROR", "Syntax error: Second \" not found")
        else:
            return func(string)
    return inner
        

TBMPError = namedtuple("TBMPError", ["Errormessage"])

class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_

    def __str__(self):
        return "[" + self.type + ", " + self.text + "]"

def isNumeral(s) -> bool:
    return all(map(lambda l: '0' <= '9', s if s != '-' else s[1:]))

    
def generateTokens(tokenstring : List) -> List[Token]:
    return list(map(lambda x: stringToToken(x), tokenstring))

@LexerErrorDecorator
def stringToToken(string: str) -> Token:
    operators = ["operator=", "operator==", "operator+", "operator-", "operator<", "operator>"]
    if(string in operators):
        return Token("OPERATOR", string)

    if(string == "if"):
        return Token("IF", "if")
    if(string == "else"):
        return Token("ELSE", "else")
    if(string == "showme"):
        return Token("SHOWME", "showme")
    if(string == "while"):
        return Token("WHILE", "while")
    if(string == "giveback"):
        return Token("GIVEBACK", "giveback")
    
    if(string == "def"):
        return Token("FUNCTIONDEF", string)

    if(string == "["):
        return Token("OPENING_BRACKET", "[")
    if(string == "]"):
        return Token("CLOSING_BRAKCET", "]")
    if(string == "{"):
        return Token("LBRACE", "{")
    if(string == "}"):
        return Token("RBRACE", "}")
    if(string == "("):
        return Token("LPAREN", "(")
    if(string == ")"):
        return Token("RPAREN", ")")    
        
    if(re.fullmatch("^[0-9-][0-9.]*", string)):
        return Token("NUMERAL", string)
    if (re.fullmatch("^[a-zA-Z_][a-zA-Z_0-9]*", string)):
        return Token("VARIABLE", string)

    elif(string[-1] == "("):
        return Token("FUNCTIONCALL", string)

    else:
        return Token("ERROR", string)



def lexer(filename: str) -> List[Token]:
    g = list(map(lambda special: list(map(lambda a: a.split(), list(map(lambda x: x.split("//", 1)[0], open(special, "r").readlines())))), filename))

    tokenList = list(map(lambda z: generateTokens(z), reduce(operator.iconcat, g, [])))
    return reduce(operator.iconcat, tokenList, []) #generate tokens and move all into one array
