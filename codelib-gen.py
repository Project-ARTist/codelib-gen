#!/usr/bin/python3
#
# The ARTist Project (https://artist.cispa.saarland)
#
# Copyright (C) 2018 CISPA (https://cispa.saarland), Saarland University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @author "Oliver Schranz <oliver.schranz@cispa.saarland>"
# @author "Sebastian Weisgerber <weisgerber@cispa.saarland>"
# @author "Alexander Fink <alexander.fink@cispa.saarland>"
#
import argparse
import logging
import javalang
from javalang.tree import *
import sys
import re

__author__ = 'Sebastian Weisgerber <weisgerber@cispa.saarland>, Alexander Fink <alexander.fink@cispa.saarland>'
__version__ = '0.0.1-beta'  # TODO pull from latest git tag?
__tool_name__ = 'CodeLibGen'

print(__tool_name__ + ' (' + __version__ + ') Python Version: ' + sys.version)

logger = None


class CodeLibDefaults:
    CLASSES = [
        'java.lang.String',
        'java.lang.Object',
    ]

class Constants:

    def __init__(self, classname="GeneratedCodeLib"):

        self.CODELIB_CLASSNAME = classname
        self.CODELIB_CLASSNAME_PREFIX = self.CODELIB_CLASSNAME + '::'
        self.CODELIB_METHOD_SET_START = self.INDENT_SOURCE + 'unordered_set<string> &'+self.CODELIB_CLASSNAME+'::getMethods() const {\n' + \
                                   self.INDENT_SOURCE + self.INDENT + 'static unordered_set<string> methods({'
        self.CODELIB_METHOD_SET_END = self.INDENT_SOURCE + self.INDENT + '});\n' + \
                                 self.INDENT_SOURCE + self.INDENT + 'return methods;\n' + \
                                      self.INDENT_SOURCE + '}'

        self.CODELIB_GETTERS = self.INDENT_SOURCE + "string &" + self.CODELIB_CLASSNAME + "::getInstanceField() const {\n" \
                          + self.INDENT_SOURCE + self.INDENT + "static string instanceField = " + self.CODELIB_CLASSNAME + "::_F_CODECLASS_INSTANCE;\n" \
                          + self.INDENT_SOURCE + self.INDENT + "return instanceField;\n" \
                          + self.INDENT_SOURCE + "}\n\n" \
                          + self.INDENT_SOURCE + "string &" + self.CODELIB_CLASSNAME + "::getCodeClass() const {\n" \
                          + self.INDENT_SOURCE + self.INDENT + "static string codeClass = " + self.CODELIB_CLASSNAME + "::_C_CODECLASS;\n" \
                          + self.INDENT_SOURCE + self.INDENT + "return codeClass;\n" \
                          + self.INDENT_SOURCE + "}\n"

    CODELIB_H = 'codelib.h'
    CODELIB_CC = 'codelib.cc'

    CODELIB_H_TEMPLATE_START = 'res/codelib_header.h'
    CODELIB_H_TEMPLATE_END = 'res/codelib_footer.h'
    CODELIB_CC_TEMPLATE_START = 'res/codelib_header.cc'
    CODELIB_CC_TEMPLATE_END = 'res/codelib_footer.cc'


    SOURCE_COMMENT_METHODS = '// METHODS //////////////////////////////////'
    SOURCE_COMMENT_FIELDS = '// FIELDS ///////////////////////////////////'
    SOURCE_COMMENT_CLASSES = '// CLASSES //////////////////////////////////'

    INDENT = 4*' '
    INDENT_HEADER = 4*' '
    INDENT_SOURCE = 0*' '

    CODELIB_VARIABLE_TYPE_H = 'static const string'
    CODELIB_VARIABLE_TYPE_SRC = 'const string'

    CODELIB_VARNAME_PREFIX_METHOD = '_M_'
    CODELIB_VARNAME_PREFIX_FIELD = '_F_'
    CODELIB_VARNAME_PREFIX_CLASS = '_C_'


    CODELIB_VARNAME_INSTANCE_FIELD = CODELIB_VARNAME_PREFIX_FIELD + 'CODECLASS_INSTANCE'
    CODELIB_VARNAME_CODECLASS = CODELIB_VARNAME_PREFIX_CLASS + 'CODECLASS'


SourceConstants = Constants()

