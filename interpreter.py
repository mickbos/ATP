from myparser import Expression, Function, Variable, Value, Loop, If, AST
from typing import List, Union, Tuple
from collections import namedtuple
from lexer import TBMPError

# Error decorator om te checken of de namedTuple van type Error is
def namedtupleErrorDecorator(func): 
    def inner(exp: namedtuple, memory: dict) -> Union[int, dict]:
        if( type(exp) == TBMPError):
            memory = {"Error": exp}
            return False, memory
        return func(exp, memory)
    return inner

# Error decorator om te checken of een van de twee arguments errors zijn
def expressionErrorDecorator(func): 
    def inner(exp: namedtuple, memory: dict) -> Union[int, dict]:
        if( type(exp.args[0]) == TBMPError or type(exp.args[1]) == TBMPError):
            memory = {"Error": exp.args[0] if type(exp.args[0]) == TBMPError else exp.args[1]}
            return True, memory
        return func(exp, memory)
    return inner

# Functie die de returnwaarde van values, variabelen, expressies en functies teruggeeft
# returnValue :: Union(Value, Variable, Function, Expression) -> dict -> int
def returnValue(expinput: Union[Value, Variable, Function, Expression], memory: dict) -> int: 
    if(type(expinput) == Value):
        return int(expinput.content)
    if(type(expinput) == Variable):
        if(memory.get(expinput.name) == None):
            return None
        return memory.get(expinput.name)
    if(type(expinput) == Expression):
        return interpretNamedTuple(expinput, memory)[0]
    if(type(expinput) == Function):
        return interpretNamedTuple(expinput, memory)[0]
    
# Interpret functie om de loop te interpreten. Checkt eerst voor de expression en gaat dan de body interpreten
# interpretLoop :: Loop -> dict -> dict
def interpretLoop(exp: Loop, memory: dict) -> dict: 
    if(interpretOperator(exp.Expression, memory)[0]):
        memory = interpret(exp.Body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory


# Interpret functie voor if statements. Checkt voor expressie en voert daarna de correcte body uit
# interpretIf :: If -> dict -> dict
def interpretIf(exp: If, memory: dict) -> dict:
    if(interpretOperator(exp.Expression, memory)[0]): 
        memory = interpret(exp.Body, memory)
    else:
        if(exp.ElseBody):
            memory = interpret(exp.ElseBody, memory)
    return memory

# Interpret functie voor functies. Genereert eerst de function memory en roept interpret aan
# interpretFunction :: Function -> dict -> dict
def interpretFunction(exp: Function, memory: dict) -> dict: 
    functionBody = memory[exp.name]
    functionArgument = returnValue(exp.args, memory)
    functionMemory = {**dict(filter(lambda a: a if type(a[1]) == AST else None, memory.items())), **{'functionarguments': [functionArgument]}}
    return interpret(functionBody, functionMemory)

 # interpret functie voor het interpreten van giveback. 
def interpretGiveback(exp: Expression, memory) -> dict:
    value = returnValue(exp.args[0], memory)
    memory = {**memory, **{"giveback": value}}
    return memory

# Interpret functie voor operators. Checkt eerst de returnvalue van de arguments om zo mismatching te voorkomen
# interpretOperator :: Expression -> dict -> (int, dict)
def interpretOperator(exp: Expression, memory: dict) -> Tuple[int, dict]: 
    returnvalue0 = returnValue(exp.args[0], memory)
    returnvalue1 = returnValue(exp.args[1], memory)
    if(returnvalue0 is None and exp.function != "operator="): # Eerst checken of de expression arguments values hebben 
        memory = {"Error": TBMPError("{0} has no definition".format(exp.args[0]))}
        return False, memory
    if(returnvalue1 is None):
        memory = {"Error": TBMPError("{0} has no definition".format(exp.args[1]))}
        return False, memory
    else:
        if(exp.function == "operator="):
            if(type(exp.args[0] == Variable)):
                memory = {**memory, **{exp.args[0].name: returnvalue1}}
                return True, memory
            else:
                memory = {"Error": TBMPError("Can only sign a value to a variable")}
                return False, memory
        if(exp.function == "operator=="):
            return (returnvalue0 == returnvalue1), memory
        if(exp.function == "operator+"):
            return (returnvalue0 + returnvalue1), memory
        if(exp.function == "operator-"):
            return (returnvalue0 - returnvalue1), memory
        if(exp.function == "operator<"):
            return (returnvalue0 < returnvalue1), memory
        if(exp.function == "operator>"):
            return (returnvalue0 > returnvalue1), memory

# Functie die het interpreten van de namedtuple naar de goeie functie doorsluist. Single responsibility ftw
# interpretNamedTuple :: Union(Expression, Loop, If, Function) -> dict -> (int, dict)
@namedtupleErrorDecorator
def interpretNamedTuple(exp: Union[Expression, Loop, If, Function], memory: dict) -> Tuple[int, dict]: 
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
            return interpretOperator(exp, memory)
    else:
        memory = {"Error": TBMPError("Syntax error: {0} is not a viable keyword".format(exp.name))}
        return False, memory

# main interpret functie. Roept interpretNamedTuple aan en checkt of de blocklist gevuld is.
# interpret :: Union(AST, [Union(Expression, Loop, If, Function)]) -> dict -> dict
def interpret(interpretInput: Union[AST, List[Union[Expression, Loop, If, Function]]], memory : dict) -> dict:
    if( type(interpretInput) == AST ): # Wanneer je een functie aan het interpreten bent
        if( 'functionarguments' in memory and interpretInput.argumentList[0] not in memory):
            memory = {**memory, **(dict(zip(interpretInput.argumentList, memory['functionarguments'])))}
        blocklist = interpretInput.blocks
    else: # bodies van if en while 
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
