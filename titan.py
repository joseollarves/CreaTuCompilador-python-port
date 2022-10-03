# Port hecho en Python del Proyecto de un compilador con implementacion minima para ser autocontenido.
# Originalmente hecho en Pascal

# La gran mayoria de los comentarios en el proyecto son del codigo original
# con el objetivo de ser lo mas fiel posible al original


# El compilador tiene una implementación simple, porque el objetivo final es poder
# hacer a este compilador, autocontenido, es decir que se pueda compilar a si mismo.
# Por ello, no se usarán opciones avanzadas del lenguaje, solo las funciones básicas,
# y las estructuras más simples. No se implementan los bucles REPEAT, o FOR.

# Los tipos de datos son solamente dos:
# - Enteros. Con signo, ocupan 32 bits.
# - Cadenas. Ocupan 255 bytes.
# Además se soportan arreglos de hasta 255 elementos de estos tipos de datos.

# Se consideran 3 tipos de almacenamiento:
# 1. Constante. Se guarda directamente el valor de la expresión.
# 2 . Variables. Se guarda la dirección de la variables.
# 3. Expresión. Se guarda el resultado en un registro de trabajo.

# Adicionalmente se permite manejar, en algunos casos, los almacenamientos:
# 4. Variable referenciada por constante.
# 5. Variable referenciada por variable.

# Estos almacenamientos se usan para implementar arreglos.

# Los registros de trabajo, son los que se usan para devolver el resultado de las
# expresiones. Son dos:
# * El registro EAX, para devolver valores numéricos.
# * La variable _regstr para devolver valores de cadena.


# Manejo de codigo fuente

# Importamos todo lo necesario
from copy import copy


# Declaramos las variables necesarias.
idxLine: int
srcLine: str  # Linea leida actualmente
srcRow: int  # Numero de linea actual

# Campos relativos a la lectura de tokens
srcChar: bytes  # Caracter leido actualmente

srcToken: str
srcToktyp: int  # Tipo de token
# 0 -> Fin de línea
# 1 -> Espacio
# 2 -> Identificador: "var1", "VARIABLE"
# 3 -> Literal numérico: 123, -1
# 4 -> Literal cadena: "Hola", "hey"
# 5 -> Comentario
# 9 -> Desconocido.


# Campos adicionales
MsjError: str
# Bandera para indicar que estamos dentro de la seccion de variables.
InVarSec: int
# Bandera para determinar si estamos generando la primera instruccion.
FirstCode: int


# Informacion sobre variables
nVars: int
varNames: str = [0] * 255
varType: int = [0] * 255
varArrSiz: int = [0] * 255


# Variables de trabajo
curVarName: str
curVarType: int
curVarArSiz: int


# Variable a asignar
asgVarName: str
asgVarType: int


# Campos para arreglos
idxStorag: int
idxCteInt: int
idxVarNam: str


# Expresiones: "res"
resType: int   # Tipo de dato:
# 1 -> int
# 2 -> str


resStorag: int  # Almacenamiento del resultado
# 0 -> Constante
# 1 -> Variable
# 2 -> Expresion
# 1000 -> Sin almacenamiento


resVarIdx: int # Indice al resultado cuando es variable
resVarNam: str  # Nombre de la variable cuando el resultado es variable
resCteInt: int  # Resultado entero cuando es constante
resCteStr: str  # Resultado cadena cuando es constante


# Operador: "Op1"
op1Type: int    # Tipo de dato:
op1Storag: int  # Almacenamiento del resultado:
op1VarNam: str  # Nombre de la variable cuando el resultado es variable
op1CteInt: int  # Resultado entero cuando es constante
op1CteStr: str  # Resultado cadena cuando es constante


# Operador: "Op2"
op2Type: int    # Tipo de dato:
op2Storag: int  # Almacenamiento del resultado:
op2VarNam: str  # Nombre de la variable cuando el resultado es variable
op2CteInt: int  # Resultado entero cuando es constante
op2CteStr: str  # Resultado cadena cuando es constante


# Variables internas
_regstr: str    # Registro para cadenas
constr: str     # Nombre de constante string usada actualmente
nconstr: int    # Numero de constante string creada


# Aqui se declaraba la funcion EvaluateExpression mas no se llenaba,
# eso no funciona en Python asi que la declaramos despues.


# Analisis Lexico


def EndOfLine():
    global idxLine
    global srcLine

    if idxLine > len(srcLine) - 1:
        return 1
    else:
        return 0


def EndOfFile():
    if EndOfLine() != 0:
        return 1
    else:
        return 0


