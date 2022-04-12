from ast import arg
from inspect import currentframe, stack
from io import TextIOWrapper
from typing import Union, Tuple, List
from interpreter import expressionErrorDecorator
from myparser import AST, Expression, Loop, If, Function, Variable, Value

stackoffsetdict = {}
functionCount = 1
functions = []

# Opens the file
def openFile(fileName : str = "") -> TextIOWrapper:
    file = open(fileName or "tbmp.asm", "w")
    file.writelines((".cpu cortex-m0\n" "\n"))
    return file

def compile(compileInput: List[AST]) -> None:
    file = openFile()
    writeGlobalFunctionDefinitions(compileInput, file)

    list(map(lambda x: compileAST(x, file), compileInput))
    
# writes all the .global <functionname> in outputFile
def writeGlobalFunctionDefinitions(astList : List[AST], outputFile: TextIOWrapper) -> None:
    list(map(lambda x: outputFile.write(".global {0} \n".format(x.name)), astList))


# Throw in a variable to be stored in register. Returns register address
def loadVariable(variable : str, targetRegister : str, currentFunction: str, fileOutput : TextIOWrapper) -> None:
    functiondict = stackoffsetdict.get(currentFunction)

    argumentOffset = functiondict.get(variable)
    if argumentOffset is None:
        print("Geen variabele gevonden")
    fileOutput.write("\tldr {0}, [r7, #{1}]\n".format(targetRegister, argumentOffset))

def storeVariable(variable : str, sourceRegister : str, currentFunction: str, fileOutput : TextIOWrapper) -> None:
    functiondict = stackoffsetdict.get(currentFunction)
    if functiondict is None:
        stackoffsetdict[currentFunction] = {}
        functiondict = stackoffsetdict[currentFunction]

    argumentOffset = functiondict.get(variable)
    if argumentOffset is None:
        stackoffsetdict[currentFunction][variable] = (len(stackoffsetdict[currentFunction]) + 1) * 4
        argumentOffset = stackoffsetdict[currentFunction][variable]
    fileOutput.write("\tstr {0}, [r7, #{1}]\n".format(sourceRegister, argumentOffset))

def returnValue(block : Union[Expression, Value, Variable, Function],  currentFunction: str, targetRegister : str , outputFile : TextIOWrapper) -> None:
    if type(block) == Expression:
        compileExpression(block, currentFunction, outputFile, targetRegister)
    elif type(block) == Variable:
        loadVariable(block.name, targetRegister, currentFunction, outputFile)
    elif type(block) == Value:
        outputFile.write("\tmov {0}, #{1}\n".format(targetRegister, block.content))
    elif type(block) == Function:
        compileFunctionCall(block, currentFunction, outputFile)
        outputFile.write("\tmov {0}, r0\n".format(targetRegister))



def compileExpression(block : Expression, currentFunction: str, targetRegister : str, outputFile : TextIOWrapper) -> None:
    if block.function == "operator+" or block.function == "operator-":
        compileCalculationExpression(block, currentFunction, outputFile, targetRegister)
    if block.function == "operator=":
        compileDefinitionExpression(block, currentFunction, outputFile)
    if block.function == "operator>" or block.function == "operator<":
        compileComparisonExpression(block, currentFunction, outputFile)

def compileCalculationExpression(block : Expression, currentFunction: str, targetRegister : str, outputFile : TextIOWrapper) -> None:
    returnValue(block.args[0], currentFunction, "r2", outputFile)
    returnValue(block.args[1], currentFunction, "r3", outputFile)

    if block.function == "operator+":
        func = "add"
    if block.function == "operator-":
        func = "sub"
    
    string = "\t{0} {1}, {2}, {3}\n".format(func, targetRegister, "r2", "r3")
    outputFile.write(string)

def compileDefinitionExpression(block : Expression, currentFunction: str, outputFile : TextIOWrapper) -> None:
    returnValue(block.args[1], currentFunction, "r2", outputFile)
    valueLocation = "r2"

    storeVariable(block.args[0].name, valueLocation, currentFunction, outputFile)

