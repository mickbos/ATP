from typing import TypeVar, List, Tuple, Union

from lexer import Token, TBMPError
from collections import namedtuple

def TBMPErrorDecorator(func):
    def inner(tokenLine: List[Token]) -> Tuple[Union[Expression, Loop, If, Function], List[Token]]:
        if(tokenLine[0].type == "ERROR"):
            return TBMPError(tokenLine[0].text), tokenLine[1:]
        return func(tokenLine)
    return inner

Expression = namedtuple("Expression", ["function", "argc", "args"])
Function = namedtuple("Function", ["name", "args"])
Variable = namedtuple("Variable", ["name"])
Value = namedtuple("Value", ["content"])
Loop = namedtuple("Loop", ["Body", "Expression"])
If = namedtuple("If", ["Body", "Expression", "ElseBody"])

class AST:
    def __init__(self, name: str = "", argumentList: List[Token] = "", codeSequence: List[Union[Expression, If, Loop, Function]] = ""):
        self.name = name
        self.argumentList = argumentList
        self.codeSequence = codeSequence
        self.blocks = List
        self.error = None
    
    def __str__(self):
        return "Abstract Syntax Tree of function " + self.name

# parseNotOperator :: [Token] -> (Union(Value, Variable, Function, TBMError), [Token])
# Parser functie voor variabelen, values en nummers
def parseNotOperator(tokenLine: List[Token]) -> Tuple[Union[Value, Variable, Function, TBMPError], List[Token]]:
    if(tokenLine[0].type == "VARIABLE"):
        if(len(tokenLine) > 1):
            if(tokenLine[1].type == "LPAREN"): #Functioncall
                parenIndexes = returnParenIndexes(tokenLine)
                if(type(parenIndexes) is not TBMPError):
                    functionname = tokenLine[0].text
                    arguments, tokenLine = returnFunctionBody(tokenLine[2:], [])
                    # arguments = ""
                    function = Function(functionname, arguments )
                    return function, tokenLine[1:]
                else:
                    return parenIndexes, tokenLine[1:]
        return Variable(tokenLine[0].text), tokenLine[1:]
    elif(tokenLine[0].type == "VALUE"):
        return Value(tokenLine[0].text), tokenLine[1:]
    elif(tokenLine[0].type == "NUMERAL"):
        return Value(tokenLine[0].text), tokenLine[1:]
    else:
        return TBMPError("Syntax error: {0} is not expected".format(tokenLine[0].text)), tokenLine[1:]
    
# parseOperator :: [Token] -> (Expression, [Token])
# Parse functie voor operators
def parseOperator(tokenLine: List[Token]) -> Tuple[Expression, List[Token]]:
    function = tokenLine[0].text
    argument1, tokenLine = detectParse(tokenLine[1:])
    argument2, tokenLine = detectParse(tokenLine)
    return Expression(function=function, argc=2, args=[argument1, argument2]), tokenLine

# parseShowGiveback :: [Token] -> (Expression, [Token])
# Parse functie om de showme en giveback af te handelen
def parseShowGiveback(tokenLine: List[Token]) -> Tuple[Expression, List[Token]]:
    function = tokenLine[0].text
    parenindex = returnParenIndexes(tokenLine)
    if(type(parenindex) != TBMPError):
        arguments, tokenLine = detectParse(tokenLine[parenindex[0]+1:])
        
        return Expression(function=function, argc=len(arguments), args=[arguments]), tokenLine[1:]
    else:
        return parenindex, []

