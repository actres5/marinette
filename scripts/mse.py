#!/usr/bin/env python3
import sys
import string
import secrets
import pathlib

from colorama import *


def mse_print(text):
    print(Fore.GREEN+"MSE: "+Fore.BLUE+text)


def string_random(length):
    s = ""
    for _ in range(length):
        s += secrets.choice(string.ascii_letters).upper()
    return s


def read_file(path):
    with open(path) as file:
        code = file.readlines()
    return code


def write_file(path, code):
    with open(path, "w") as file:
        file.writelines(map(lambda l: l+"\n", code))


def simplify(code):
    simplified = list()
    for line in code:
        line = line.strip()
        if not line or (not DEBUG and line.find("//") == 0):
            continue
        simplified.append(line)
    return simplified


def beautify(code, tab_size=4):
    tab = 0
    for i in range(len(code)):
        line = code[i].strip()
        code[i] = (" "*tab) + line
        if " = function" in line:
            tab += tab_size
        if line.rfind("then") == len(line) - len("then"):
            tab += tab_size
        if line.find("else") == 0:
            tab -= tab_size
            code[i] = (" "*tab) + line
            tab += tab_size
        if line.find("for") == 0 or line.find("while") == 0:
            tab += tab_size
        if line.find("end") == 0 or line.find("else if") == 0:
            tab -= tab_size
            if line.rfind("then") == len(line) - len("then"):
                tab -= tab_size
            code[i] = (" "*tab) + line
            if line.rfind("then") == len(line) - len("then"):
                tab += tab_size
    return code


def transpile_prepends(code):
    payload = [
        "//-- MSE TRANSPILE PAYLOAD --",
        "______MSE_EXIT = @exit",
        'function Object() {',
        'Private = {}',
        'Private.ltsInheritancePath = ["Object"]',
        'function Private.IsObject(aObject) {',
        'return @aObject isa map and aObject.hasIndex("classID")',
        '}',
        'function Private.IsInstanceOf(aObject) {',
        'return Private.IsObject(@aObject) and Private.ltsInheritancePath.indexOf(aObject.classID) != null',
        '}',
        'Public = {}',
        'function Public.GetInheritancePath() {',
        'return Private.ltsInheritancePath[0:]',
        '}',
        'function Public.AddObjectRelation(aObject) {',
        'if (Private.IsObject(@aObject) and not Private.IsInstanceOf(aObject)) {',
        'Private.ltsInheritancePath.push(aObject.classID)',
        '}',
        '}',
        'Public.classID = "Object"',
        'Public.IsInstanceOf = @Private["IsInstanceOf"]',
        'return Public',
        '}',
        'function IsInstanceOf(mpInstance, aBase) {',
        'if (aBase isa string) {',
        'return typeof(@aInstance) == aBase',
        '} else if (@mpInstance isa map and mpInstance.hasIndex("IsInstanceOf")) {',
        'return mpInstance.IsInstanceOf(aBase)',
        '} else if (@mpInstance isa map and mpInstance.hasIndex("__isa")) {',
        'return IsInstanceOf(@mpInstance.__isa, aBase)',
        '}',
        'return false',
        '}',
        "function Success(aValue) {",
        "return [aValue, null]",
        "}",
        "function Error(aErrorValue) {",
        "return [null, aErrorValue]",
        "}",
        "//-- END TRANSPILE PAYLOAD --",
    ]
    code = payload + code
    return code


def transpile_ternaries(code):
    contexts = list()
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1 and "else" not in line:
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            continue
        if line.find("if (") == 0 or line.find("} else if (") == 0 or line.find("} else {") == 0:
            if line.find("{") == len(line) - 1:
                if line.find("}") == 0:
                    contexts.pop()
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            contexts.append(False)
        if len(contexts) == 0 or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            continue
        if line.find("}") == len(line) - 1 and len(contexts):
            contexts.pop()
        code[i] = code[i].replace(") {", ") then")
        code[i] = code[i].replace("} else if (", "else if (")
        code[i] = code[i].replace("} else {", "else")
        code[i] = code[i].replace("}", "end if")
    return code


def transpile_while_loops(code):
    contexts = list()
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1:
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            continue
        if line.find("while (") == 0:
            if line.find("{") == len(line) - 1:
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            contexts.append(False)
        if not len(contexts) or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            continue
        if line.find("}") == len(line) - 1 and len(contexts):
            contexts.pop()
        code[i] = code[i].replace(") {", ")")
        code[i] = code[i].replace("}", "end while")
    return code


