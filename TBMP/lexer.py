from collections import namedtuple
import re
from functools import reduce
from typing import List, Tuple
import operator

TBMPError = namedtuple("TBMPError", ["Errormessage"])


class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_

    def __str__(self):
        return "[" + self.type + ", " + self.text + "]"

# generateTokens :: [str] -> [Token]
# functie om lijst van strings in tokens te converten
def generateTokens(tokenstring : List[str]) -> List[Token]:
    return list(map(lambda x: stringToToken(x), tokenstring))

# stringToToken :: str -> Token
# Converts de string naar tokens
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

    else:
        return Token("ERROR", string)

# lexer :: str -> [Token]
# Main lexer functie.
def lexer(filename: str) -> List[Token]:
    itemList = list(map(lambda special: list(map(lambda a: a.split(), list(map(lambda x: x.split("//", 1)[0], open(special, "r").readlines())))), filename)) # Lees alle bestanden. Verwijder alles na een // en split op spaties
    tokenList = list(map(lambda z: generateTokens(z), reduce(operator.iconcat, itemList, []))) # Run generateTokens over alle tokens uit itemList
    return reduce(operator.iconcat, tokenList, []) # Flikker alle tokens bij mekaar in 1 lijst
