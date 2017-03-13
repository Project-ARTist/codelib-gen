import javalang
from javalang.tree import ClassDeclaration, Type, Import, CompilationUnit, MethodDeclaration, FieldDeclaration, \
    BasicType, VariableDeclarator, ConstructorDeclaration

def is_singleton_instance_field():
    return str(member.declarators[0].name).lower() == 'instance'


source_file_path = 'test/app/src/main/java/de/infsec/tainttracking/taintlib/TaintLib.java'
source_file = open(source_file_path, 'r')
compilationUnit = javalang.parse.parse(source_file.read())

package_name = str(compilationUnit.package.name).lstrip('app.src.main.java.')

print('Package: ' + package_name)
# print(compilationUnit.imports)
print('Types: ' + ''.join(map(str, compilationUnit.types)) + ' (Count: ' + str(len(compilationUnit.types)) + ')')

def get_method_return_type(member):
    return_string = ''
    if isinstance(member.return_type, BasicType):
        if (member.return_type.name != None):
            return_string += (member.return_type.name + ' ')
    else:
        return_string += 'void '
    return return_string


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
                java_method_string = ''
                readable_method_string = ''
                readable_method_string += '> M: '

                readable_method_string = get_method_return_type(member)

                readable_method_string += (class_name + '.' + member.name)
                readable_method_string += '('

                for param in member.parameters:
                    readable_method_string += param.name + ', '

                if (member.type_parameters != None):
                    for param_type in member.type_parameters:
                        print('> param_type: ' + param_type)
                        print('> param_type: ' + param_type.name)

                readable_method_string = readable_method_string.rstrip(', ')
                readable_method_string += ')'
                print(readable_method_string)
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