class CodeLibGenerator:
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

    java_source_file_path = None
    java_source_folder_root = None
    java_package_name_strip = ""

    imports = list()
    methods = dict()
    fields = dict()
    classes = dict()

    def __init__(self, args):
        global SourceConstants
        if args.name:
            SourceConstants = Constants(args.name)
        else:
            SourceConstants = Constants(args.module_name.capitalize()+"CodeLib")
        self.java_source_file_path = args.java_file
        self.java_source_folder_root = args.source_root
        self.module_folder_name = args.module_name
        self.java_package_name_strip = str(self.java_source_folder_root) \
            .replace('/', '.') \
            .replace('\\', '.') \
            .rstrip('.') \
            .lstrip('.')
        self.java_package_name_strip += '.'

        log('Generating codelib sources for: ' + self.java_source_file_path)

    def is_singleton_instance_field(self, member):
        return str(member.declarators[0].name).lower() == 'instance'

    def convert_class_package_path(self, classPackagePath):
        return 'L' + str(classPackagePath).replace('.', '/') + ';'

    def get_method_return_type(self, imports, member):
        return_string = ''

        if (member.return_type != None and member.return_type.name != None):
            return_string += self.get_type_string_java(imports, member.return_type)
        else:
            return_string += self.java_type_map['void']
        return return_string

    def get_type_string_java(self, imports, type):
        type_string_java = ''
        type_name = type.name
        logd('Looking up: ' + type_name)
        try:
            type_string_java += self.java_type_map[type_name]
        except KeyError:
            logd('Looking up: ' + type_name + ' -> KeyError')
            found = False
            for imprt in imports:
                if str(imprt).endswith(str(type_name)):
                    type_string_java += self.convert_class_package_path(imprt)
                    logd('Looking up: ' + type_name + ' Imports: Found: ' + type_string_java)
                    found = True
                    break
            if not found:
                type_string_java += self.convert_class_package_path('java.lang.' + type_name)
                logd('Looking up: ' + type_name + ' Imports: NOT Found: ' + type_string_java)

        return type_string_java

    def get_parameter_string_java(self, imports, class_name, parameters):
        parameter_string_java = ''
        for param in parameters:
            parameter_string_java += self.get_type_string_java(imports, param.type)
            # if (param.varargs == True):
            #     parameter_string_java += '...'
        return parameter_string_java

    def get_shortened_class_types(self, java_type_string):
        """
        Replaces all Object Types with 'L'

        :param java_type_string: chain of Java types [1...n] e.g.: BCDFLjava/lang/String;IJSZV[
        :return: Replaced type String BCDFLIJSZV[
        """
        return re.sub(r"L.+?;", 'L', java_type_string)

    def generate_method_string_java(self, imports, class_name, member):
        parameter_signature = self.get_parameter_string_java(imports, class_name, member.parameters)
        return_type = self.get_method_return_type(imports, member)

        class_name_tokens = str(class_name).split('.')

        variable_name = ''
        variable_name += SourceConstants.CODELIB_VARNAME_PREFIX_METHOD
        for class_name_token in class_name_tokens:
            variable_name += (class_name_token + '_')
        variable_name += '_'
        variable_name += member.name
        variable_name += '__'
        variable_name += self.get_shortened_class_types(parameter_signature)
        variable_name += '__'
        variable_name += self.get_shortened_class_types(return_type)
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

        self.methods[method_signature] = variable_name

        return method_signature

    def generate_field_string_java(self, class_name, member, proposed_variable_name=None):

        class_name_tokens = str(class_name).split('.')

        variable_name = ''
        if (proposed_variable_name is None):
            variable_name += SourceConstants.CODELIB_VARNAME_PREFIX_FIELD
            for class_name_token in class_name_tokens:
                variable_name += (class_name_token + '_')
            variable_name += '_'
            variable_name += member.declarators[0].name
            variable_name = variable_name.upper()
        else:
            variable_name = proposed_variable_name

        field_signature = ''
        field_signature += 'L'
        field_signature += class_name + ';'
        field_signature += member.declarators[0].name
        field_signature = str(field_signature).replace('.', '/')
        self.fields[field_signature] = variable_name
        return field_signature

    def generate_class_string_java(self, class_name, proposed_variable_name=None):

        class_name_tokens = str(class_name).split('.')

        variable_name = ''
        if (proposed_variable_name is None):
            variable_name += SourceConstants.CODELIB_VARNAME_PREFIX_CLASS
            for class_name_token in class_name_tokens:
                variable_name += (class_name_token + '_')
            variable_name = variable_name.rstrip('_').upper()
        else:
            variable_name = proposed_variable_name

        class_signature = ''
        class_signature += 'L'
        class_signature += class_name + ';'
        class_signature = str(class_signature).replace('.', '/')
        self.classes[class_signature] = variable_name
        return class_signature

    def write_codelib_source_file(self):
        # Source File Writing
        log('Writing Source: ' + SourceConstants.CODELIB_CC)
        codelib_source_file = open(SourceConstants.CODELIB_CC, 'w')
        source_template_head = open(SourceConstants.CODELIB_CC_TEMPLATE_START, 'r')
        source_template_foot = open(SourceConstants.CODELIB_CC_TEMPLATE_END, 'r')

        codelib_source_file.write(source_template_head.read())
        codelib_source_file.write('\n')
        codelib_source_file.write(SourceConstants.INDENT_SOURCE + SourceConstants.SOURCE_COMMENT_METHODS + '\n')
        log('> Methods: #' + str(len(self.methods)))
        for key, value in self.methods.items():
            codelib_source_file.write(SourceConstants.INDENT_SOURCE + SourceConstants.CODELIB_VARIABLE_TYPE_SRC
                                      + ' ' + SourceConstants.CODELIB_CLASSNAME_PREFIX
                                      + value + ' =\n    "' + key + '";\n')

        codelib_source_file.write('\n')

        codelib_source_file.write(SourceConstants.INDENT_SOURCE + SourceConstants.SOURCE_COMMENT_FIELDS + '\n')
        log('> Fields:  #' + str(len(self.fields)))
        for key, value in self.fields.items():
            codelib_source_file.write(
                SourceConstants.INDENT_SOURCE
                + SourceConstants.CODELIB_VARIABLE_TYPE_SRC
                + ' ' + SourceConstants.CODELIB_CLASSNAME_PREFIX
                + value + ' =\n    "' + key + '";\n')

        codelib_source_file.write('\n')

        codelib_source_file.write(
            SourceConstants.INDENT_SOURCE +
            SourceConstants.SOURCE_COMMENT_CLASSES + '\n')
        log('> Classes: #' + str(len(self.classes)))
        for key, value in self.classes.items():
            codelib_source_file.write(
                SourceConstants.INDENT_SOURCE
                + SourceConstants.CODELIB_VARIABLE_TYPE_SRC
                + ' ' + SourceConstants.CODELIB_CLASSNAME_PREFIX
                + value + ' =\n    "' + key + '";\n')

        codelib_source_file.write('\n')

        codelib_source_file.write(SourceConstants.CODELIB_METHOD_SET_START + '\n')
        for key, value in self.methods.items():
            codelib_source_file.write(SourceConstants.INDENT + SourceConstants.CODELIB_CLASSNAME_PREFIX + value + ',\n')
        codelib_source_file.write(SourceConstants.CODELIB_METHOD_SET_END + '\n')

        codelib_source_file.write('\n')

        codelib_source_file.write(SourceConstants.CODELIB_GETTERS)

        codelib_source_file.write('\n')

        codelib_source_file.write(source_template_foot.read())
        codelib_source_file.close()
        source_template_head.close()
        source_template_foot.close()
        log('')

    def write_codelib_header_file(self):
        log('Writing Header: ' + SourceConstants.CODELIB_H)
        # Header File Writing
        codelib_header_file = open(SourceConstants.CODELIB_H, 'w')
        header_file_start = open(SourceConstants.CODELIB_H_TEMPLATE_START, 'r')
        header_file_end = open(SourceConstants.CODELIB_H_TEMPLATE_END, 'r')

        codelib_header_file.write(header_file_start.read().replace("ModuleCodeLib", SourceConstants.CODELIB_CLASSNAME)
                                  .replace("CHANGEME", self.module_folder_name.upper()))
        codelib_header_file.write(
            SourceConstants.INDENT_HEADER + SourceConstants.SOURCE_COMMENT_METHODS + '\n')
        log('> Methods: #' + str(len(self.methods)))
        for key, value in self.methods.items():
            codelib_header_file.write(
                SourceConstants.INDENT_HEADER + SourceConstants.CODELIB_VARIABLE_TYPE_H + ' ' + value + ';\n')
        codelib_header_file.write(
            SourceConstants.INDENT_HEADER + SourceConstants.SOURCE_COMMENT_FIELDS + '\n')
        log('> Fields:  #' + str(len(self.fields)))
        for key, value in self.fields.items():
            codelib_header_file.write(
                SourceConstants.INDENT_HEADER + SourceConstants.CODELIB_VARIABLE_TYPE_H + ' ' + value + ';\n')
        codelib_header_file.write(SourceConstants.INDENT_HEADER + SourceConstants.SOURCE_COMMENT_CLASSES + '\n')
        log('> Classes: #' + str(len(self.classes)))
        for key, value in self.classes.items():
            codelib_header_file.write(
                SourceConstants.INDENT_HEADER + SourceConstants.CODELIB_VARIABLE_TYPE_H + ' ' + value + ';\n')
        codelib_header_file.write(header_file_end.read().replace("ModuleCodeLib", SourceConstants.CODELIB_CLASSNAME)
                                  .replace("CHANGEME", self.module_folder_name.upper()))

        codelib_header_file.close()
        header_file_start.close()
        header_file_end.close()
        log('')

    def setup_package_name(self, compilation_unit):
        return str(compilation_unit.package.name).lstrip(self.java_package_name_strip)

    def setup_imports(self, compilation_unit):
        for imprt in compilation_unit.imports:
            self.imports.append(imprt.path)

    def Run(self):
        # Code ###################################
        codelib_source_file = open(self.java_source_file_path, 'r')
        compilation_unit = javalang.parse.parse(codelib_source_file.read())

        package_name = self.setup_package_name(compilation_unit)

        self.setup_imports(compilation_unit)

        log('')
        log('Package: ' + package_name)
        log('> TypeCount: ' + ''.join(map(str, compilation_unit.types)) + ' (Count: ' + str(
            len(compilation_unit.types)) + ')')
        log('')

        self.SetupDefaultMembers()

        for child in compilation_unit.types:
            logd(child)
            class_name = package_name + '.' + child.name
            log("> Parsing Class: " + class_name)
            log('')
            if isinstance(child, ClassDeclaration):
                class_string = self.generate_class_string_java(class_name, SourceConstants.CODELIB_VARNAME_CODECLASS)

                logd(class_string)

                for class_member in child.body:
                    if isinstance(class_member, MethodDeclaration):
                        annotations = class_member.children[2]
                        for annotation in annotations:
                            # only use annotated functions
                            if "Inject" in annotation.children:
                                method_string = self.generate_method_string_java(self.imports, class_name, class_member)
                                logd(method_string)
                                break
                    elif isinstance(class_member, FieldDeclaration):
                        if (self.is_singleton_instance_field(class_member)):
                            field_string = self.generate_field_string_java(
                                class_name,
                                class_member,
                                SourceConstants.CODELIB_VARNAME_INSTANCE_FIELD)
                            logd(field_string)
                    elif isinstance(class_member, ConstructorDeclaration):
                        pass
            else:
                loge('No ClassDeclaration')

        self.write_codelib_header_file()

        self.write_codelib_source_file()

    def SetupDefaultMembers(self):
        for class_name in CodeLibDefaults.CLASSES:
            self.generate_class_string_java(class_name)