def NextLine(inFile):
    global srcLine
    global srcRow
    global idxLine

    srcLine = inFile.readline()  # Lee nueva linea
    srcRow += 1
    idxLine = 0  # Apunta al primer caracter


def ReadChar():
    global srcChar
    global srcLine
    global idxLine

    # Lee el caracter actual y actualiza srcChar.
    srcChar = ord(srcLine[idxLine])


def NextChar():
    global idxLine
    idxLine += 1  # Pasa al siguiente caracter


def NextCharIsSlash():
    # Incrementa idxLine. Pasa al siguiente caracter.

    global idxLine
    global srcLine

    if idxLine > len(srcLine) - 1:
        return 0

    if srcLine[idxLine + 1] == '/':
        return 1

    return 0


def IsAlphaUp():
    # Indica si el caracter en "srcChar" es alfabético mayúscula.

    global srcChar

    if 'A' <= chr(srcChar) <= 'Z':
        return 1
    else:
        return 0


def IsAlphaDown():
    # Indica si el caracter en "srcChar" es alfabético minuscula.

    global srcChar

    if 'a' <= chr(srcChar) <= 'z':
        return 1
    else:
        return 0


def IsNumeric():
    # Indica si el caracter en "srcChar" es numerico.

    global srcChar

    if '0' <= chr(srcChar) <= '9':
        return 1
    else:
        return 0


def ExtractIdentifier():

    global srcToken
    global srcToktyp
    global srcChar

    IsToken: int  # Variable temporal
    srcToken = ''
    srcToktyp = 2
    IsToken = 1

    while IsToken == 1:
        srcToken += chr(srcChar)  # Acumula
        NextChar()  # Pasa al siguiente

        if EndOfLine() == 1:
            return  # No hay mas caracteres

        ReadChar()  # Lee siguiente en srcChar
        IsToken = IsAlphaUp() or IsAlphaDown()
        IsToken = IsToken or IsNumeric()


def ExtractSpace():
    global srcToken
    global srcToktyp
    global srcChar

    IsToken: int  # Variable temporal
    srcToken = ''
    srcToktyp = 1
    IsToken = 1

    while IsToken == 1:
        srcToken += chr(srcChar)  # Acumula
        NextChar()  # Pasa al siguiente

        if EndOfLine() == 1:
            return  # No hay mas caracteres

        ReadChar()  # Lee siguiente en srcChar

        if srcChar == ord(' '):
            IsToken = 1
        else:
            IsToken = 0


def ExtractNumber():

    global srcToken
    global srcToktyp
    global srcChar

    IsToken: int  # Variable temporal

    srcToken = ''
    srcToktyp = 3
    IsToken = 1

    while IsToken == 1:
        srcToken += chr(srcChar)  # Acumula
        NextChar()  # Pasa al siguiente

        if EndOfLine() == 1:
            return  # No hay mas caracteres

        ReadChar()  # Lee siguiente en srcChar
        IsToken = IsNumeric()


def ExtractString():

    global srcToken
    global srcToktyp
    global srcChar

    IsToken: int  # Variable temporal
    srcToken = ''
    srcToktyp = 4
    IsToken = 1

    while IsToken == 1:
        srcToken += chr(srcChar)  # Acumula
        NextChar()  # Pasa al siguiente

        if EndOfLine() == 1:
            return  # No hay mas caracteres

        ReadChar()  # Lee siguiente en srcChar

        if srcChar != ord('"'):
            IsToken = 1
        else:
            IsToken = 0

    NextChar()  # Toma la comilla final
    srcToken += '"'  # Acumula


def ExtractComment():
    global srcToken
    global srcToktyp
    global srcChar

    srcToken = ''
    srcToktyp = 5

    while EndOfLine() == 0:
        srcToken += chr(srcChar)  # Acumula
        NextChar()  # Toma caracter


def NextToken(inFile):
    # Lee un token y devuelve el texto en srcToken y el tipo en srcTokytp.
    # Mueve la posicion de lectura al siguiente token.
    global srcToktyp
    global srcToken
    global srcChar

    srcToktyp = 9  # Desconocido por defecto

    if EndOfFile() == 1:
        srcToken = ''
        srcToktyp = 0  # Fin de linea
        return

    if EndOfLine() == 1:
        srcToken = ''
        srcToktyp = 0
        NextLine(inFile)

    else:
        # Hay caracteres por leer en la linea
        ReadChar()  # Lee en srcChar

        if IsAlphaUp() == 1 or IsAlphaDown() == 1 or srcChar == ord('_'):
            ExtractIdentifier()
            return

        if IsNumeric() == 1:
            ExtractNumber()
            return

        if srcChar == ord(' '):
            ExtractSpace()
            return

        if srcChar == ord('"'):
            ExtractString()
            return

        if srcChar == ord('/'):
            if NextCharIsSlash() == 1:
                ExtractComment()
                return

        srcToken = chr(srcChar)  # Acumula

        srcToktyp = 9

        NextChar()  # Pasa al siguiente


