import re
from functools import reduce
from typing import List, Tuple
import operator

class Token:
    def __init__(self, type_: str, text_: str, linenr_):
        self.type = type_
        self.text = text_
        self.linenr = linenr_

    def __repr__(self):
        return "[" + self.type + ", " + self.text + "] at " + self.linenr

def addLineNumbers(fileinput: List, linenr: int) -> Tuple[List[Token], int]:
    fileinput[linenr] = (fileinput[linenr], linenr)
    if (linenr+1 == len(fileinput)):
        return fileinput
    return addLineNumbers(fileinput, linenr + 1)

def rfind(r : List) -> int:
    if not r:
        return -1
    elif r[-1][-1] == "\"": 
        return len(r) - 1
    else:
        return rfind(r[:-1])

def lfind(l : List) -> int:
    if not l:
        return -1
    elif l[-1][0] == "\"":
        return len(l) -1
    else:
        return lfind(l[:-1])

def isNumeral(s) -> bool:
    return all(map(lambda l: '0' <= '9', s if s != '-' else s[1:]))

def combineStrings(stringinput: List[Token]) -> List[Token]:
    left = lfind(stringinput)
    right = rfind(stringinput)
    if(left != -1):
        if(right != -1):
            if(len(stringinput[left:right+1]) >= 2):
                head, *tail = stringinput[left:right+1]
                head += " " + tail[0]
                stringinput[left: right+1] = [head] + tail[1:]
                return combineStrings(stringinput)
            else:
                return stringinput
        else:
            raise Exception("Syntax error: Expected second \"")
    else:
        return stringinput
    
def generateTokens(tokenstring : List, linenr: int) -> List[Token]:
    return list(map(lambda x: stringToToken(x, linenr), tokenstring))

def stringToToken(string: str, linenr: int) -> Token:
    operators = ["operator=", "operator==", "operator+", "operator-", "operator<", "operator>"]
    if(string in operators):
        return Token("OPERATOR", string, linenr)

    if(string == "if"):
        return Token("IF", "if", linenr)
    if(string == "else"):
        return Token("ELSE", "else", linenr)
    if(string == "showme"):
        return Token("SHOWME", "showme", linenr)
    if(string == "while"):
        return Token("WHILE", "while", linenr)
    if(string == "giveback"):
        return Token("GIVEBACK", "giveback", linenr)
    
    if(string == "def"):
        return Token("FUNCTIONDEF", string, linenr)

    if(string[0] == "\""):
        return Token("STRING", string, linenr)
    if(string == "["):
        return Token("OPENING_BRACKET", "[", linenr)
    if(string == "]"):
        return Token("CLOSING_BRAKCET", "]", linenr)
    if(string == "{"):
        return Token("LBRACE", "{", linenr)
    if(string == "}"):
        return Token("RBRACE", "}", linenr)
    if(string == "("):
        return Token("LPAREN", "(", linenr)
    if(string == ")"):
        return Token("RPAREN", ")", linenr)    
        
    if(re.fullmatch("^[0-9-][0-9.]*", string)):
        return Token("NUMERAL", string, linenr)
    if (re.fullmatch("^[a-zA-Z_][a-zA-Z_0-9]*", string)):
        return Token("VARIABLE", string, linenr)

    elif(string[-1] == "("):
        return Token("FUNCTIONCALL", string, linenr)

    else:
        raise Exception("Syntax Error: \"{0}\" on line {1}.".format(string, linenr))




def lexer(filename: str) -> List[Token]:
    f = list(map(lambda special: list(map(lambda y: (combineStrings(y[0]), y[1]), addLineNumbers(list(map(lambda a: a.split(), list(map(lambda x: x.split("//", 1)[0], open(special, "r").readlines())))), 0))), filename)) #Split the file, add line numbers and combine strings
    tokenList = list(map(lambda z: generateTokens(z[0], z[1]), reduce(operator.iconcat, f, [])))
    return reduce(operator.iconcat, tokenList, []) #generate tokens and move all into one array

