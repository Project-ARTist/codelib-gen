import javalang
from javalang.tree import *

def is_singleton_instance_field():
    return str(member.declarators[0].name).lower() == 'instance'

java_type_map = {
    'byte': 'B',
    'char': 'C',
    'double': 'D',
    'float': 'F',
    'int': 'I',
    'long': 'J',
    'short': 'S',
    'boolean': 'Z',
    'void': 'V',
    'ClassName': 'L',
    'reference': '[',
}

source_file_path = 'test/app/src/main/java/de/infsec/tainttracking/taintlib/TaintLib.java'
source_file = open(source_file_path, 'r')
compilationUnit = javalang.parse.parse(source_file.read())

imports = list()

package_name = str(compilationUnit.package.name).lstrip('app.src.main.java.')

for imprt in compilationUnit.imports:
    print('Import: ' + imprt.path)
    imports.append(imprt.path)
print('')

print('Package: ' + package_name)
# print(compilationUnit.imports)
print('Types: ' + ''.join(map(str, compilationUnit.types)) + ' (Count: ' + str(len(compilationUnit.types)) + ')')

def convert_class_package_path(classPackagePath):
    return 'L' + str(classPackagePath).replace('.', '/') + ';'

def get_method_return_type(imports, classname, member):
    return_string = ''
    if isinstance(member.return_type, BasicType):
        if (member.return_type.name != None):
            return_string += get_type_string_java(imports, classname, member.return_type)
    else:
        return_string += java_type_map['void']
    return_string += ' '
    return return_string


def get_method_string_readable(imports, class_name, member):
    method_string_readable = ''
    method_string_readable += '> M: '
    method_string_readable += get_method_return_type(imports, class_name, member)
    method_string_readable += (class_name + '.' + member.name)
    method_string_readable += '('
    for param in member.parameters:
        method_string_readable += param.type.name
        if (param.varargs == True):
            method_string_readable += '...'
        method_string_readable += ' ' + param.name + ', '
    method_string_readable = method_string_readable.rstrip(', ')
    method_string_readable += ')'
    return method_string_readable

def get_type_string_java(imports, class_name, type):
    type_string_java = ''
    try:
        type_string_java += java_type_map[type.name]
    except KeyError:
        found = False
        for imprt in imports:
            if str(type.name) in str(imprt):
                type_string_java += convert_class_package_path(imprt)
                found = True
                break
        if not found:
            type_string_java += convert_class_package_path('java.lang.' + type.name)
    return type_string_java

def get_parameter_string_java(imports, class_name, parameters):
    parameter_string_java = ''
    for param in parameters:
        parameter_string_java += get_type_string_java(imports, class_name, param.type)
        if (param.varargs == True):
            parameter_string_java += '...'
    return parameter_string_java

def get_method_string_java(imports, class_name, member):
    method_string_java = ''
    method_string_java += 'L'
    method_string_java += (class_name + ';' + member.name)
    method_string_java = method_string_java.replace('.', '/')
    method_string_java += '('
    method_string_java += get_parameter_string_java(imports, class_name, member.parameters)

    method_string_java = method_string_java.rstrip(', ')
    method_string_java += ')'
    method_string_java += get_method_return_type(imports, class_name, member)
    return method_string_java


for child in compilationUnit.types:
    # print(child)
    class_name = package_name + '.' + child.name
    print("Class: " + class_name)
    print('')
    if isinstance(child, ClassDeclaration):
        # print('> C: ' + class_name)
        # print(child.body)
        for member in child.body:
            if isinstance(member, MethodDeclaration):
                method_string_java = get_method_string_java(imports, class_name, member)
                print(method_string_java)

                # method_string_readable = get_method_string_readable(imports, class_name, member)
                # print(method_string_readable)
            elif isinstance(member, FieldDeclaration):
                if (is_singleton_instance_field()):
                    field_string = ''
                    field_string += '> F: '
                    field_string += 'L'
                    field_string += class_name + ';'
                    field_string += member.declarators[0].name
                    field_string = str(field_string).replace('.', '/')
                    print(field_string)
                    # print(member.type.dimensions)
            elif isinstance(member, ConstructorDeclaration):
                ctor_string = ''
                ctor_string += ('> CTOR: ' + class_name + '.' + member.name + '()')
                print(ctor_string)
        # print(child.type_parameters)
        # print(child.extends.name)
        # print(child.implements)
    else:
        print('No ClassDeclaration')



