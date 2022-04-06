from io import TextIOWrapper
from typing import Union, Tuple, List
from interpreter import expressionErrorDecorator
from myparser import AST, Expression, Loop, If, Function, Variable, Value

stackoffsetdict = {}
functionCount = 1
functions = []

def openFile(fileName : str = ""):
    file = open(fileName or "tbmp.asm", "w")
    file.writelines((".cpu cortex-m0\n" "\n"))
    return file

def compile(compileInput: List[AST]):
    file = openFile()
    writeGlobalFunctionDefinitions(compileInput, file)

    list(map(lambda x: compileAST(x, file), compileInput))
    
# writes all the .global <functionname> in outputFile
def writeGlobalFunctionDefinitions(astList : List[AST], outputFile: TextIOWrapper):
    list(map(lambda x: outputFile.write(".global {0} \n".format(x.name)), astList))


# Throw in a variable to be stored in register. Returns register address
def loadVariable(variable : str, targetRegister : str, fileOutput : TextIOWrapper) -> str:
    argumentOffset = stackoffsetdict.get(variable)
    if argumentOffset is None:
        print("Geen variabele gevonden")
    fileOutput.write("\tldr {0}, [r7, #{1}]\n".format(targetRegister, argumentOffset))

def storeVariable(variable : str, sourceRegister : str, fileOutput : TextIOWrapper) -> str:
    argumentOffset = stackoffsetdict.get(variable)
    if argumentOffset is None:
        stackoffsetdict[variable] = (len(stackoffsetdict) + 1) * 4
        argumentOffset = stackoffsetdict[variable]
    fileOutput.write("\tstr {0}, [r7, #{1}]\n".format(sourceRegister, argumentOffset))

def returnValue(block : Union[Expression, Value, Variable, Function], outputFile : TextIOWrapper, targetRegister : str):
    if type(block) == Expression:
        compileExpression(block, outputFile, targetRegister)
    elif type(block) == Variable:
        loadVariable(block.name, targetRegister, outputFile)
    elif type(block) == Value:
        outputFile.write("\tmov {0}, #{1}\n".format(targetRegister, block.content))
    elif type(block) == Function:
        compileFunctionCall(block, outputFile)
        outputFile.write("\tmov {0}, r0\n".format(targetRegister))



def compileExpression(block : Expression, outputFile : TextIOWrapper, targetRegister : str):
    if block.function == "operator+" or block.function == "operator-":
        compileCalculationExpression(block, outputFile, targetRegister)
    if block.function == "operator=":
        compileDefinitionExpression(block, outputFile)
    if block.function == "operator>" or block.function == "operator<":
        compileComparisonExpression(block, outputFile)

def compileCalculationExpression(block : Expression, outputFile : TextIOWrapper, targetRegister : str) -> str:
    returnValue(block.args[0], outputFile, "r2")
    returnValue(block.args[1], outputFile, "r3")

    if block.function == "operator+":
        func = "add"
    if block.function == "operator-":
        func = "sub"
    
    string = "\t{0} {1}, {2}, {3}\n".format(func, targetRegister, "r2", "r3")
    outputFile.write(string)

def compileDefinitionExpression(block : Expression, outputFile : TextIOWrapper):
    returnValue(block.args[1], outputFile, "r2")
    valueLocation = "r2"

    storeVariable(block.args[0].name, valueLocation, outputFile)

def compileComparisonExpression(block : Expression, outputFile : TextIOWrapper):
    returnValue(block.args[0], outputFile, "r2")
    returnValue(block.args[1], outputFile, "r3")

    compare = "\tcmp {0}, {1}\n".format("r2", "r3")
    outputFile.write(compare)

def compileGiveback(block : Expression, outputFile : TextIOWrapper):
    returnValue(block.args[0], outputFile, "r0")

def compileLoop(block : Loop, outputFile : TextIOWrapper):
    global functionCount
    branchLink = ".L{0}:\n".format(functionCount)
    functionCount += 1
    outputFile.write(branchLink)
    compileComparisonExpression(block.Expression, outputFile)
    if block.Expression.function == "operator<":
        outputFile.write("\tbge .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator>":
        outputFile.write("\tble .L{0}\n".format(functionCount))

    list(map(lambda x: compileBlock(x, outputFile), block.Body))
    outputFile.write("\tb .L{0}\n".format(functionCount - 1))
    
    outputFile.write(".L{0}:\n".format(functionCount))
    functionCount += 1

def compileFunctionCall(block : Function, outputFile : TextIOWrapper):
    returnValue(block.args, outputFile, "r2")

    outputFile.write("\tmov r0, {0}\n".format("r2"))
    outputFile.write("\tbl {0}\n".format(block.name))

def compileIf(block : If, outputFile : TextIOWrapper):
    global functionCount
    compileComparisonExpression(block.Expression, outputFile)
    if block.Expression.function == "operator<":
        outputFile.write("\tbge .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator>":
        outputFile.write("\tble .L{0}\n".format(functionCount))
    elif block.Expression.function == "operator==":
        outputFile.write("\tbne .L{0}\n".format(functionCount))

    list(map(lambda x: compileBlock(x, outputFile), block.Body))

    if block.ElseBody:
        outputFile.write("\tb .L{0}\n".format(functionCount + 1))
        outputFile.write(".L{0}:\n".format(functionCount))
        functionCount += 1

        list(map(lambda y: compileBlock(y, outputFile), block.ElseBody))

    outputFile.write(".L{0}:\n".format(functionCount))
    functionCount += 1

# compiles block and returns
def compileBlock(block : Union[Expression, If, Loop, Function], outputFile : TextIOWrapper):
    if type(block) == Expression:
        if block.function != "showme" and block.function != "giveback":
            compileExpression(block, outputFile, "r2")
        if block.function == "giveback":
            compileGiveback(block, outputFile)
    if type(block) == Loop:
        compileLoop(block, outputFile)
    if type(block) == If:
        compileIf(block, outputFile)



def compileAST(ast : AST, outputFile : TextIOWrapper):
    outputFile.write(ast.name + ":\n")
    outputFile.write("\tpush {r7, lr}\n")
    outputFile.write("\tsub sp, sp, #16\n")
    outputFile.write("\tadd r7, sp, #0\n")

    if ast.argumentList:
        storeVariable(ast.argumentList[0], "r0", outputFile)

    blockList = ast.blocks

    list(map(lambda x: compileBlock(x, outputFile), blockList))

    outputFile.write("\tmov sp, r7\n")
    outputFile.write("\tadd sp, sp, #16\n")
    outputFile.write("\tpop {r7, pc}\n")