# parseIf :: [Token] -> (If, [Token])
# Parse functie voor if statements
def parseIf(tokenLine: List[Token]) -> Tuple[If, List[Token]]:
    parenIndex = returnParenIndexes(tokenLine)
    if(type(parenIndex) != TBMPError):
        expression, tokenLine = detectParse(tokenLine[parenIndex[0]+1:])
        braceIndex = returnBraceIndexes(tokenLine)
        if(type(braceIndex) != TBMPError):
            body, tokenLine = detectParse(tokenLine[braceIndex[0]+1:])

            if(len(tokenLine) > 1):
                if(tokenLine[1].type == "ELSE"):
                    tokenLine = tokenLine[1:]
                    braceIndex = returnBraceIndexes(tokenLine)
                    elsebody, tokenLine = detectParse(tokenLine[braceIndex[0]+1:])
                    return If(Expression=expression, Body=[body], ElseBody=[elsebody]), tokenLine[1:]

            return If(Expression=expression, Body=[body], ElseBody = []),  tokenLine[1:]
        return braceIndex, [] # returns de error
    return parenIndex, [] # returns de error

# ReturnWhileBody :: [Token] -> [Union(Expression, Loop, If, Function)] -> ([Union(Expression, Loop, If, Function)], [Token])
# Functie om de body van de while te returnen. 
def returnWhileBody(tokenLine : List[Token],  temp: List[Union[Expression, Loop, If, Function]]) -> Tuple[List[Union[Expression, Loop, If, Function]], List[Token]]:
    if tokenLine[0].text == "}":
        return temp, tokenLine[1:]
    else:
        exp, tokenLine = detectParse(tokenLine)
        temp.append(exp)
        return returnWhileBody(tokenLine, temp)

# ReturnWhileBody :: [Token] -> [Union(Expression, Loop, If, Function)] -> ([Union(Expression, Loop, If, Function)], [Token])
# Functie om de body van de if te returnen
def returnFunctionBody(tokenLine : List[Token],  temp: List[Union[Expression, Loop, If, Function]]) -> Tuple[List[Union[Expression, Loop, If, Function]], List[Token]]:
    if tokenLine[0].text == ")":
        return temp, tokenLine[1:]
    else:
        exp, tokenLine = detectParse(tokenLine)
        temp.append(exp)
        return returnFunctionBody(tokenLine, temp)

# parseWhile :: [Token] -> (Loop, [Token])
# Functie om de while te parsen. Check de haakjes. Sla de expressie op
def parseWhile(tokenLine: List[Token]) -> Tuple[Loop, List[Token]]:
    parenIndex = returnParenIndexes(tokenLine)
    if(type(parenIndex) != TBMPError):
        expression, tokenLine = detectParse(tokenLine[parenIndex[0]+1:])
        braceIndex = returnBraceIndexes(tokenLine)
        if(type(braceIndex) != TBMPError):
            body, tokenLine = returnWhileBody(tokenLine[braceIndex[0]+1:], [])

            return Loop(Expression=expression, Body=body), tokenLine
        return braceIndex, []
    return parenIndex, []

# detectParse :: [Token] -> [Union(Expression, Loop, If, Function), [Token])
# Functie die de Token checkt en de juiste functie aanroept
@TBMPErrorDecorator
def detectParse(tokenLine: List[Token]) -> Tuple[Union[Expression, Loop, If, Function], List[Token]]:
    operators = ["OPERATOR", "SHOWME", "GIVEBACK", "WHILE", "IF", "ELSE"]
    if tokenLine:
        if(tokenLine[0].type not in operators):
            return parseNotOperator(tokenLine)
        if(tokenLine[0].type == "OPERATOR"):
            return parseOperator(tokenLine)
        if(tokenLine[0].type == "SHOWME" or tokenLine[0].type == "GIVEBACK"):
            return parseShowGiveback(tokenLine)
        if(tokenLine[0].type == "IF"):
            return parseIf(tokenLine)
        if(tokenLine[0].type == "WHILE"):
            return parseWhile(tokenLine)
    return [], []

# findFunctionIndex :: [Token] -> [int] -> [int]
# Functie die de locatie van de "def" Tokens teruggeeft
def findFunctionIndex(tokenlist: List[Token], index: List[int] = []) -> List[int]:
    if(len(tokenlist) == 0):
        return index
    elif (tokenlist[-1].text == "def"):
        index.append(len(tokenlist))
        return findFunctionIndex(tokenlist[:-1], index)
    else:
        return findFunctionIndex(tokenlist[:-1], index)