def setup_logger():
    global logger
    if (logger == None):
        logger = logging.getLogger('codelib')
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())


def log(message):
    global logger
    setup_logger()
    logger.info(message)


def loge(message):
    global logger
    setup_logger()
    logger.error(message)


def logd(message):
    global logger
    setup_logger()
    logger.debug(message)


def main(args):
    codelib_generator = CodeLibGenerator(args)
    codelib_generator.Run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Artist helper tool. Generates codelib.h/.cc files for the specified java source file.'
    )

    parser.add_argument('java_file',
                        metavar='<path-to-java-source>',
                        action='store',
                        help='Path to the java source file for which the codelib.h/.cc should get generated\”'
                             'Class must be in package-names subfolders, e.g.: ./java/lang/Object.java')

    parser.add_argument('module_name',
                        metavar='<module-name>',
                        action='store',
                        help='Name of the artist module folder. '
                             'E.g. "mymodule" if the codelib will be used in artist/modules/mymodule')

    parser.add_argument('-n', '--name',
                        metavar='<name>',
                        action='store',
                        help='Set a custom class name for the CodeLib. Default: "<module-name>CodeLib"')

    parser.add_argument('-s', '--source_root',
                        metavar='<source_root>',
                        action='store',
                        help='Path to the folder, where the first java package-name folder is.'
                             'E.g.: "app/src/main/java/" if your file is '
                             'in folder ">app/src/main/java/<java/lang/Object.java"')

    args = parser.parse_args()

    main(args)
