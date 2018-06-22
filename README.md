# codelib-gen - CodeLib Native Sources Generator 

[![Gitter](https://badges.gitter.im/Project-ARTist/meta.svg)](https://gitter.im/project-artist/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=body_badge)


codelig-gen is a handy tool in the [ARTist](https://github.com/Project-ARTist/ARTist) toolchain that automates the generation of a [CodeLib's](https://github.com/Project-ARTist/CodeLib) native counterparts. It essentially scans a provided CodeLib for its class, method and field signatures and generates a C++ class that exposes those to the ARTist framework. 

For more information on the ARTist framework and ecosystem, check out the dedicated section below. 

## Usage

```
$ ./codelib-gen.py -h
CodeLibGen (1.0.0 RC2) Python Version: 3.6.1 (default, Apr 29 2017, 18:44:06) 
[GCC 5.4.0 20160609]
usage: codelib-gen.py [-h] [-n <name>] [-s <source_root>]
                      <path-to-java-source> <module-name>

Artist helper tool. Generates codelib.h/.cc files for the specified java
source file.

positional arguments:
  <path-to-java-source>
                        Path to the java source file for which the
                        codelib.h/.cc should get generated\”Class must be in
                        package-names subfolders, e.g.:
                        ./java/lang/Object.java
  <module-name>         Name of the artist module folder. E.g. "mymodule" if
                        the codelib will be used in artist/modules/mymodule

optional arguments:
  -h, --help            show this help message and exit
  -n <name>, --name <name>
                        Set a custom class name for the CodeLib. Default:
                        "<module-name>CodeLib"
  -s <source_root>, --source_root <source_root>
                        Path to the folder, where the first java package-name
                        folder is.E.g.: "app/src/main/java/" if your file is
                        in folder ">app/src/main/java/<java/lang/Object.java"

```

## Used Libraries

> codelib-gen uses the Python-library [javalang](https://github.com/c2nes/javalang), which is free to use and modify.
> See [javalang/LICENSE.txt](javalang/LICENSE.txt)


# ARTist - The Android Runtime Instrumentation and Security Toolkit

ARTist is a flexible open source instrumentation framework for Android's apps and Java middleware. It is based on the Android Runtime’s (ART) compiler and modifies code during on-device compilation. In contrast to existing instrumentation frameworks, it preserves the application's original signature and operates on the instruction level. 

ARTist can be deployed in two different ways: First, as a regular application using our [ArtistGui](https://github.com/Project-ARTist/ArtistGui) project that allows for non-invasive app instrumentation on rooted devices, or second, as a system compiler for custom ROMs where it can additionally instrument the system server (Package Manager Service, Activity Manager Service, ...) and the Android framework classes (```boot.oat```). It supports Android versions after (and including) Marshmallow 6.0. 

For detailed tutorials and more in-depth information on the ARTist ecosystem, have a look at our [official documentation](https://artist.cispa.saarland) and join our [Gitter chat](https://gitter.im/project-artist/Lobby).

## Upcoming Beta Release

We are about to enter the beta phase soon, which will bring a lot of changes to the whole ARTist ecosystem, including a dedicated ARTist SDK for simplified Module development, a semantic versioning-inspired release and versioning scheme, an improved and updated version of our online documentation, great new Modules, and a lot more improvements. However, in particular during the transition phase, some information like the one in the repositories' README.md files and the documentation at [https://artist.cispa.saarland](https://artist.cispa.saarland) might be slightly out of sync. We apologize for the inconvenience and happily take feedback at [Gitter](https://gitter.im/project-artist/Lobby). To keep up with the current progress, keep an eye on the beta milestones of the Project: ARTist repositories and check for new blog posts at [https://artist.cispa.saarland](https://artist.cispa.saarland) . 

## Contribution

We hope to create an active community of developers, researchers and users around Project ARTist and hence are happy about contributions and feedback of any kind. There are plenty of ways to get involved and help the project, such as testing and writing Modules, providing feedback on which functionality is key or missing, reporting bugs and other issues, or in general talk about your experiences. The team is actively monitoring [Gitter](https://gitter.im/project-artist/) and of course the repositories, and we are happy to get in touch and discuss. We do not have a full-fledged contribution guide, yet, but it will follow soon (see beta announcement above). 

## Academia

ARTist is based on a paper called **ARTist - The Android Runtime Instrumentation and Security Toolkit**, published at the 2nd IEEE European Symposium on Security and Privacy (EuroS&P'17). The full paper is available [here](https://artist.cispa.saarland/res/papers/ARTist.pdf). If you are citing ARTist in your research, please use the following bibliography entry:

```
@inproceedings{artist,
  title={ARTist: The Android runtime instrumentation and security toolkit},
  author={Backes, Michael and Bugiel, Sven and Schranz, Oliver and von Styp-Rekowsky, Philipp and Weisgerber, Sebastian},
  booktitle={2017 IEEE European Symposium on Security and Privacy (EuroS\&P)},
  pages={481--495},
  year={2017},
  organization={IEEE}
}
```

There is a follow-up paper where we utilized ARTist to cut out advertisement libraries from third-party applications, move the library to a dedicated app (own security principal) and reconnect both using a custom Binder IPC protocol, all while preserving visual fidelity by displaying the remote advertisements as floating views on top of the now ad-cleaned application. The full paper **The ART of App Compartmentalization: Compiler-based Library Privilege Separation on Stock Android**, as it was published at the 2017 ACM SIGSAC Conference on Computer and Communications Security (CCS'17), is available [here](https://artist.cispa.saarland/res/papers/CompARTist.pdf).
