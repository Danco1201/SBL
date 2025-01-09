import sys
import threading
from sys import argv

modules = {}
threads = []
functions = {}

def include(name):
    if name in modules:
        return modules[name]
    try:
        with open(name + ".sbl", "r") as f:
            module_lines = f.readlines()
        module = procesar(module_lines)
        modules[name] = module
        return module
    except FileNotFoundError:
        print(f"module {name} not found")
        sys.exit(1)

class SBLException(Exception):
    pass

class UnderflowError(SBLException):
    pass

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
        print(f"file {path} doesn't exist")
        sys.exit(1)
    return lines

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
    global functions, threads
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
        elif opcode == "LAMBDA":
            func_code = parts[1:]
            id = f"lambda_{t}"
            functions[id] = func_code
        elif opcode == "FLAMBDA":
            id = parts[1]
            if id in functions:
                lambda_code = functions[id]
                execute(lambda_code, labels)
            else:
                print(f"lambda {id} not defined.")
                sys.exit(1)

        elif opcode == "PRINT":
            if len(parts) > 1:
                strlit = ' '.join(parts[1:])
                print(strlit)
            else:
                print(f"print error in line {t}.")
                sys.exit(1)

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
        elif opcode == "THREAD":
            thread_code = parts[1:]
            thread = threading.Thread(target=execute, args=(thread_code, labels))
            threads.append(thread)
            thread.start()

        elif opcode == "JOIN":
            for thread in threads:
                thread.join()

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