def TrimSpaces(inFile):
    global srcTokytp

    while srcToktyp == 1 or srcToktyp == 5:
        NextToken(inFile)  # Pasa al siguiente.


def GetLastToken(inFile):
    # Toma el ultimo token de una linea. Si hay algo mas que no sean espacios o comentarios,
    # genera error de error.
    global srcToktyp
    global MsjError
    global srcToken

    NextToken(inFile)  # Toma ultimo token.
    TrimSpaces(inFile)

    if srcToktyp != 0:
        MsjError = 'Error de sintaxis: ' + srcToken
        return


def CaptureChar(c: int, inFile):
    # Toma el caracter como token. Si no encuentra, genera mensaje de error.
    global srcToken
    global MsjError

    TrimSpaces(inFile)
    if srcToken != chr(c):
        MsjError = 'Se esperaba: ' + chr(c)
        return
    NextToken(inFile)  # Toma el caracter


# Analisis Sintactico y Semantico


def ParserVar(inFile, outFile):
    # Hace el analisis sintactico para la declaracion de variables.
    global srcToktyp
    global MsjError
    global nVars
    global varNames
    global varType
    global varArrSiz
    global srcToken

    varName: str
    typName: str
    arrSize: int

    NextToken(inFile)  # Toma el var
    TrimSpaces(inFile)  # Quita espacios

    if srcToktyp != 2:
        MsjError = 'Se esperaba un identificador.'
        return

    varName = srcToken
    NextToken(inFile)  # Toma nombre de variable
    TrimSpaces(inFile)

    # Lee tipo
    if srcToken == '[':
        # Es un arreglo de algun tipo
        NextToken(inFile)  # Toma el token
        TrimSpaces(inFile)

        if srcToktyp != 3:
            MsjError = 'Se esperaba numero.'

        arrSize = int(srcToken)  # Tamano del arreglo
        NextToken(inFile)

        CaptureChar(ord(']'), inFile)

        if MsjError != '':
            return
        # Se espera ':'

        CaptureChar(ord(':'), inFile)

        if MsjError != '':
            return
        # Debe seguir tipo comun

        NextToken(inFile)
        typName = srcToken

        if typName == 'integer':
            # GetLastToken(inFile)  # Debe terminar la linea

            if MsjError != '':
                return

            outFile.write('   ' + varName + ' DD ' +
                          str(arrSize) + ' dup(0)\n')

            # Registra variable
            varNames[nVars] = varName
            varType[nVars] = 1  # Integer
            varArrSiz[nVars] = arrSize  # Es arreglo
            nVars += 1

        elif typName == 'string':
            # GetLastToken(inFile)  # Debe terminar la linea

            if MsjError != '':
                return

            outFile.write('   ' + varName + ' DB ' +
                          256 * arrSize + ' dup(0)\n')

            # Registra variable
            varNames[nVars] = varName
            varType[nVars] = 2  # String
            varArrSiz[nVars] = arrSize  # Es arreglo
            nVars += 1

        else:
            MsjError = 'Tipo desconocido: ' + typName
            return

    elif srcToken == ':':  # Es declaracion de tipo comun

        NextToken(inFile)
        TrimSpaces(inFile)
        typName = srcToken

        if typName == 'integer':

            # GetLastToken(inFile)  # Debe terminar la linea

            if MsjError != '':
                return

            outFile.write('    ' + varName + ' DD 0\n')

            # Registra variable
            varNames[nVars] = varName
            varType[nVars] = 1  # Integer
            varArrSiz[nVars] = 0  # No es arreglo
            nVars += 1

        elif typName == 'string':
            # GetLastToken(inFile)  # Debe terminar la linea

            if MsjError != '':
                return

            outFile.write('   ' + varName + ' DB 256 dup(0)\n')

            # Registra variable
            varNames[nVars] = varName
            varType[nVars] = 2
            varArrSiz[nVars] = 0
            nVars += 1
        else:
            MsjError = 'Tipo desconocido: ' + typName
            return
    else:
        MsjError = 'Se esperaba ":" o "[".'
        return


