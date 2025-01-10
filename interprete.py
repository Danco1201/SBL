import sys
import threading
from sys import argv

modules = {}
threads = []
functions = {}
arrays={}
classes={}
instances={}
def concatenate(*args):
    return ''.join(args)

def substring(string, start, end):
    return string[start:end]

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
            labels[opcode[:-1]] = tokcounter
        tokcounter += 1
    return labels

def execute(pgm, labels):
    t = 0
    stack = Stack(256)
    variables = {}
    loopstack = []
    global functions, threads, instances, classes

    for line in pgm:
        if line.startswith("INCLUDE"):
            module_name = line.split()[1]
            include(module_name)

    while pgm[t] != "STOP":
        opcode = pgm[t]
        t += 1
        parts = pgm[t].split() if t < len(pgm) else []

        if opcode == "PUSH":
            if len(parts) > 0:
                arg = parts[0]
                try:
                    n = int(arg)
                    stack.push(n)
                except ValueError:
                    if arg in variables:
                        stack.push(variables[arg])
                    else:
                        print(f"pushing variable error in line {t}.")
                        sys.exit(1)
            else:
                print(f"pushing integer error in line {t}.")
                sys.exit(1)


        elif opcode == "PRINT":
            if parts:
                strlit = ' '.join(parts)
                print(strlit)
            else:
                print(f"print error in line {t}.")
                sys.exit(1)

        elif opcode == "SET":
            if len(parts) > 1:
                name = parts[0]
                val = int(parts[1])
                variables[name] = val
            else:
                print(f"variableset error in line {t}")
                sys.exit(1)

        elif opcode == "GET":
            if parts:
                name = parts[0]
                stack.push(variables.get(name, 0))
            else:
                print(f"getting variable error in line {t}")

        if opcode == "CLASS":
            class_name = parts[1]
            classes[class_name] = {"methods": {}, "attributes": []}
        
        elif opcode == "CREATE":
            class_name = parts[1]
            instance_name = parts[2]
            if class_name in classes:
                instance = {"class": class_name, "attributes": {}}
                instances[instance_name] = instance
                stack.push(instance_name)
            else:
                print(f"Class {class_name} not defined.")
                sys.exit(1)

        elif opcode == "SETATTR":
            instance_name = parts[1]
            attr_name = parts[2]
            value = int(parts[3])
            if instance_name in instances:
                instance = instances[instance_name]
                instance["attributes"][attr_name] = value
            else:
                print(f"Instance {instance_name} not found.")
                sys.exit(1)

        elif opcode == "GETATTR":
            instance_name = parts[1]
            attr_name = parts[2]
            if instance_name in instances and attr_name in instances[instance_name]["attributes"]:
                stack.push(instances[instance_name]["attributes"][attr_name])
            else:
                print(f"Error retrieving attribute {attr_name} from {instance_name}.")
                sys.exit(1)
        elif opcode in ["ADD", "SUB", "MUL", "DIV"]:
            b = stack.pop()
            a = stack.pop()
            if opcode == "ADD":
                stack.push(a + b)
            elif opcode == "SUB":
                stack.push(a - b)
            elif opcode == "MUL":
                stack.push(a * b)
            elif opcode == "DIV":
                if b == 0:
                    print("division by zero error")
                    sys.exit(1)
                stack.push(a // b)

        elif opcode == "WHILE":
            condition = parts[0]
            loopstack.append((t - 1, condition))

        elif opcode == "ENDWHILE":
            start, condition = loopstack.pop()
            val = variables.get(condition, 0)
            if val != 0:
                t = start

        if opcode == "CONCAT":
            if len(parts) >= 2:
                result = concatenate(*parts)
                stack.push(result)
            else:
                print(f"Concatenation error in line {t}.")
                sys.exit(1)

        elif opcode == "SUBSTR":
            if len(parts) == 3:
                string = stack.pop()
                start = int(parts[1])
                end = int(parts[2])
                result = substring(string, start, end)
                stack.push(result)
            else:
                print(f"Substring error in line {t}.")
                sys.exit(1)

        elif opcode == "FOR":
            var_name, start, end = parts[:3]
            loopstack.append((t - 1, var_name, int(start), int(end)))
            variables[var_name] = int(start)

        elif opcode == "ENDFOR":
            start, var_name, loop_start, loop_end = loopstack.pop()
            variables[var_name] += 1
            if variables[var_name] <= loop_end:
                t = start

        elif opcode.endswith(":"):
            label = opcode[:-1]
            functions[label_name] = t

        elif opcode == "CALL":
            func_name = parts[0]
            if func_name in functions:
                execute(pgm[functions[func_name]:], labels)
            else:
                print(f"function {func_name} not found.")
                sys.exit(1)

        elif opcode == "DEBUG":
            debug(stack, variables)

        elif opcode == "THREAD":
            thread_code = parts
            thread = threading.Thread(target=execute, args=(thread_code, labels))
            threads.append(thread)
            thread.start()

        elif opcode == "JOIN":
            for thread in threads:
                thread.join()
        if opcode == "ARRCREATE":
            name = parts[1]
            size = int(parts[2])
            arrays[name] = [None] * size  

        elif opcode == "ARRSET":
            name = parts[1]
            index = int(parts[2])
            value = int(parts[3])
            if name in arrays and 0 <= index < len(arrays[name]):
                arrays[name][index] = value
            else:
                print(f"array  {name} index {index} setting error in line {t}")
                sys.exit(1)

        elif opcode == "ARRGET":
            name = parts[1]
            index = int(parts[2])
            if name in arrays and 0 <= index < len(arrays[name]):
                stack.push(arrays[name][index])
            else:
                print(f"Error al obtener de {name} en índice {index}.")
                sys.exit(1)
        elif opcode == "EQ":
            var1 = stack.pop()
            var2 = stack.pop()
            stack.push(1 if var1 == var2 else 0)  

        elif opcode == "LT":
            var1 = stack.pop()
            var2 = stack.pop()
            stack.push(1 if var1 < var2 else 0) 

        elif opcode == "GT":
            var1 = stack.pop()
            var2 = stack.pop()
            stack.push(1 if var1 > var2 else 0) 


        else:
            print(f"operation not available {opcode} at line {t}.")
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
            print("index doesn't exist")
            sys.exit(1)
        n = self.array[self.full]
        self.full -= 1
        return n

    def top(self):
        if self.full == -1:
            print("stack doesn't exist.")
            sys.exit(1)
        return self.array[self.full]

def debug(stack):
    print("Depuracion:", stack.array[:stack.full + 1])

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

