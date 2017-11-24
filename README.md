# codelib-gen - CodeLib Native Sources Generator [![Gitter](https://badges.gitter.im/Project-ARTist/meta.svg)](https://gitter.im/project-artist/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=body_badge)

This small utiity generates codelib header and source files from Java sources.

## Used Libraries

> codelib-gen uses the Python-library [javalang](https://github.com/c2nes/javalang), which is free to use and modify.
> See [javalang/LICENSE.txt](javalang/LICENSE.txt)

## Usage

```
$ ./codelib-gen.py -h
CodeLibGen (1.0.0 RC1) Python Version: 3.6.0 (default, Jan 16 2017, 12:12:55) 
[GCC 6.3.1 20170109]
usage: codelib-gen.py [-h] [-s <source_root>] <path-to-java-source>

Artist helper tool. Generates codelib.h/.cc files for the specified java
source file.

positional arguments:
  <path-to-java-source>
                        Path to the java source file for which the
                        codelib.h/.cc should get generated\”Class must be in
                        package-names subfolders, e.g.:
                        ./java/lang/Object.java

optional arguments:
  -h, --help            show this help message and exit
  -s <source_root>, --source_root <source_root>
                        Path to the folder, where the first java package-name
                        folder is.E.g.: "app/src/main/java/" if your file is
                        in folder ">app/src/main/java/<java/lang/Object.java"

```