def FindVariable():
    # Busca la variable con el nombre que está en "srcToken", y actualiza las variables:
    # "curVarName", "curVarType", y "curVarArSiz".
    # Si no encuentra, devuelve cadena vacía en "curVarName".

    global varNames
    global varType
    global varArrSiz
    global srcToken
    global curVarName
    global curVarArSiz
    global curVarType

    tmp: str
    contin: int
    curVar: int

    curVar = 0

    tmp = varNames[curVar]

    if tmp != srcToken:
        contin = 1
    else:
        contin = 0

    while contin == 1:
        curVar += 1

        if curVar == 256:
            break

        tmp = varNames[curVar]
        if tmp != srcToken:
            contin = 1
        else:
            contin = 0
    # Verifica si encontro
    if contin == 0:
        curVarName = varNames[curVar]
        curVarType = varType[curVar]
        curVarArSiz = varArrSiz[curVar]
        return  # 'curVar' contiene el indice

    # No encontro
    curVarName = ''


def ReadArrayIndex(inFile):
    # Lee el índice de un arreglo. Es decir, lo que va entre corchetes: [].
    # Devuelve información en las variables: idxStorag, idxCteInt, y idxVarNam.
    # No genera código y no usa ningún registro adicional, porque restringe que el
    # índice sea una constante o una variable simple.
    # Se asume que el token actual es '['.
    # Si encuentra algún error, devuelve el mensaje en "MsjError"

    global MsjError
    global resStorag
    global idxStorag
    global idxCteInt
    global idxVarNam
    global resCteInt
    global resVarNam

    # Es acceso a arreglo
    NextToken(inFile)  # Toma '['
    EvaluateExpression(inFile, outFile)

    if MsjError() != '':
        return

    if resStorag == 2:
        # Se restringe el uso de expresiones aquí, por simplicidad, para no complicar la
        # generación de código. Así solo tendremos constantes o variables como índice.
        MsjError = 'No se permiten expresiones aqui.'
        return

    if resStorag == 1:
        # Es variable. Solo puede ser entera.

        if resType != 1:
            MsjError = 'Se esperaba variable entera.'
            return

    CaptureChar((']'), inFile)

    if MsjError != '':
        return

    # Sí, es un arreglo. Guarda información sobre el índice.
    # Solo puede ser entero o variable entera.

    idxStorag = resStorag  # Guarda almacenamiento del índice.
    idxCteInt = resCteInt  # Valor entero
    idxVarNam = resVarNam  # Nombre de varaible


def GetOperand(inFile, outFile):
    # Extrae un operando. Actualiza variables "resXXX".
    global srcToktyp
    global srcToken
    global resStorag
    global resType
    global resCteInt
    global resCteStr
    global MsjError

    n: int

    TrimSpaces(inFile)

    # Captura primer operando, asumiendo que es el unico
    if srcToktyp == 3:  # Literal numero

        n = int(srcToken)  # Falta verificacion de error
        resStorag = 0  # Constante
        resType = 1   # Integer
        resCteInt = n  # Valor
        NextToken(inFile)

    elif srcToktyp == 4:  # Literal Cadena
        resStorag = 0  # Constante
        resType = 2   # Integer

        resCteStr = copy(srcToken)  # Valor
        NextToken(inFile)

    elif srcToktyp == 2:  # Identificador
        # Verifica función del sistema
        if srcToken == 'length':
            NextToken(inFile)
            CaptureChar(ord('('), inFile)

            if MsjError != '':
                return
            EvaluateExpression(inFile, outFile)

            if MsjError != '':
                return
            CaptureChar(ord(')'), inFile)

            if MsjError != '':
                return

            if resType != 2:
                MsjError = 'Se esperaba una cadena.'
                return

            if resStorag == 0:
                # Constante cadena
                resType = 1  # Devuelve constante numérica
                resCteInt = len(resCteStr)

            elif resStorag == 1:
                # Variable cadena
                outFile.write('    invoke szLen, addr '+resVarNam)
                resType = 1  # Devuelve número en EAX
                resStorag = 2  # Expresión

            elif resStorag == 2:
                # Expresión cadena
                outFile.write('    invoke szLen, addr _regstr')
                resType = 1  # Devuelve número en EAX
                resStorag = 2  # Expresión

            else:
                MsjError = 'Almacenamiento no soportado'
                return

        else:
            # Busca variable
            FindVariable()
            if curVarName == '':
                MsjError = 'Identificador desconocido: ' + srcToken
                return

            # Es una variable. Podria ser un arreglo
            NextToken(inFile)
            TrimSpaces(inFile)

            if srcToken == '[':
                # Es acceso a arreglo

                # Actualiza idxStorag, idxCteInt, y idxVarNam.
                ReadArrayIndex(inFile)

                # Valida si la variable es arreglo
                if curVarArSiz == 0:
                    MsjError = 'Esta variable no es un arreglo.'
                    return

                # Extraemos valor y devolvemos como expresión
                resStorag = 2  # Expresión
                resType = curVarType  # Devuelve el mismo tipo que la variable.

                if resType == 1:
                    # Arreglo de enteros
                    outFile.write(
                        '    mov eax, DWORD PTR [', curVarName, '+', idxCteInt*4, ']')

                else:
                    # Arreglo de cadenas
                    outFile.write('    invoke szCopy,addr ' +
                                  curVarName+'+', idxCteInt*256, ', addr _regstr')

            else:
                # Es una variable común
                resStorag = 1
                resType = curVarType
                resVarNam = curVarName

    else:
        MsjError = 'Error de sintaxis: ' + srcToken
        return