# returnParenIndexes :: [Token] -> int -> int -> int -> Union((int, int), TBMPError)
# functie die de locatie van de haakjes teruggeeft in tokenlist
def returnParenIndexes(tokenlist: List[Token], lParen: int =0, rParen: int =0, toSkip: int = -1) -> Union[Tuple[int, int], TBMPError]:
    if(tokenlist[rParen].text == ")"):
        if(toSkip > 0):
            return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip - 1)
        if(toSkip == -1):
            return TBMPError("Opening parenthesis not found")
        else:
            return lParen, rParen
    elif(tokenlist[rParen].text == "("):
        if( ( len(tokenlist) - rParen) == 1 ):
            return TBMPError("Closing parenthesis not found")
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip + 1)

    elif(tokenlist[lParen].text == "("):
        if( ( len(tokenlist) - rParen) == 1 ):
            return TBMPError("Closing parenthesis not found")
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip)
    else:
        if( ( len(tokenlist) - lParen) == 1 ):
            return TBMPError("Opening parenthesis not found")
        return returnParenIndexes(tokenlist, lParen + 1, rParen, toSkip)

# returnBraceIndexes :: [Token] -> int -> int -> int -> Union((int, int), TBMPError)
# functie die de locatie van de accolades teruggeeft in tokenlist
def returnBraceIndexes(tokenlist: List, lBrace: int = 0, rBrace: int =0, toSkip: int = -1) -> Union[Tuple[int, int], TBMPError]:
    if(tokenlist[rBrace].text == "}"):
        if(toSkip > 0):
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip - 1)
        if(toSkip == -1):
            return TBMPError("Opening brace not found")
        else:
            return lBrace, rBrace
    else:
        if(tokenlist[rBrace].text == "{"):
            if( ( len(tokenlist) - rBrace) == 1 ):
                return TBMPError("Closing brace not found")
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip + 1)

        elif(tokenlist[lBrace].text == "{"):
            if( ( len(tokenlist) - rBrace) == 1 ):
                return TBMPError("Closing brace not found")
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip)
        else:
            if( ( len(tokenlist) - lBrace) == 1 ):
                return TBMPError("Opening brace not found")
            return returnBraceIndexes(tokenlist, lBrace + 1, rBrace, toSkip)


# makeAST :: [Token] -> AST
# Functie die de AST genereert
def makeAST(tokenlist: List[Token]) -> AST:
    ast = AST()
    ast.name = tokenlist[1].text

    parenIndex = returnParenIndexes(tokenlist, 0, 0)
    if (type(parenIndex) == TBMPError):
        ast.error = parenIndex
        return ast
    firstP, lastP = parenIndex

    ast.argumentList =  list(map(lambda i: i.text, tokenlist[firstP+1: lastP])) # Sla de variabelenaam van de argumenten op in de AST

    braceIndex = returnBraceIndexes(tokenlist, lastP + 1, lastP + 1)
    if (type(braceIndex) == TBMPError):
        ast.error = braceIndex
        return ast
    firstB, lastB = braceIndex

    ast.codeSequence = tokenlist[firstB + 1: lastB ]
    ast.blocks = []
    return ast

# Nadat de ASTs gegenereerd zijn, worden de tokens geparsed naar blocks.
# generateBlocks :: AST -> AST
def generateBlocks(ast: AST) -> AST:
    value, tokenlist = detectParse(ast.codeSequence)
    if (value):
        ast.blocks.append(value)
        ast.codeSequence = tokenlist
        if(tokenlist and type(value) != TBMPError):
            return generateBlocks(ast)
        else:
            return ast
    return ast

# Main parse functie. Zoekt de functionindexes en roept generateBlocks aan per functionindex
# parse :: [Token] -> [AST]
def parse(tokens: List[Token]) -> List[AST]:
    functionindexes = findFunctionIndex(tokens)
    asts = list(map(lambda y: generateBlocks(y), list(map(lambda x: makeAST(tokens[x-1:]), functionindexes))))
    return asts
