from utils import ArrayContains, dec_to_hex16, is_int


chars = ["'", "(", ")", "-", "+", "*", "/", "^", ","]

def lexer(data):
    data2 = []
    for i in data:
        if i != '\n':
            data2.append(i)
    data2 = "".join(data2)
    data2 = data2.split(";")
    data2.remove("")
    data3 = []
    for i in data2:
        arr = []
        word = []
        for i, x in enumerate(i):
            if x == ' ' or x == '\n':
                if len(word) > 0:
                    arr.append(''.join(word))
                    word = []
            elif ArrayContains(chars, x):
                if len(word) > 0:
                    arr.append(''.join(word))
                    word = []
                arr.append(x)
            else:
                word.append(x)
        # Check for the last one
        if len(word) > 0:
            arr.append(''.join(word))

        data3.append(arr)

    return(data3)



declaredvars = {}
freedvars = []
regs = {"A":"", "B":"", "C":""}


def manage(var, action=0, value=0):
    x = ""
    cmd = ""
    if var[0] == "_" and var != "_":
        raise BaseException("'_' cannot be used in high level variables!")

    if action == 1:
        if len(freedvars) > 0:
            x = freedvars[0]
            declaredvars[var] = x
            freedvars.remove(x)
        else:
            declaredvars[var] = var
        cmd = f"LDIA {dec_to_hex16(int(value))}\nSTA {declaredvars[var]}\n"
        regs["A"] = var
    elif action == -1:
        if var in declaredvars:
            x = declaredvars[var]
            freedvars.append(x)
            del x

    return cmd


helpers = """

_MUL:
# Register: B * C
# Product in A
INC
LDIA 0000
__MUL_LOOP:
ADB
SETA
MOVCA
LDIC 0001
SBC
MOVAC
OUT
GETA
JPNZ __MUL_LOOP
DEC
RET

_MULM:
# Register: B * C
# Product in A
LDIA 0000
__MULM_LOOP:
ADB
STA _PROD
MOVCA
LDIC 0001
SBC
MOVAC
OUT
LDA _PROD
JPNZ __MULM_LOOP
RET

_DIV:
# Register: A / B
# Quotient in A
# Remainder in B
INC
LDIC 0000
__DIV_LOOP:
SBB
JMPN __DIV_END
SETA
LDIA 0001
ADC
MOVAC
OUT
GETA
JMP __DIV_LOOP
__DIV_END:
GETB
MOVCA
DEC
RET

_DIVM:
# Register: A / B
# Quotient in A
# Remainder in B
LDIC 0000
__DIVM_LOOP:
SBB
JMPN __DIVM_END
STA _REM
LDIA 0001
ADC
MOVAC
OUT
LDA _REM
JMP __DIVM_LOOP
__DIVM_END:
LDB _REM
MOVCA
RET

"""