def GetOperand1(inFile, outFile):
    GetOperand(inFile, outFile)

    global op1Type
    global op1Storag
    global op1VarNam
    global op1CteInt
    global op1CteStr
    global resType
    global resStorag
    global resVarNam
    global resCteInt
    global resCteStr

    op1Type = resType
    op1Storag = resStorag
    op1VarNam = resVarNam
    op1CteInt = resCteInt
    op1CteStr = resCteStr


def GetOperand2(inFile, outFile):
    GetOperand(inFile, outFile)

    global op2Type
    global op2Storag
    global op2VarNam
    global op2CteInt
    global op2CteStr
    global resType
    global resStorag
    global resVarNam
    global resCteInt
    global resCteStr

    op2Type = resType
    op2Storag = resStorag
    op2VarNam = resVarNam
    op2CteInt = resCteInt
    op2CteStr = resCteStr


def DeclareConstantString(constStr: str, outFile):
    # Inserta la declaracion de una constante string, en la seccion de datos, para
    # poder trabajarla.
    global nconstr
    global constr

    tmp: str

    tmp = str(nconstr)
    constr = '_ctestr' + tmp  # Nombre de constante

    outFile.writelines(['    .data\n', '    ' + constr +
                       ' db "' + constStr + '",0\n', '    .code\n'])
    nconstr += 1


def OperAdd(outFile):
    # Realiza la operacion "+" sobre los operandos "op1XXX" y "op2XXX". Devuelve resultado en
    # resXXX"
    global op1Type
    global op2Type
    global MsjError
    global resType
    global op1Storag
    global op2Storag
    global resStorag
    global resCteInt
    global op1CteInt
    global op2CteInt
    global op1VarNam
    global op2VarNam
    global resCteStr
    global op1CteStr
    global op2CteStr
    global constr

    if op1Type != op2Type:
        MsjError = 'No se pueden sumar estos tipos'
        return

    # Son del mismo tipo
    if op1Type == 1:
        # ******** Suma de Enteros **********
        resType = 1

        if op1Storag == 0:
            if op2Storag == 0:
                # --- Constante + Constante ---
                resStorag = op1Storag
                resCteInt = op1CteInt + op2CteInt

            elif op2Storag == 1:
                # --- Constante + Variable ---
                resStorag = 2  # Expresion
                outFile.writelines(
                    ['    mov eax, ' + op2VarNam, '    add eax, ' + op1CteInt])

            elif op2Storag == 2:
                # Constante + Expresion
                resStorag = 2  # Expresion
                outFile.write('    add eax, ' + op1CteInt)

            else:
                MsjError = 'Operacion no implementada'
                return

        elif op1Storag == 1:
            if op2Storag == 0:
                # --- Variable + Constante ---
                resStorag = 2  # Expresion
                outFile.writelines(
                    ['    mov eax, ' + op1VarNam+'\n' + '    add eax, ' + str(op2CteInt)+'\n'])

            elif op2Storag == 1:
                # --- Variable + Variable ---
                resStorag = 2  # Expresion
                outFile.writelines(
                    ['    mov eax, ' + op2VarNam, '    add eax, ' + op1CteInt])

            elif op2Storag == 2:
                # Variable + Expresion
                resStorag = 2  # Expresion
                outFile.writelines(
                    ['    mov ebx, ' + op1VarNam, '    add eax, ebx'])
            else:
                MsjError = 'Operacion no implementada'
                return

        elif op1Storag == 2:
            if op2Storag == 0:
                # --- Expresion + Constante ---
                resStorag = 2  # Expresion
                outFile.write('    add eax, ', op2CteInt)

            elif op2Storag == 1:
                # --- Expresion + Variable ---
                resStorag = 2  # Expresion
                outFile.write('    add eax, ', op2VarNam)

            elif op2Storag == 2:
                # Expresion + Expresion
                resStorag = 2  # Expresion
                outFile.writelines(['    pop ebx', '    add eax, ebx'])
            else:
                MsjError = 'Operacion no implementada'
                return

        else:
            MsjError = 'Operacion no implementada'
            return

    elif op1Type == 2:
        # ******** Suma de Cadenas **********
        resType = 2

        if op1Storag == 0:
            if op2Storag == 0:
                # --- Constante + Constante ---
                resStorag = op1Storag
                resCteStr = op1CteStr + op2CteStr

            elif op2Storag == 1:
                # --- Constante + Variable ---
                resStorag = 2  # Expresion
                DeclareConstantString(op1CteStr, outFile)
                outFile.writelines(['    invoke szCopy, addr ' +
                                    constr + ', addr _regstr', '    invoke szCopy, addr ' + op2VarNam + ', addr _regstr+', len(resCteStr)])

            else:
                MsjError = 'Operacion no implementada'
                return

        elif op1Storag == 1:
            if op2Storag == 0:
                # --- Variable + Constante ---
                resStorag = 2  # Expresion
                outFile.write('    invoke szCopy, addr ' +
                              op1VarNam+', addr _regstr')
                DeclareConstantString(op2CteStr, outFile)
                outFile.write(
                    '    invoke szCatStr, addr _regstr, addr ' + constr+'\n')

            elif op2Storag == 1:
                # --- Variable + Variable ---
                resStorag = 2  # Expresion
                outFile.write(['    invoke szCopy, addr ' +
                              op1VarNam+', addr _regstr', '    invoke szCatStr, addr _regstr, addr ' + op2VarNam])

            elif op2Storag == 2:
                # Variable + Expresion
                resStorag = 2  # Expresion
                outFile.writelines(['    invoke szCopy, addr ' +
                                    op1VarNam+', addr _regstr', '    invoke szCatStr, addr _regstr, addr ' + op2VarNam])
            else:
                MsjError = 'Operacion no implementada'
                return
    else:
        MsjError = 'Operacion no implementada'
        return