def transpile_for_loops(code):
    contexts = list()
    blocks = list()
    initializer, condition, iterator = str(), str(), str()
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1:
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            continue
        if line.find("for (") == 0:
            if line.find("{") == len(line) - 1:
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            contexts.append(False)
        if not len(contexts) or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            continue
        if line.find("}") == len(line) - 1 and len(contexts):
            contexts.pop()
        if code[i].find("for (") == 0:
            start = code[i].find("(") + 1
            end = code[i].rfind(")")
            parts = code[i][start:end].split("; ")
            if len(parts) == 3:
                initializer, condition, iterator = map(lambda s: s.strip(), parts)
                blocks.append([initializer, condition, iterator])
            else:
                blocks.append(list())
            code[i] = code[i].replace(") {", "")
            if initializer:
                code[i] = initializer+"; while "+condition
            else:
                code[i] = code[i].replace("for (", "for ")
        if code[i].find("}") == 0:
            if len(blocks) > 0:
                parts = blocks.pop()
                if len(parts) == 3:
                    initializer, condition, iterator = parts
            if iterator:
                j = i
                while code[j] != initializer+"; while "+condition:
                    if code[j] == "continue":
                        code[j] = initializer+";continue"
                    j -= 1
                code[i] = code[i].replace("}", iterator+"; end while")
            else:
                code[i] = code[i].replace("}", "end for")
        initializer, condition, iterator = str(), str(), str()
    return code


def transpile_function_declarations(code):
    transpiled = list()
    contexts = list()
    main_context_len = -1
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("function ") == 0:
            if line.find("{") == len(line) - 1:
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            contexts.append(False)
        if not len(contexts) or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            transpiled.append(code[i])
            continue
        if line.find("}") == 0 and len(contexts):
            contexts.pop()
        if line.find("function ") == 0:
            start = line.find(" ") + 1
            end = line.find("(")
            name = line[start:end]
            if name.lower() == "main":
                name = "Main"
                main_context_len = len(contexts) - 1
            start = end
            end = line.rfind(")") + 1
            parameters = line[start:end][1:-1]
            if parameters:
                parameters = list(map(lambda p: p.strip(), parameters.split(", ")))
                for j in range(len(parameters)):
                    if "=" not in parameters[j]:
                        parameters[j] = parameters[j]+'="______MSE_UNSET"'
            code[i] = name+" = function"+"("+", ".join(parameters)+")"
            transpiled.append(code[i])
            for parameter in parameters:
                if "______MSE_UNSET" in parameter:
                    pname, *_ = parameter.split("=")
                    transpiled.append('if @'+pname+' == "______MSE_UNSET" then ______MSE_EXIT("MSE: '+name+'() missing required positional argument \''+pname+'\'. (line '+str(len(transpiled) + 1)+')")')
            continue
        if len(contexts) == main_context_len:
            code[i] = code[i].replace("}", "end function; Main()")
        elif line.find("}") == len(line) - 1:
            code[i] = code[i].replace("}", "end function")
        transpiled.append(code[i])
    return transpiled


def transpile_packed_variables(code):
    transpiled = list()
    for i in range(len(code)):
        line = code[i]
        parts = line.split(" = ")
        if len(parts) >= 2 and line.find("if") == -1 and line.find("while") == -1 and line.find("for") == -1 and "function" not in line and line.find("class") == -1 and line.find("namespace") == -1:
            variables, packed = map(lambda s: s.strip(), parts)
            variables = list(map(lambda s: s.strip(), variables.split(", ")))
            if len(variables) < 2:
                transpiled.append(line)
                continue
            payload = [
                "______MSE_PACKED = "+packed,
                'if not @______MSE_PACKED isa list and not @______MSE_PACKED isa map then ______MSE_EXIT("MSE: Can not unpack non-iterable "+typeof(______MSE_PACKED)+" object ('+", ".join(variables)+'). (line '+str(len(transpiled) + 1)+')")',
                'if ______MSE_PACKED isa list and ______MSE_PACKED.len != '+str(len(variables))+' then ______MSE_EXIT("MSE: Not enough or too many values to unpack ('+", ".join(variables)+'). (line '+str(len(transpiled) + 1)+')")',
                'if ______MSE_PACKED isa map and (not ______MSE_PACKED.hasIndex("key") or not ______MSE_PACKED.hasIndex("value")) then ______MSE_EXIT("MSE: Not enough or too many values to unpack ('+", ".join(variables)+'). (line '+str(len(transpiled) + 1)+')")',
            ]
            for pline in payload:
                transpiled.append(pline)
            transpiled.append("if ______MSE_PACKED isa list then")
            transpiled.append('if ______MSE_PACKED.len != '+str(len(variables))+' then ______MSE_EXIT("MSE: Not enough or too many values to unpack ('+", ".join(variables)+'). (line '+str(len(transpiled) + 1)+')")')
            for v, variable in enumerate(variables):
                transpiled.append(variable+" = @______MSE_PACKED["+str(v)+"]")
            transpiled.append("else if ______MSE_PACKED isa map then")
            transpiled.append('if not ______MSE_PACKED.hasIndex("key") or not ______MSE_PACKED.hasIndex("value") or '+str(len(variables))+' != 2 then ______MSE_EXIT("MSE: Not enough or too many values to unpack ('+", ".join(variables)+'). (line '+str(len(transpiled) + 1)+')")')
            transpiled.append(variables.pop(0)+' = @______MSE_PACKED["key"]')
            transpiled.append(variables.pop(0)+' = @______MSE_PACKED["value"]')
            transpiled.append("end if")
            transpiled.append('locals.remove("______MSE_PACKED")')
        else:
            transpiled.append(line)
    return transpiled


