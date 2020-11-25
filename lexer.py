import io
import os
import re
import time
from functools import reduce
from typing import Callable, TypeVar, List

def readyForExtraction(fileinput : List) -> List:
    fileinput = list(map(lambda x : checkForComments(x), fileinput))
    fileinput = addLineNumbers(fileinput, 0) #adds the line numbers
    return list(filter(lambda y: y[0], fileinput))  # removes lines with None or empty list entries

def checkForComments(stringinput: str) -> str:
    stringinput = stringinput.strip() # Strips whitespaces and \n
    if(stringinput[0:2] != "//"):   # only returns the string if it doesn't have // as first 2 characters
        return stringinput

def addLineNumbers(fileinput: List, linenr: int) -> List:
    fileinput[linenr] = (fileinput[linenr], linenr)
    if (linenr+1 == len(fileinput)):
        return fileinput
    return addLineNumbers(fileinput, linenr + 1)

def rfind(r : List):
    if not r:
        return -1
    elif r[-1][-1] == "\"": 
        return len(r) - 1
    else:
        return rfind(r[:-1])

def lfind(l : List):
    if not l:
        return -1
    elif l[-1][0] == "\"":
        return len(l) -1
    else:
        return lfind(l[:-1])

def combineStrings(stringinput: List):
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
    
def readFile(fileName : io.TextIOWrapper) -> List:
    read = fileName.readline()
    if (read == ""):
        return [read]
    return [read] + readFile(fileName)
    

def generateTokens(tokenstring : List, linenr: int):
    return list(map(lambda x: stringToToken(x, linenr), tokenstring))

def stringToToken(string: str, linenr: int):
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
        
    if(string.isnumeric()):
        return Token("NUMERAL", string, linenr)
    if (re.fullmatch("^[a-zA-Z_][a-zA-Z_0-9]*", string)):
        return Token("VARIABLE", string, linenr)

    else:
        raise Exception("Syntax Error: \"{0}\" on line {1}. Pogn't".format(string, linenr))

class Token:
    def __init__(self, type_: str, text_: str, linenr_):
        self.type = type_
        self.text = text_
        self.linenr = linenr_

    def __repr__(self):
        return "[" + self.type + ", " + self.text + "]"


def main():
    
    f = open("tbmp.txt", "r")
    f = readFile(f)

    # addLineNumbers(f)
    try:
        f = (readyForExtraction(f))
        f = list(map(lambda x: (x[0].split(" "), x[1]), f))
        f = list(map(lambda y: (combineStrings(y[0]), y[1]), f))
        tokens = (list(map(lambda z: generateTokens(z[0], z[1]), f)))
        for t in tokens:
            print(t)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()