def compileComparisonExpression(block : Expression, currentFunction: str, outputFile : TextIOWrapper) -> None:
    returnValue(block.args[0], currentFunction, "r2", outputFile)
    returnValue(block.args[1], currentFunction, "r3", outputFile)

    compare = "\tcmp {0}, {1}\n".format("r2", "r3")
    outputFile.write(compare)

def compileGiveback(block : Expression, currentFunction :str, outputFile : TextIOWrapper) -> None:
    returnValue(block.args[0], currentFunction,  "r0", outputFile)

def compileLoop(block : Loop, currentFunction: str, outputFile : TextIOWrapper) -> None:
    global functionCount
    branchLink = ".L{0}:\n".format(functionCount)
    functionCount += 1
    outputFile.write(branchLink)
    compileComparisonExpression(block.Expression, currentFunction, outputFile)
    if block.Expression.function == "operator<":
        outputFile.write("\tbge .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator>":
        outputFile.write("\tble .L{0}\n".format(functionCount))

    list(map(lambda x: compileBlock(x, currentFunction, outputFile), block.Body))
    outputFile.write("\tb .L{0}\n".format(functionCount - 1))
    
    outputFile.write(".L{0}:\n".format(functionCount))
    functionCount += 1

def compileFunctionCall(block : Function, currentFunction: str, outputFile : TextIOWrapper) -> None:
    returnValue(block.args, currentFunction, "r2", outputFile)

    outputFile.write("\tmov r0, {0}\n".format("r2"))
    outputFile.write("\tbl {0}\n".format(block.name))

def compileIf(block : If, currentFunction: str, outputFile : TextIOWrapper):
    global functionCount
    compileComparisonExpression(block.Expression, currentFunction, outputFile)
    if block.Expression.function == "operator<":
        outputFile.write("\tbge .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator>":
        outputFile.write("\tble .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator==":
        outputFile.write("\tbne .L{0}\n".format(functionCount))

    list(map(lambda x: compileBlock(x, currentFunction, outputFile), block.Body))

    if block.ElseBody:
        outputFile.write("\tb .L{0}\n".format(functionCount + 1))
        outputFile.write(".L{0}:\n".format(functionCount))
        functionCount += 1

        list(map(lambda y: compileBlock(y, currentFunction, outputFile), block.ElseBody))

    outputFile.write(".L{0}:\n".format(functionCount))
    functionCount += 1

# compiles block and returns
def compileBlock(block : Union[Expression, If, Loop, Function], currentFunction: str, outputFile : TextIOWrapper) -> None:
    if type(block) == Expression:
        if block.function != "showme" and block.function != "giveback":
            compileExpression(block, currentFunction, "r2", outputFile)
        if block.function == "giveback":
            compileGiveback(block, currentFunction, outputFile)
    if type(block) == Loop:
        compileLoop(block, currentFunction, outputFile)
    if type(block) == If:
        compileIf(block, currentFunction, outputFile)
    if type(block) == Function:
        compileFunctionCall(block, currentFunction, outputFile)

def storeParameters(argumentList : List, i : int, currentFunction: str, outputFile : TextIOWrapper):
    if argumentList:
        storeVariable(argumentList[0], "r" + str(i), currentFunction, outputFile)
        storeParameters(argumentList[1:], i + 1, currentFunction, outputFile)

def compileAST(ast : AST, outputFile : TextIOWrapper) -> None:
    outputFile.write(ast.name + ":\n")
    outputFile.write("\tpush {r7, lr}\n")
    outputFile.write("\tsub sp, sp, #16\n")
    outputFile.write("\tadd r7, sp, #0\n")

    functionName = ast.name

    # if ast.argumentList:
    #     storeVariable(ast.argumentList[0], "r0", functionName, outputFile)
    storeParameters(ast.argumentList, 0, functionName, outputFile)

    blockList = ast.blocks

    list(map(lambda x: compileBlock(x, functionName, outputFile), blockList))

    outputFile.write("\tmov sp, r7\n")
    outputFile.write("\tadd sp, sp, #16\n")
    outputFile.write("\tpop {r7, pc}\n")