from myparser import Expression, Function, Variable, Value, Loop, If, AST
from typing import List, Union, Tuple
from collections import namedtuple
from lexer import TBMPError

def errorDecorator(func): # Error decorator om zo de afhandeling van de errors uit de normale code te halen
    def inner(exp: namedtuple, memory: dict):
        if( type(exp) == TBMPError):
            memory = {"Error": exp}
            return False, memory
        return func(exp, memory)
    return inner


def returnValue(expinput, memory) -> Union[int, str]: # Functie die de returnwaarde van values, variabelen, expressies en functies teruggeeft
    if(type(expinput) == Value):
        if(expinput.content.isnumeric()):
            return int(expinput.content)
        else:
            return str(expinput.content[1:-1])
    if(type(expinput) == Variable):
        if(memory.get(expinput.name) == None):
            return None
        return memory.get(expinput.name)
    if(type(expinput) == Expression):
        memory = interpretNamedTuple(expinput, memory)[1]
        return returnValue(expinput.args[0], memory)
    if(type(expinput) == Function):
        return interpretNamedTuple(expinput, memory)[0]
    
def interpretLoop(exp: namedtuple, memory: dict) -> dict:
    if(interpretExpression(exp.Expression, memory)[0]):
        memory = interpret(exp.Body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory

def interpretIf(exp: namedtuple, memory: dict) -> dict:
    if(interpretExpression(exp.Expression, memory)[0]):
        memory = interpret(exp.Body, memory)
    else:
        if(exp.ElseBody):
            memory = interpret(exp.ElseBody, memory)
    return memory

def interpretFunction(exp: namedtuple, memory: dict) -> dict:
    functionBody = memory[exp.name]
    functionArguments = returnValue(exp.args, memory)
    functionMemory = {**dict(filter(lambda a: a if type(a[1]) == AST else None, memory.items())), **{'functionarguments': [functionArguments]}}
    return interpret(functionBody, functionMemory)

def interpretGiveback(exp: namedtuple, memory) -> dict:
    value = returnValue(exp.args[0], memory)
    memory = {**memory, **{"giveback": value}}
    return memory

def interpretExpression(exp: namedtuple, memory: dict) -> Tuple[Union[int, bool], dict]:
    if( type(exp.args[0]) == TBMPError or type(exp.args[1]) == TBMPError):
        memory = {"Error": exp.args[0] if type(exp.args[0]) == TBMPError else exp.args[1]}
        return True, memory
    returnvalue0 = returnValue(exp.args[0], memory)
    returnvalue1 = returnValue(exp.args[1], memory)
    if(returnvalue0 is None and exp.function != "operator="):
        memory = {"Error": TBMPError("{0} has no definition".format(exp.args[0]))}
        return True, memory
    elif(returnvalue1 is None and exp.function != "operator="):
        memory = {"Error": TBMPError("{0} has no definition".format(exp.args[1]))}
        return True, memory
    else:
        if(exp.function == "operator="):
            if(type(exp.args[0] == Variable)):
                memory = {**memory, **{exp.args[0].name: returnvalue1}}
                return True, memory
            else:
                memory = {"Error": TBMPError("Can only sign a value to a variable")}
                return False, memory
        if(exp.function == "operator=="):
            if(type(returnvalue0) == type(returnvalue1)):
                return (memory[exp.args[0].name] == returnvalue1), memory
            else:
                memory = {"Error": TBMPError("Cannot check equality operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnvalue1))}
                return True, memory
        if(exp.function == "operator+"):
            if(type(returnvalue0) == int and type(returnvalue1) == int):
                memory[exp.args[0].name] += returnvalue1
                return memory[exp.args[0].name], memory
            else:
                memory = {"Error": TBMPError("Cannot preform + operation on {0}, {1} because one isn't of type Int".format(exp.args[0], exp.args[1]))}
                return True, memory
        if(exp.function == "operator-"):
            if(type(returnvalue0) == int and type(returnvalue1) == int):
                memory[exp.args[0].name] -= returnvalue1
                return memory[exp.args[0].name], memory
            else:
                memory = {"Error": TBMPError("Cannot preform + operation on {0}, {1} because one isn't of type Int".format(exp.args[0], exp.args[1]))}
                return True, memory
        if(exp.function == "operator<"):
            if(type(returnvalue1) == type(returnvalue1)):
                f = memory[exp.args[0].name]
                return (memory[exp.args[0].name] < returnvalue1), memory
            else:
                memory = {"Error": TBMPError("Cannot check less than operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnvalue1))}
                return True, memory
        if(exp.function == "operator>"):
            if(type(returnvalue1) == type(returnvalue1)):
                return (memory[exp.args[0].name] > returnvalue1), memory
            else:
                memory = {"Error": TBMPError("Cannot check greater than operation. Type of {0} and {1} are not the same".format(memory[exp.args[0].name], returnvalue1))}
                return True, memory

@errorDecorator
def interpretNamedTuple(exp: namedtuple, memory: dict) -> Tuple[Union[str, int, bool], dict]:
    if( type(exp) == Loop):
        return True, interpretLoop(exp, memory)
    if( type(exp) == If):
        return True, interpretIf(exp, memory)
    if( type(exp) == Function):
        if( exp.name in memory): 
            return interpretFunction(exp, memory)['giveback'], memory
        memory = {"Error": TBMPError("{0} is not a defined function".format(exp.name))}
        return False, memory
    if( type(exp) == Expression ):
        if(exp.function == "showme" or exp.function == "giveback"):
            if(exp.function == "showme"):
                print(*(list(map(lambda x: returnValue(x, memory), exp.args))))
                return True, memory
            if(exp.function == "giveback"):
                return True, interpretGiveback(exp, memory)
        else:
            return interpretExpression(exp, memory)
    else:
        memory = {"Error": TBMPError("Syntax error: {0} is not a viable keyword".format(exp.name))}
        return False, memory

def interpret(interpretInput: Union[AST, List[Union[Expression, Loop, If, Function]]], memory : dict) -> dict:
    if( type(interpretInput) == AST ):
        if( 'functionarguments' in memory and interpretInput.argumentList[0] not in memory):
            memory = {**memory, **(dict(zip(interpretInput.argumentList, memory['functionarguments'])))}
        blocklist = interpretInput.blocks
    else:
        blocklist = interpretInput
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
