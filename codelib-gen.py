#!/usr/bin/python3

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

codelib_class_name = 'CodeLib'
codelib_class_prefix = codelib_class_name + '::'
codelib_variable_type_header = 'static const std::string'
codelib_variable_type_source = 'const std::string'
codelib_variable_name_prefix_method = '_M_'
codelib_variable_name_prefix_field = '_F_'
codelib_variable_name_prefix_class = '_C_'

codelib_methods_start = 'const std::unordered_set<std::string> CodeLib::METHODS({'
codelib_methods_end = '});'

source_file_path = 'test/app/src/main/java/de/infsec/tainttracking/taintlib/TaintLib.java'
source_file = open(source_file_path, 'r')
compilationUnit = javalang.parse.parse(source_file.read())

imports = list()
methods = dict()
fields = dict()
constants = dict()

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
        # if (param.varargs == True):
        #     parameter_string_java += '...'
    return parameter_string_java

def generate_method_string_java(imports, class_name, member):
    global methods
    parameter_signature = get_parameter_string_java(imports, class_name, member.parameters)
    return_type = get_method_return_type(imports, class_name, member)

    class_name_tokens = str(class_name).split('.')

    variable_name = ''
    variable_name += codelib_variable_name_prefix_method
    for class_name_token in class_name_tokens:
        variable_name += (class_name_token + '_')
    variable_name += '_'
    variable_name += member.name
    variable_name += '__'
    variable_name += parameter_signature.upper().replace('LJAVA/LANG/OBJECT;', 'L').replace('LJAVA/LANG/STRING;', 'L').replace('LANDROID/CONTENT/CONTEXT;', 'L')
    variable_name += '__'
    variable_name += return_type
    variable_name = variable_name.upper()

    method_signature = ''
    method_signature += 'L'
    method_signature += (class_name + ';' + member.name)
    method_signature = method_signature.replace('.', '/')
    method_signature += '('

    method_signature += parameter_signature

    method_signature = method_signature.rstrip(', ')
    method_signature += ')'
    method_signature += return_type

    methods[method_signature] = variable_name

    return method_signature


def generate_field_string_java():
    field_string = ''
    field_string += '> F: '
    field_string += 'L'
    field_string += class_name + ';'
    field_string += member.declarators[0].name
    field_string = str(field_string).replace('.', '/')
    return field_string


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
                method_string_java = generate_method_string_java(imports, class_name, member)
                # print(method_string_java)
                # method_string_readable = get_method_string_readable(imports, class_name, member)
                # print(method_string_readable)
            elif isinstance(member, FieldDeclaration):
                if (is_singleton_instance_field()):
                    field_string = generate_field_string_java()
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


header_file = open('codelib.h', 'w')
source_file = open('codelib.cc', 'w')

header_template_head = open('res/codelib_header.h', 'r')
header_template_foot = open('res/codelib_footer.h', 'r')

source_template_head = open('res/codelib_header.cc', 'r')
source_template_foot = open('res/codelib_footer.cc', 'r')

header_file.write(header_template_head.read())
header_file.write('  // METHODS ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')

source_file.write(source_template_head.read())
source_file.write('// METHODS ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')

for key, value in methods.items():
    header_file.write('  ' + codelib_variable_type_header + ' ' + value + ';\n')
    source_file.write(codelib_variable_type_source + ' ' + codelib_class_prefix + value + ' =\n    "' + key + '";\n')

source_file.write('\n')
source_file.write(codelib_methods_start + '\n')
for key, value in methods.items():
    source_file.write('    ' + codelib_class_prefix + value + ',\n')
source_file.write(codelib_methods_end + '\n')

header_file.write('  // Fields ////////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
header_file.write('  // Classes ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
header_file.write(header_template_foot.read())

source_file.write('// Fields ////////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
source_file.write('// Classes ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
source_file.write(source_template_foot.read())

header_file.close()
source_file.close()
header_template_head.close()
header_template_foot.close()
source_template_head.close()
source_template_foot.close()