def transpile_increments_decrements(code):
    transpiled = list()
    recurse = False
    for i in range(len(code)):
        line = code[i]
        op = str()
        if line.find("//") != 0 and "++" in line:
            op = "+"
        elif line.find("//") != 0 and "--" in line:
            op = "-"
        if not op:
            transpiled.append(line)
            continue
        j = line.find(op*2)
        preop = False
        if j == 0 or line[j - 1] not in (string.ascii_letters + string.digits + "_"):
            preop = True
        var = str()
        payload = list()
        rnd = string_random(16)
        if preop:
            if line.find(op*2) == line.find(op*3):
                j = line.rfind(op*2)
            j += 2
            k = j + 1
            while k < len(line) and line[k - 1] in (string.ascii_letters + string.digits + "_."):
                k += 1
            # var = line[j:k - 1]
            var = line[j:k]
            # ugly hack ngl
            for char in var:
                if char not in (string.ascii_letters + string.digits + "_."):
                    var = var.replace(char, "")
            payload = [
                "______MSE_"+rnd+" = function",
                "outer."+var+" = outer."+var+" "+op+" 1",
                "return outer."+var,
                "end function",
                line.replace(op*2+var, "______MSE_"+rnd, 1),
            ]
        else:
            k = j - 1
            while k > 0 and line[k - 1] in (string.ascii_letters + string.digits + "_."):
                k -= 1
            var = line[k:j]
            payload = [
                "______MSE_"+rnd+" = function",
                "______MSE_PREVALUE = outer."+var,
                "outer."+var+" = outer."+var+" "+op+" 1",
                "return ______MSE_PREVALUE",
                "end function",
                line.replace(var+op*2, "______MSE_"+rnd, 1),
            ]
        # print(preop, [var], line, (string.ascii_letters + string.digits + "_."))
        for pline in payload:
            transpiled.append(pline)
        if line.find("//") != 0 and ("++" in line or "--" in line):
            recurse = True
    if recurse:
        return transpile_increments_decrements(transpiled)
    return transpiled


def transpile_augmented_assignments(code):
    for i in range(len(code)):
        line = code[i]
        if line.find("//") == 0:
            continue
        flag = False
        for assignment in [" += ", " -= ", " *= ", " /= ", " %= "]:
            parts = line.split(assignment)
            if len(parts) == 2:
                op = assignment[1]
                flag = True
                break
        if not flag:
            continue
        parts = list(map(lambda p: p.strip(), parts))
        var = parts[0]
        expr = parts[1]
        code[i] = var+" = "+var+" "+op+" "+expr
    return code


def transpile_classes(code):
    transpiled = list()
    contexts = list()
    name = str()
    init_params = "()"
    init_args = "()"
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("class ") == 0:
            if line.find("{") == len(line) - 1:
                init_args = "()"
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            if line.find("function Public.Init") == 0:
                start = line.find("(")
                end = line.rfind(")") + 1
                parameters = line[start:end][1:-1]
                if parameters:
                    init_params = "("+parameters+")"
                    parameters = list(map(lambda p: p.strip(), parameters.split(", ")))
                    for j in range(len(parameters)):
                        if "=" in parameters[j]:
                            parameters[j] = "@"+parameters[j][:parameters[j].find("=")]
                init_args = "("+", ".join(parameters)+")"
            contexts.append(False)
        if not len(contexts) or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            transpiled.append(code[i])
            continue
        if line.find("}") == 0 and len(contexts):
            contexts.pop()
        if line.find("class ") == 0:
            start = line.find(" ") + 1
            end = line.find("(")
            name = line[start:end].strip()
            start = end
            end = line.rfind(")") + 1
            parent = line[start:end][1:-1]
            code[i] = "function "+name+"() {"
            transpiled.append(code[i])
            prepayload = [
                "//-- MSE CLASS PRE PAYLOAD --",
                "Private = {}",
                "Public = new "+parent,
                'Public.classID = "'+name+'"',
                "//-- END CLASS PRE PAYLOAD --",
            ]
            for pline in prepayload:
                transpiled.append(pline)
            continue
        if line.find("}") == 0:
            j = len(transpiled) - 1
            while True:
                if "Virtual." in transpiled[j]:
                    if transpiled[j].find("function Virtual.") == 0:
                        transpiled[j] = transpiled[j].replace("Virtual.", "Public.")
                    else:
                        transpiled[j] = transpiled[j].replace("Virtual.", "self.")
                if transpiled[j] == "function "+name+"() {":
                    break
                j -= 1
            postpayload = [
                "//-- MSE CLASS POST PAYLOAD --",
                "function Public.______MSE_INIT"+init_params+" {",
                "}",
                'if (Public.hasIndex("Init")) {',
                'Public.______MSE_INIT = @Public["Init"]',
                "}",
                "function Public.Init"+init_params+" {",
                'Public.remove("Init")',
                "Public.______MSE_INIT"+init_args,
                'Public.remove("______MSE_INIT")',
                "return Public",
                "}",
                # 'Public.classID = "'+name+'"',
                "Public.AddObjectRelation(Public)",
                "return Public",
                "//-- END CLASS POST PAYLOAD --",
            ]
            for pline in postpayload:
                transpiled.append(pline)
            init_params = "()"
            init_args = "()"
            # code[i] = code[i].replace("}", "end function")
        transpiled.append(code[i])
    return transpiled


