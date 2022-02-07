from myparser import Expression, Function, Variable, Value, Loop, If, AST, ParserError
from typing import List, Union, Tuple
from collections import namedtuple
from copy import copy

def returnValue(expinput, memory) -> Union[int, str]:
    if(type(expinput) == Value):
        if(expinput.content.isnumeric()):
            return int(expinput.content)
        else:
            return str(expinput.content[1:-1])
    if(type(expinput) == Variable):
        if(memory.get(expinput.name) == None):
            raise Exception("{0} has no definition".format(expinput.name))
        return memory.get(expinput.name)
    if(type(expinput) == Expression):
        memory = interpretNamedTuple(expinput, memory)[1]
        return returnValue(expinput.args[0], memory)
    if(type(expinput) == Function):
        return interpretNamedTuple(expinput, memory)[0]
    
def interpretLoop(exp: namedtuple, memory: dict) -> dict:
    if(interpretNamedTuple(*exp.Expression, memory)[0]):
        memory = interpret(exp.Body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory

def interpretIf(exp: namedtuple, memory: dict) -> dict:
    if(interpretNamedTuple(*exp.Expression, memory)[0]):
        memory = interpret(exp.Body, memory)
    else:
        if(exp.ElseBody):
            memory = interpret(exp.ElseBody, memory)
    return memory

def interpretFunction(exp: namedtuple, memory: dict):
    functionBody = memory[exp.name]
    functionMemory = {**dict(filter(lambda a: a if type(a[1]) == AST else None, memory.items())), **{'functionarguments': list(map(lambda l: returnValue(l, memory), exp.args))}}
    return interpret(functionBody, functionMemory)

def interpretExpression(exp: namedtuple, memory: dict):
    if(exp.function == "operator="):
        memory = {**memory, **{exp.args[0].name: returnValue(exp.args[1], memory)}}
        return True, memory
    if(exp.function == "operator=="):
        if(type(memory[exp.args[0].name] == type(returnValue(exp.args[1], memory)))):
            return (memory[exp.args[0].name] == returnValue(exp.args[1], memory)), memory
        else:
            raise TypeError("Cannot check equality operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnValue(exp.args[1], memory)))
    if(exp.function == "operator+"):
        if(type(returnValue(exp.args[0], memory) != int)):
            memory[exp.args[0].name] += returnValue(exp.args[1], memory)
            return True, memory
        else:
            raise TypeError("Cannot preform + operation on {0}, {1} because one isn't an integer".format(exp.args[0], exp.args(1)))
    if(exp.function == "operator-"):
        if(type(returnValue(exp.args[0], memory) != int)):
            memory[exp.args[0].name] -= returnValue(exp.args[1], memory)
            return True, memory
        else:
            raise TypeError("Cannot preform - operation on {0}, {1} because one isn't an integer".format(exp.args[0], exp.args(1)))
    if(exp.function == "operator<"):
        if(type(memory[exp.args[0].name] == type(returnValue(exp.args[1], memory)))):
            return (memory[exp.args[0].name] < returnValue(exp.args[1], memory)), memory
        else:
            raise TypeError("Cannot check less than operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnValue(exp.args[1], memory)))
    if(exp.function == "operator>"):
        if(type(memory[exp.args[0].name] == type(returnValue(exp.args[1], memory)))):
            return (memory[exp.args[0].name] > returnValue(exp.args[1], memory)), memory
        else:
            raise TypeError("Cannot check greater than operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnValue(exp.args[1], memory)))
    
def interpretNamedTuple(exp: namedtuple, memory: dict) -> Tuple[Union[bool, Union[str, int]], dict]:
    print(exp)
    print(memory)
    if( type(exp) == Loop):
        return True, interpretLoop(exp, memory)
    if( type(exp) == If):
        return True, interpretIf(exp, memory)
    if( type(exp) == Function):
        if( exp.name in memory): #For the line under here: interpret the list of blocks in combination with a memory filled with every functioncall and a zip between the arguments given with the function and the 
            return interpretFunction(exp, memory)['giveback'][0], memory
        memory = {"Error": ParserError("{0} is not a defined function".format(exp.name))}
        return memory
    if( type(exp) == Expression ):
        if(type(exp.args[0]) == Variable or exp.function == "showme" or exp.function == "giveback"):
            if(exp.function == "showme"):
                print(*(list(map(lambda x: returnValue(x, memory), exp.args))))
                return True, memory
            if(exp.function == "giveback"):
                memory = {**memory, **{"giveback": list(map(lambda i: returnValue(i, memory), exp.args))}}
                return True, memory
            else:
                return interpretExpression(exp, memory)
        else:
            memory = {"Error": ParserError("Cannot use {0} as variable".format(type(exp.args[0]).__name__))}
            return True, memory
    

def interpret(ast : List, memory : dict):
    if( type(ast) == AST ):
        if( 'functionarguments' in memory and ast.argumentList[0] not in memory):
            memory = {**memory, **(dict(zip(ast.argumentList, memory['functionarguments'])))}
        blocklist = ast.blocks
    else:
        blocklist = ast
    if ( len(blocklist) > 1 ):
        memory = interpretNamedTuple(blocklist[0], memory)[1]
        if( (memory.get("Error"))):
            print(memory.get("Error").Errormessage)
            return
        return interpret(blocklist[1:], memory)
    else:
        memory = interpretNamedTuple(blocklist[0], memory)[1]
        if( memory.get("Error")):
            print(memory.get("Error").Errormessage)
            return
        return memory