def OperSub(outFile):
    # Realiza la operacion "-" sobre los operandos "op1XXX" y "op2XXX". Devuelve resultado en
    # "resXXX"
    global op1Type
    global op2Type
    global MsjError
    global resType
    global op1Storag
    global op2Storag
    global resStorag
    global resCteInt
    global op1CteInt
    global op2CteInt
    global op1VarNam
    global op2VarNam
    global resCteStr
    global op1CteStr
    global op2CteStr
    global constr

    if op1Type != op2Type:
        MsjError = 'No se pueden restar estos tipos'
        return

    # Son del mismo tipo
    if op1Type == 1:
        # ********* Resta de enteros **************
        resType = 1
        if op1Storag == 0:
            # Constante + algo
            if op2Storag == 0:
                # --- Constante - Constante ---
                resStorag = op1Storag
                resCteInt = op1CteInt - op2CteInt

            elif op2Storag == 1:
                #--- Constante - Variable
                resStorag == 2  # Expresión
                outFile.writelines(
                    ['    mov eax, ' + op1CteInt, '    sub eax, ' + op2VarNam])

            elif op2Storag == 2:
                #--- Constante - Expresión
                resStorag = 2  # Expresión
                outFile.writelines(
                    ['    mov ebx, ' + op1CteInt, '    sub eax, ebx'])

            else:
                MsjError = 'Operación no implementada'
                return

        elif op1Storag == 1:
            # Variable + algo
            if op2Storag == 0:
                # --- Variable - Constante ---
                resStorag = 2  # Expresión
                outFile.writelines(
                    ['    mov eax, ' + op1VarNam, '    sub eax, ' + op2CteInt])

            elif op2Storag == 1:
                #--- Variable - Variable
                resStorag = 2  # Expresión
                outFile.writelines(
                    ['    mov eax, ' + op1VarNam, '    sub eax, ' + op2VarNam])

            elif op2Storag == 2:
                #--- Variable - Expresión
                resStorag = 2  # Expresión
                outFile.writelines(
                    ['    mov ebx, ' + op1VarNam, '    sub ebx, eax', '    mov eax, ebx'])

            else:
                MsjError = 'Operación no implementada'
                return

        elif op1Storag == 2:
            # Expresión menos algo
            if op2Storag == 0:
                # --- Expresión - Constante ---
                resStorag = 2  # Expresión
                outFile.write('    sub eax, ' + op2CteInt)

            elif op2Storag == 1:
                #--- Expresión - Variable
                resStorag = 2  # Expresión
                outFile.write('    sub eax, ' + op2VarNam)

            elif op2Storag == 2:
                #--- Expresión - Expresión
                resStorag = 2  # Expresión
                outFile.writelines(
                    ['    pop ebx', '    sub ebx, eax', '    mov eax, ebx'])

            else:
                MsjError = 'Operación no implementada'
                return
        else:
            MsjError = 'Operación no implementada'
            return


