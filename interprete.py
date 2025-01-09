from sys import argv
import sys

modules = {}

def include(module_name):
    if module_name in modules:
        return modules[module_name]
    try:
        with open(module_name + ".sbl", "r") as f:
            module_lines = f.readlines()
        module = procesar(module_lines)
        modules[module_name] = module
        return module
    except FileNotFoundError:
        print(f"Module {module_name} not found!")
        sys.exit(1)

class SBLException(Exception):
    pass
class UnderflowError(SBLException):
    def __init__(self, value):
        self.value: str = value
    def __str__(self):
        return str(self.value)

    def __init__(self, value, dtype):
        self.value = value
        self.dtype = dtype

    def __repr__(self):
        return f"{self.value}({self.dtype})"
def check():
    if len(argv) != 2:
        print("the argument must be a file")
        sys.exit(1)
    return argv[1]

def read(path):
    lines = []
    try:
        with open(path, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("--")]
    except FileNotFoundError:
        print(f"file {path} doesnt exist")
        sys.exit(1)
    return lines

def printstack(stack) -> None:
    print(stack.array[:stack.full+1])

def procesar(lines):
    labels = {}
    tokcounter = 0
    for line in lines:
        parts = line.split()
        opcode = parts[0]
        if opcode.endswith(":"):
            labels[opcode[::-1]] = tokcounter
        tokcounter += 1
    return labels

def execute(pgm, labels) -> None:
    t = 0
    stack = Stack(256)
    variables = {}

    for line in pgm:
        if line.startswith("INCLUDE"):
            module_name = line.split()[1]
            include(module_name)

    while pgm[t] != "STOP":
        opcode = pgm[t]
        t += 1
        parts = pgm[t].split()

        if opcode == "PUSH":
            if len(parts) > 1:
                n = int(parts[1])
                stack.push(n)
            else:
                print(f"pushing error in line {t}")
                sys.exit(1)
        elif opcode == "POP":
            try:
                stack.pop()
            except UnderflowError:
                print("pile is overflow.")
                sys.exit(1)
        elif opcode == "ADD":
            a = stack.pop()
            b = stack.pop()
            stack.push(a + b)
        elif opcode == "SUB":
            a = stack.pop()
            b = stack.pop()
            stack.push(b - a)
        elif opcode == "MUL":
            a = stack.pop()
            b = stack.pop()
            stack.push(a * b)
        elif opcode == "DIV":
            a = stack.pop()
            b = stack.pop()
            if a == 0:
                print(f"infinity")
            stack.push(b / a)
        elif opcode == "MOD":
            a = stack.pop()
            b = stack.pop()
            stack.push(b % a)
        elif opcode == "NEG":
            a = stack.pop()
            stack.push(-a)
        elif opcode == "DUP":
            a = stack.top()
            stack.push(a)
        elif opcode == "SWAP":
            a = stack.pop()
            b = stack.pop()
            stack.push(a)
            stack.push(b)
        elif opcode == "PRINT":
            if len(parts) > 1:
                strlit = ' '.join(parts[1:])
                print(strlit)
            else:
                print(f"print error in line {t}.")
                sys.exit(1)
        elif opcode == "READ":
            n = int(input())
            stack.push(n)

        elif opcode == "SET":
            if len(parts) > 2:
                name = parts[1]
                val = int(parts[2])
                variables[name] = val
            else:
                print(f"variableset error in line {t}")
                sys.exit(1)

        elif opcode == "GET":
            if len(parts) > 1:
                name = parts[1]
                stack.push(variables.get(name, 0))
            else:
                print(f"getting variable error in line {t}")
        elif opcode == "IF":
            condition = stack.pop()
            if condition == 0:
                while pgm[t] != "ENDIF":
                    t += 1
        elif opcode == "ELSE":
            while pgm[t] != "ENDIF":
                t += 1
        elif opcode == "ENDIF":
            pass
        elif opcode == "CALL":
            if len(parts) > 1:
                label = parts[1]
                stack.push(t)
                t = labels.get(label[::-1], t)
            else:
                print(f"calling function error in line {t}.")
        elif opcode == "RETURN":
            t = stack.pop()
        elif opcode == "JEQ0":
            n = stack.top()
            if n == 0:
                t = labels[pgm[t][::-1]]
        elif opcode == "JGT0":
            number = stack.top()
            if number > 0:
                t = labels[pgm[t][::-1]]
        elif opcode == "BREAKPOINT":
            print([stack, variables])
            debug(stack)

        else:
            print(f"operacion no disponible {opcode} en la linea {t}.")
            sys.exit(1)
        t += 1

class Stack:
    def __init__(self, size):
        self.array = [None] * size
        self.full = -1

    def push(self, n):
        self.full += 1
        self.array[self.full] = n

    def pop(self):
        if self.full == -1:
            print("index dont exist")
            sys.exit(1)
        n = self.array[self.full]
        self.full -= 1
        return n

    def top(self):
        if self.full == -1:
            print("pile dont exist.")
            sys.exit(1)
        return self.array[self.full]

def debug(stack):
    print("Depuracion:", stack.array[:stack.full+1])

if __name__ == "__main__":
    path = check()
    lines = read(path)
    labels = procesar(lines)
    pgm = []
    tokcounter = 0
    for line in lines:
        parts = line.split()
        opcode = parts[0]
        if opcode.endswith(":"):
            continue
        pgm.append(opcode)
        tokcounter += 1
        if opcode == "PUSH":
            pgm.append(int(parts[1]))
            tokcounter += 1
        elif opcode == "PRINT":
            strlit = ' '.join(parts[1:])[1:-1]
            pgm.append(strlit)
            tokcounter += 1
        elif opcode in ["JEQ0", "JGT0"]:
            pgm.append(parts[1])
            tokcounter += 1
    pgm.append("STOP")
    execute(pgm, labels)
