#!/usr/bin/python3

import javalang
from javalang.tree import *

INDENT_HEADER = '  '

def is_singleton_instance_field(member):
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
codelib_source_file = open(source_file_path, 'r')
compilationUnit = javalang.parse.parse(codelib_source_file.read())

imports = list()
methods = dict()
fields = dict()
classes = dict()

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

    if (member.return_type != None and member.return_type.name != None):
        return_string += get_type_string_java(imports, classname, member.return_type)
    else:
        return_string += java_type_map['void']
    return return_string

def get_type_string_java(imports, class_name, type):
    type_string_java = ''
    type_name = type.name
    print('Looking up: ' + type_name)
    try:
        type_string_java += java_type_map[type_name]
    except KeyError:
        print('Looking up: ' + type_name + ' -> KeyError')
        found = False
        for imprt in imports:
            if str(imprt).endswith(str(type_name)):
                type_string_java += convert_class_package_path(imprt)
                print('Looking up: ' + type_name + ' Imports: Found: ' + type_string_java)
                found = True
                break
        if not found:
            type_string_java += convert_class_package_path('java.lang.' + type_name)
            print('Looking up: ' + type_name + ' Imports: NOT Found: ' + type_string_java)
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
    variable_name += return_type.upper().replace('LJAVA/LANG/OBJECT;', 'L').replace('LJAVA/LANG/STRING;', 'L').replace('LANDROID/CONTENT/CONTEXT;', 'L')
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


def generate_field_string_java(class_name, member):
    global fields

    class_name_tokens = str(class_name).split('.')

    variable_name = ''
    variable_name += codelib_variable_name_prefix_field
    for class_name_token in class_name_tokens:
        variable_name += (class_name_token + '_')
    variable_name += '_'
    variable_name += member.declarators[0].name
    variable_name = variable_name.upper()

    field_signature = ''
    field_signature += 'L'
    field_signature += class_name + ';'
    field_signature += member.declarators[0].name
    field_signature = str(field_signature).replace('.', '/')
    fields[field_signature] = variable_name
    return field_signature

def generate_class_string_java(class_name):
    global classes

    class_name_tokens = str(class_name).split('.')

    variable_name = ''
    variable_name += codelib_variable_name_prefix_class
    for class_name_token in class_name_tokens:
        variable_name += (class_name_token + '_')
    variable_name = variable_name.rstrip('_').upper()

    class_signature = ''
    class_signature += 'L'
    class_signature += class_name + ';'
    class_signature = str(class_signature).replace('.', '/')
    classes[class_signature] = variable_name
    return class_signature

def write_codelib_source_file():
    global methods, fields, classes
    # Source File Writing
    codelib_source_file = open('codelib.cc', 'w')
    source_template_head = open('res/codelib_header.cc', 'r')
    source_template_foot = open('res/codelib_footer.cc', 'r')

    codelib_source_file.write(source_template_head.read())
    codelib_source_file.write(
        '// METHODS //////////////////////////////////////////////////'
        '/////////////////////////////////////////////////////////\n')
    for key, value in methods.items():
        codelib_source_file.write(
            codelib_variable_type_source + ' ' + codelib_class_prefix + value + ' =\n    "' + key + '";\n')

    codelib_source_file.write('\n')

    codelib_source_file.write(
        '// Fields /////////////////////////////////////////////////////'
        '///////////////////////////////////////////////////////\n')
    for key, value in fields.items():
        codelib_source_file.write(
            codelib_variable_type_source + ' ' + codelib_class_prefix + value + ' =\n    "' + key + '";\n')

    codelib_source_file.write('\n')

    codelib_source_file.write(
        '// Classes //////////////////////////////////////////////////////'
        '/////////////////////////////////////////////////////\n')
    for key, value in classes.items():
        codelib_source_file.write(
            codelib_variable_type_source + ' ' + codelib_class_prefix + value + ' =\n    "' + key + '";\n')

    codelib_source_file.write('\n')

    codelib_source_file.write(codelib_methods_start + '\n')
    for key, value in methods.items():
        codelib_source_file.write('    ' + codelib_class_prefix + value + ',\n')
    codelib_source_file.write(codelib_methods_end + '\n')

    codelib_source_file.write('\n')

    codelib_source_file.write(source_template_foot.read())
    codelib_source_file.close()
    source_template_head.close()
    source_template_foot.close()

def write_codelib_header_file():
    global methods, fields, classes

    # Header File Writing
    codelib_header_file = open('codelib.h', 'w')
    header_file_start = open('res/codelib_header.h', 'r')
    header_file_end = open('res/codelib_footer.h', 'r')

    codelib_header_file.write(header_file_start.read())
    codelib_header_file.write(
        '  // METHODS ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
    for key, value in methods.items():
        codelib_header_file.write(INDENT_HEADER + codelib_variable_type_header + ' ' + value + ';\n')
    codelib_header_file.write(
        '  // Fields ////////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
    for key, value in fields.items():
        codelib_header_file.write(INDENT_HEADER + codelib_variable_type_header + ' ' + value + ';\n')
    codelib_header_file.write(
        '  // Classes ///////////////////////////////////////////////////////////////////////////////////////////////////////////\n')
    for key, value in classes.items():
        codelib_header_file.write(INDENT_HEADER + codelib_variable_type_header + ' ' + value + ';\n')
    codelib_header_file.write(header_file_end.read())

    codelib_header_file.close()
    header_file_start.close()
    header_file_end.close()

generate_class_string_java('java.lang.String')

for child in compilationUnit.types:
    # print(child)
    class_name = package_name + '.' + child.name
    print("Class: " + class_name)
    print('')
    if isinstance(child, ClassDeclaration):
        generate_class_string_java(class_name)
        for class_member in child.body:
            if isinstance(class_member, MethodDeclaration):
                generate_method_string_java(imports, class_name, class_member)
            elif isinstance(class_member, FieldDeclaration):
                if (is_singleton_instance_field(class_member)):
                    field_string = generate_field_string_java(class_name, class_member)
                    print(field_string)
            elif isinstance(class_member, ConstructorDeclaration):
                ctor_string = ''
                ctor_string += ('> CTOR: ' + class_name + '.' + class_member.name + '()')
                print(ctor_string)
    else:
        print('No ClassDeclaration')

write_codelib_header_file()

write_codelib_source_file()