def EvaluateExpression(inFile, outFile):
    # Evalua la expresión actual y actualiza resStorag, resVarNam, resCteInt, resCteStr.
    # Puede generar código si es necesario.
    global resVarNam
    global MsjError
    global srcToktyp
    global srcToken

    # Toma primer operando
    GetOperand1(inFile, outFile)
    if MsjError != '':
        return
    # Guarda datos del operando
    # Verifica si hay operandos, o la expresion termina aquí

    TrimSpaces(inFile)
    # Captura primer operando, asumiendo que es el único

    if srcToktyp == 0:
        return
    if srcToken == ')':
        return  # Terminó la expresión
    if srcToken == ']':
        return  # Terminó la expresión
    # Hay más tokens
    # Extrae operador

    if srcToken == '+':

        NextToken(inFile)  # toma token
        GetOperand2(inFile, outFile)
        if MsjError != '':
            return
        OperAdd(outFile)  # Puede salir con error

    elif srcToken == '-':
        NextToken(inFile)  # toma token
        GetOperand2(inFile, outFile)

        if MsjError != '':
            return
        OperSub(outFile)  # Puede salir con error

    else:

        MsjError = 'Error de sintaxis: ' + srcToken
        return


def processPrint(ln: int, inFile, outFile):
    # Implementa las instrucciones "print" y "println". Si "ln" = 0 se compila "print",
    # de otra forma se compila "println".
    global MsjError
    global resStorag
    global resType
    global resCteInt
    global resCteStr
    global resVarNam

    NextToken(inFile)
    EvaluateExpression(inFile, outFile)

    if MsjError != '':
        return

    if resStorag == 0:
        # Almacenamiento en Constantes

        if resType == 1:
            # Imprime constante entera
            outFile.writelines(['    print "', resCteInt + '"'])

        elif resType == 2:
            # Imprime constante cadena
            outFile.write('    print "'+resCteStr+'"')

    elif resStorag == 1:
        # Almacenamiento en variable

        if resType == 1:
            # Imprime variable entera
            outFile.writelines(
                ['    invoke dwtoa,' + resVarNam + ', addr _regstr', '    print addr _regstr'])

        elif resType == 2:
            # Imprime constante cadena
            outFile.write('    print addr ' + resVarNam)

    elif resStorag == 2:
        # Almacenamiento en expresion

        if resType == 1:
            # Imprime variable entera
            outFile.writelines(
                ['    invoke dwtoa, eax, addr _regstr', '    print addr _regstr'])

        elif resType == 2:
            # Imprime constante cadena
            outFile.write('    print addr _regstr')

    else:
        MsjError = 'Almacenamiento no soportado'
        return

    if ln == 0:
        outFile.write('')

    else:
        outFile.write(',13,10')