def transpile_namespaces(code):
    transpiled = list()
    contexts = list()
    for i in range(len(code)):
        line = code[i]
        if line.find("}") == 0 and line.find("{") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("//") != 0 and "{" in line and "}" in line and line.find("{") != 0 and line.find("}") == len(line) - 1:
            transpiled.append(line)
            continue
        if line.find("namespace ") == 0:
            if line.find("{") == len(line) - 1:
                contexts.append(True)
        elif line.find("{") == len(line) - 1:
            contexts.append(False)
        if not len(contexts) or not contexts[-1]:
            if line.find("}") == len(line) - 1 and len(contexts):
                contexts.pop()
            transpiled.append(code[i])
            continue
        if line.find("}") == 0 and len(contexts):
            contexts.pop()
        if line.find("namespace ") == 0:
            start = line.find(" ") + 1
            end = line.find(" {")
            name = line[start:end]
            code[i] = name+" = function()"
            transpiled.append(code[i])
            continue
        if line.find("}") == len(line) - 1:
            # transpiled.append('locals.classID = "Namespace"')
            # transpiled.append("return locals")
            # code[i] = code[i].replace("}", "end function; "+name+" = "+name+"()")
            payload = [
                'classID = "______MSE_NAMESPACE"',
                "return locals",
                "end function",
                "______MSE_NAMESPACE_INDEX = locals.indexes[len(locals) - 1]",
                "______MSE_NAMESPACE_FUNCTION = @locals[______MSE_NAMESPACE_INDEX]",
                "locals[______MSE_NAMESPACE_INDEX] = ______MSE_NAMESPACE_FUNCTION()",
                'locals.remove("______MSE_NAMESPACE_INDEX")',
                'locals.remove("______MSE_NAMESPACE_FUNCTION")',
            ]
            for pline in payload:
                transpiled.append(pline)
            continue
        transpiled.append(code[i])
    return transpiled


def simplify_statements(code):
    transpiled = list()
    for i in range(len(code)):
        line = code[i]
        for subline in map(lambda l: l.strip(), line.split(";")):
            transpiled.append(subline)
    return transpiled


def transpile(code):
    transpiles = [
        # Code preparation for transpiling
        simplify,
        transpile_prepends,
        transpile_classes,

        # Transpiles that has no order of execution really
        transpile_ternaries,
        transpile_while_loops,
        transpile_for_loops,
        transpile_function_declarations,
        transpile_packed_variables,
        transpile_augmented_assignments,
        transpile_namespaces,

        # Must be executed after all other transpiles
        simplify_statements,
        transpile_increments_decrements,
        beautify,
    ]
    for transpile in transpiles:
        mse_print("\tRunning "+transpile.__name__+"() ...")
        code = transpile(code)
    return code


def transpile_src(src):
    if "_o_" in src.name:
        return
    mse_print("Transpiling src \""+src.name+"\" ...")
    code = read_file(src)
    code = transpile(code)
    write_file(str(src).replace(src.name, "_o_"+src.name), code)


def transpile_directory(dir):
    mse_print("Transpiling directory \""+dir.name+"\" ...")
    for p in dir.iterdir():
        if p.is_dir():
            transpile_directory(p)
        else:
            transpile_src(p)


DEBUG = False
def main(argv):
    init(autoreset=True)
    if argv == []:
        mse_print("No files for transpiling. Quiting...")
        sys.exit(1)
    for path in argv:
        path = pathlib.Path(path)
        if not path.exists():
            mse_print("Path does not exist: "+str(path))
        elif path.is_dir():
            transpile_directory(path)
        else:
            transpile_src(path)
    deinit()


if __name__ == "__main__":
    main(sys.argv[1:])