def parser(data):
    stackptr = 0
    stacklim = 15
    def canPush():
        return stackptr < stacklim - 1

    data2 = lexer(data)
    prg = []
    for i in data2:
        if i[0] == "let":
            prg.append(manage(i[1], 1, i[-1]))
        elif i[0] == "out":
            if regs["A"] == i[2]:
                prg.append("OUT\n")
            else:
                prg.append(f"LDA {declaredvars[i[2]]}\nOUT\n")
        elif i[0] == "del":
            prg.append(manage(i[1], -1))

        elif i[0] == "push":
            if canPush():
                stackptr += 1
            else:
                raise BaseException("Stack Limit Reached!")

            if regs["A"] == i[2]:
                prg.append(f"INC\nSETA\n")
            elif regs["B"] == i[2]:
                prg.append(f"INC\nSETB\n")            
            elif regs["C"] == i[2]:
                prg.append(f"INC\nSETC\n")
            else:
                prg.append(f"INC\n{[f"LDIA {dec_to_hex16(int(i[2]))}" if is_int(i[2]) else f"LDA {declaredvars[i[2]]}"][0]}\nSETA\n")

        elif i[0] == "pop":
            if stackptr > 0:
                stackptr -= 1
            else:
                raise BaseException("Stack Empty!")

            if i[2] == ")":
                prg.append(f"GETA\nDEC\n")
            else:
                try:
                    prg.append(f"GETA\nDEC\nSTA {declaredvars[i[2]]}\n")
                except:
                    raise BaseException("Variable not declared!")


        elif i[2] in ["add", "sub", "mul", "divf"]:
            if i[2] == "add":
                if regs["A"] == i[4] and regs["B"] == i[6]:
                    prg.append(f"ADB\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4] and regs["C"] == i[6]:
                    prg.append(f"ADC\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nADB\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[6]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDB {declaredvars[i[4]]}"][0]}\nADB\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\n{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nADB\nSTA {declaredvars[i[0]]}\n")

            elif i[2] == "sub":
                if regs["A"] == i[4] and regs["B"] == i[6]:
                    prg.append(f"SBB\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4] and regs["C"] == i[6]:
                    prg.append(f"SBC\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nSBB\nSTA {declaredvars[i[0]]}\n")
                elif regs["B"] == i[6]:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\nSBB\nSTA {declaredvars[i[0]]}\n")
                elif regs["C"] == i[6]:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\nSBC\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\n{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nSBB\nSTA {declaredvars[i[0]]}\n")

            elif i[2] == "mul" and canPush():
                if regs["B"] == i[4] and regs["C"] == i[6]:
                    prg.append(f"CALL _MUL\nSTA {declaredvars[i[0]]}\n")
                elif regs["B"] == i[4]:
                    prg.append(f"{[f"LDIC {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDC {declaredvars[i[6]]}"][0]}\nCALL _MUL\nSTA {declaredvars[i[0]]}\n")
                elif regs["C"] == i[6]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDB {declaredvars[i[4]]}"][0]}\nCALL _MUL\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDB {declaredvars[i[4]]}"][0]}\n{[f"LDIC {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDC {declaredvars[i[6]]}"][0]}\nCALL _MUL\nSTA {declaredvars[i[0]]}\n")
            elif i[2] == "mul" and canPush() != True:
                if regs["B"] == i[4] and regs["C"] == i[6]:
                    prg.append(f"CALL _MULM\nSTA {declaredvars[i[0]]}\n")
                elif regs["B"] == i[4]:
                    prg.append(f"{[f"LDIC {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDC {declaredvars[i[6]]}"][0]}\nCALL _MULM\nSTA {declaredvars[i[0]]}\n")
                elif regs["C"] == i[6]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDB {declaredvars[i[4]]}"][0]}\nCALL _MULM\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDB {declaredvars[i[4]]}"][0]}\n{[f"LDIC {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDC {declaredvars[i[6]]}"][0]}\nCALL _MULM\nSTA {declaredvars[i[0]]}\n")

            elif i[2] == "divf" and canPush():
                if regs["A"] == i[4] and regs["B"] == i[6]:
                    prg.append(f"CALL _DIV\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nCALL _DIV\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\n{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nCALL _DIV\nSTA {declaredvars[i[0]]}\n")
            elif i[2] == "divf" and canPush() != True:
                if regs["A"] == i[4] and regs["B"] == i[6]:
                    prg.append(f"CALL _DIVM\nSTA {declaredvars[i[0]]}\n")
                elif regs["A"] == i[4]:
                    prg.append(f"{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nCALL _DIVM\nSTA {declaredvars[i[0]]}\n")
                else:
                    prg.append(f"{[f"LDIA {dec_to_hex16(int(i[4]))}" if is_int(i[4]) else f"LDA {declaredvars[i[4]]}"][0]}\n{[f"LDIB {dec_to_hex16(int(i[6]))}" if is_int(i[6]) else f"LDB {declaredvars[i[6]]}"][0]}\nCALL _DIVM\nSTA {declaredvars[i[0]]}\n")

        else:
            prg.append(f"{" ".join(i)}\n")
    prg.append("HLT")
    prg.append(helpers)
    return("".join(prg))



mneumonics = {
    "fetch": "0000",  # 000 {"00000084", "00000052", "00000120", "00000000"}
    "LDIA": "0004",   # 004 {"00000084", "00000052", "00000902", "00000000"}
    "LDIB": "0008",   # 008 {"00000084", "00000052", "00002102", "00000000"}
    "LDIC": "000c",   # 012 {"00000084", "00000052", "00020102", "00000000"}
    "ADB": "0010",    # 016 {"00000084", "00041400", "00008800", "00000000"}
    "ADC": "0014",    # 020 {"00000084", "00050400", "00008800", "00000000"}
    "SBB": "0018",    # 024 {"00000084", "00045400", "00008800", "00000000"}
    "SBC": "001c",    # 028 {"00000084", "00054400", "00008800", "00000000"}
    "STA": "0020",    # 032 {"00000084", "00000052", "00000180", "00000408"}
    "STB": "0024",    # 036 {"00000084", "00000052", "00000180", "00000000"}
    "STC": "0028",    # 040 {"00000084", "00000052", "00000180", "00000000"}
    "OUT": "002c",    # 044 {"00000084", "00080400", "00000000", "00000000"}
    "JMP": "0030",    # 048 {"00000084", "00000052", "00000101", "00000000"}
    "CALL": "0034",   # 052 {"00000086", "00200054", "00000101", "00000000"}
    "RET": "0038",    # 056 {"00100001", "00000000", "00000000", "00000000"}
    "JMPZ": "003c",   # 060 {"00000084", "00000052", "00c00100", "00000000"}
    "JMPN": "0040",   # 064 {"00000084", "00000052", "01400100", "00000000"}
    "LDA": "0044",    # 068 {"00000084", "00000052", "00000180", "00000950"}
    "LDB": "0048",    # 072 {"00000084", "00000052", "00000180", "00002150"}
    "LDC": "004c",    # 076 {"00000084", "00000052", "00000180", "00020150"}
    "JMPY": "0050",   # 080 {"00000084", "00000052", "02400100", "00000000"}
    "JPNZ": "0054",   # 084 {"00000084", "00000052", "04400100", "00000000"}
    "MOVAB": "0058",  # 088 {"00002400", "00000000"} Move A into B
    "MOVAC": "005a",  # 090 {"00020400", "00000000"}
    "MOVBA": "005c",  # 092 {"00001800", "00000000"}
    "MOVBC": "005e",  # 094 {"00021000", "00000000"}
    "MOVCA": "0060",  # 096 {"00010800", "00000000"}
    "MOVCB": "0062",  # 098 {"00012000", "00000000"}
    "INC": "0064",    # 100 {"18000000", "00000000"} Stack Ops
    "DEC": "0066",    # 102 {"10000000", "00000000"}
    "SETA": "0068",   # 104 {"20000400", "00000000"}
    "GETA": "006a",   # 106 {"40000800", "00000000"}
    "SETB": "006c",   # 108 {"20001000", "00000000"}
    "GETB": "006e",   # 110 {"40002000", "00000000"}
    "SETC": "0070",   # 112 {"20010000", "00000000"}
    "GETC": "0072",   # 114 {"40020000", "00000000"}
    "HLT": "0003",    # 003 {"80000000"}
}

script = {}
var = {}

def hexer(data):
    k = 0
    x = []
    y = []
    z = []
    for i in data.split("\n"):
        if i != "":
            x.append(i.split(" "))

    for i in x:
        if i[0][-1] == ":":
            script[i[0][:-1]] = dec_to_hex16(k)
        elif i[0] == "#":
            pass
        else:
            y.append(i)
            k += len(i)
    del x

    for i in y:
        # print(i)
        if i[0][-1] != ":":
            z.append(mneumonics[i[0]])
        
        if len(i) == 2:
            if i[0] in ["STA", "STB", "STC"]:
                if ArrayContains(var.keys(), i[1]) != True:
                    var[i[1]] = dec_to_hex16(k)
                z.append(var[i[1]])
                k += 1
            elif i[0] in ["LDA", "LDB", "LDC"]:
                try:
                    z.append(var[i[1]])
                except:
                    raise BaseException(f"Variable accessed before initialization! - '{i[1]}' - word {k}")
            elif i[0] in ["JMP", "JMPZ", "JMPN", "JPNZ", "CALL"]:
                try:
                    z.append(script[i[1]])
                except:
                    raise BaseException(f"Method accessed before initialization! - '{i[1]}' - word {k}")
            else:
                z.append(i[1])

    return z