def ProcessAssigment(inFile, outFile):

    global srcToken
    global curVarArSiz
    global MsjError
    global idxStorag
    global resType
    global asgVarType
    global resVarNam

    NextToken(inFile)
    TrimSpaces(inFile)

    if srcToken == '[':

        ReadArrayIndex(inFile)  # Actualiza idxStorag, idxCteInt, y idxVarNam.
        # Valida si la variable es un arreglo

        if curVarArSiz == 0:
            MsjError = 'Esta variable no es un arreglo.'
            return

    else:
        idxStorag = 1000  # Sin almacenamiento

    TrimSpaces(inFile)

    if srcToken != '=':
        MsjError = 'Se esperaba "=".'
        return

    NextToken(inFile)  # Toma "="

    # Evalua expresion
    EvaluateExpression(inFile, outFile)

    if MsjError != '':
        return

    # Codifica la asignacion
    if resType == 1:

        # Integer
        if asgVarType != 1:
            MsjError = 'No se puede asignar un entero a esta variable.'
            return

        if resStorag == 0:
            # Constante
            if idxStorag == 1000:  # Sin arreglo
                outFile.write('    mov DWORD PTR ' +
                              asgVarName + ', ' + str(resCteInt)+'\n')

            elif idxStorag == 0:  # Indexado por constante
                outFile.write(
                    '    mov DWORD PTR [' + asgVarName + '+' + idxCteInt*4 + '], ' + resCteInt)

            else:
                MsjError = 'No se soporta este tipo de expresion'
                return

        elif resStorag == 1:
            # Variable

            if idxStorag == 1000:  # Sin arreglo

                outFile.writelines('    mov eax, ' + resVarNam +
                                   '\n' + '    mov ' + asgVarName + ', eax\n')

            else:
                MsjError = 'No se soporta este tipo de expresión.'
                return

        else:
            # Expresión. Ya está en EAX
            if idxStorag == 1000:
                outFile.write('    mov ' + asgVarName + ', eax\n')

            else:
                MsjError = 'No se soporta este tipo de expresion'
                return

    else:
        # String

        if asgVarType != 2:
            MsjError = 'No se puede asignar una cadena a esta variable.'

        if resStorag == 0:
            # <variable> <- Constante

            if idxStorag == 1000:  # Sin arreglo

                DeclareConstantString(resCteStr, outFile)
                outFile.write('    invoke szCopy,addr ' +
                              constr + ', addr ' + asgVarName+'\n')

            elif idxStorag == 0:  # Indexado por constante

                DeclareConstantString(resCteStr, outFile)
                outFile.write('    invoke szCopy,addr '+constr +
                              ', addr ' + asgVarName + ' + ' + idxCteInt * 256)

            else:
                MsjError = 'No se soporta este tipo de expresion'
                return

        elif resStorag == 1:

            # <variable> <- Variable
            outFile.write('    invoke szCopy,addr ' +
                          resVarNam + ', addr ' + asgVarName)

        else:
            # Expresión. Ya está en "_regstr"
            outFile.write('    invoke szCopy,addr _regstr' +
                          ', addr ' + asgVarName)


srcRow = 0
# Abre archivo de entrada
#inFile = open('./input.tit', 'r')

outFile = open('input.asm', 'w')

# Inicia banderas
nVars = 0  # Número inicial de variables
srcRow = 0  # Número de línea
FirstCode = 1  # Inicia bandera


nconstr = 0
resVarNam = ""
resCteStr = ""
resCteInt = 0
resType = 0
resStorag = 0
# Escribe encabezado de archivo

outFile.writelines(['    include \masm32\include\masm32rt.inc\n',
                   '    .data\n', '    _regstr DB 256 dup(0)\n'])
InVarSec = 1
MsjError = ''

with open('input.tit', 'r') as inFile:
    NextLine(inFile)  # Para hacer la primera lectura.
    while EndOfFile() != 1:

        NextToken(inFile)
        print(srcToken)
        if EndOfLine() == 1:
            NextLine(inFile)
        else:
            if srcToktyp == 5:
                ExtractComment()  # Comentario

            elif srcToken == 'var':

                # Es una declaración
                if InVarSec == 0:
                    # Estamos fuera de un bloque de variables

                    outFile.write('    .data\n')
                    InVarSec = 1  # Fija bandera
                # *** Aquí procesamos variables
                ParserVar(inFile, outFile)

                if MsjError != '':
                    break

            else:
                # Debe ser una instrucción. Aquí debe empezar la sección de código.
                if InVarSec == 1:

                    # Estamos dentro de un blqoue de variables
                    outFile.write('    .code\n')
                    InVarSec = 0

                if FirstCode == 1:
                    # Primera instrucción
                    outFile.writelines(['    .code\n', 'start:\n'])
                    FirstCode = 0
                # **** Aquí procesamos instrucciones.
                # y ya no se deben permitir más declaraciones.

                if srcToken == 'print':
                    processPrint(0, inFile, outFile)
                    if MsjError != '':
                        break

                elif srcToken == 'println':
                    processPrint(1, inFile, outFile)
                    if MsjError != '':
                        break

                if srcToktyp == 2:
                    # Es un identificador, puede ser una asignación
                    FindVariable()

                    asgVarName = curVarName
                    asgVarType = curVarType

                    if curVarName == '':
                        MsjError = 'Se esperaba variable: ' + srcToken
                        break

                    # Debe ser una asignación
                    ProcessAssigment(inFile, outFile)

                    if MsjError != '':
                        break
                else:

                    MsjError = 'Instruccion desconocida' + srcToken
                    break

    if MsjError != '':
        print('Line: {0}, {1}: {2}'.format(srcRow, idxLine, MsjError))

        # Termino la exploracion de tokens

    if FirstCode == 1:
        # No se han encontrado instrucciones. Incluimos encabezado de código en ASM.
        outFile.writelines(['    .code\n', 'start:\n'])

    outFile.writelines(['    exit\n', 'end start\n'])
    print('<<< Pulse <Enter> para continuar >>>')
