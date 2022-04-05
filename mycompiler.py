from io import TextIOWrapper
from typing import Union, Tuple, List
from interpreter import expressionErrorDecorator
from myparser import AST, Expression, Loop, If, Function, Variable, Value

stackoffsetdict = {}
functionCount = 1

def openFile(fileName : str = "") -> TextIOWrapper:
    file = open(fileName or "tbmp.asm", "w")
    file.writelines((".cpu cortex-m0\n" "\n"))
    return file

def compile(compileInput: List[AST]):
    file = openFile()
    writeGlobalFunctionDefinitions(compileInput, file)

    list(map(lambda x: compileAST(x, file), compileInput))

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


# writes all the .global <functionname> in outputFile
def writeGlobalFunctionDefinitions(astList : List[AST], outputFile: TextIOWrapper):
    list(map(lambda x: outputFile.write(".global {0} \n".format(x.name)), astList))

def compileCalculationExpression(block : Expression, outputFile : TextIOWrapper) -> str:
    if type(block.args[0]) == Variable:
        loadVariable(block.args[0].name, "r2", outputFile)
        variable0 = "r2"
    elif type(block.args[0]) == Value:
        variable0 = "#" + block.args[0].content
    
    if type(block.args[1]) == Variable:
        loadVariable(block.args[1].name, "r3", outputFile)
        variable1 = "r3"
    elif type(block.args[1]) == Value:
        variable1 = "#" + block.args[1].content

    if block.function == "operator+":
        func = "add"
    if block.function == "operator-":
        func = "sub"
    

    string = "\t{0} r2, {1}, {2}\n".format(func, variable0, variable1)
    outputFile.write(string)
    return "r2"

def compileExpression(block : Expression, outputFile : TextIOWrapper):
    if block.function == "operator+" or block.function == "operator-":
        compileCalculationExpression(block, outputFile)
    if block.function == "operator=":
        compileDefinitionExpression(block, outputFile)
    if block.function == "operator>" or block.function == "operator<":
        compileComparisonExpression(block, outputFile)

def compileDefinitionExpression(block : Expression, outputFile : TextIOWrapper):
    if type(block.args[1]) == Expression:
        compileExpression(block.args[1], outputFile)
    elif type(block.args[1]) == Variable:
        loadVariable(block.args[1].name, "r2", outputFile)

    storeVariable(block.args[0].name, 'r2', outputFile)

def compileComparisonExpression(block : Expression, outputFile : TextIOWrapper):
    if type(block.args[0]) == Variable:
        loadVariable(block.args[0].name, "r2", outputFile)
        variable0 = "r2"
    elif type(block.args[0]) == Value:
        variable0 = "#" + block.args[0].content
    
    if type(block.args[1]) == Variable:
        loadVariable(block.args[1].name, "r3", outputFile)
        variable1 = "r3"
    elif type(block.args[1]) == Value:
        variable1 = "#" + block.args[1].content

    compare = "\tcmp {0}, {1}\n".format(variable0, variable1)
    outputFile.write(compare)

def compileGiveback(block : Expression, outputFile : TextIOWrapper):
    if type(block.args[0]) == Variable:
        loadVariable(block.args[0].name, "r2", outputFile)
        variable0 = "r2"
    elif type(block.args[0]) == Value:
        variable0 = "#" + block.args[0].content

    outputFile.write("\tmov r0, {0}\n".format(variable0))

def compileLoop(block : Loop, outputFile : TextIOWrapper):
    global functionCount
    branchLink = ".L{0}\n".format(functionCount)
    functionCount += 1
    outputFile.write(branchLink)
    compileComparisonExpression(block.Expression, outputFile)
    if block.Expression.function == "operator<":
        outputFile.write("\tbl {0}".format(branchLink))
    elif block.Expression.function == "operator>":
        outputFile.write("\tbg {0}".format(branchLink))

    list(map(lambda x: compileBlock(x, outputFile), block.Body))
    
    outputFile.write(".L{0}\n".format(functionCount))
    functionCount += 1


# compiles block and returns
def compileBlock(block : Union[Expression, If, Loop, Function], outputFile : TextIOWrapper) -> str:
    if type(block) == Expression:
        if block.function != "showme" and block.function != "giveback":
            compileExpression(block, outputFile)
        if block.function == "giveback":
            compileGiveback(block, outputFile)
    if type(block) == Loop:
        compileLoop(block, outputFile)

def compileAST(ast : AST, outputFile : TextIOWrapper):
    outputFile.write(ast.name + ":\n")
    outputFile.write("\tpush {r7, lr}\n")
    outputFile.write("\tsub sp, sp, #8\n")
    outputFile.write("\tadd r7, sp, #0\n")

    if ast.argumentList:
        storeVariable(ast.argumentList[0], "r0", outputFile)

    blockList = ast.blocks

    list(map(lambda x: compileBlock(x, outputFile), blockList))

    outputFile.write("\tmov sp, r7\n")
    outputFile.write("\tadd sp, sp, #8\n")
    outputFile.write("\tpop {r7, pc}\n")