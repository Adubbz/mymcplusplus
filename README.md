# mymc++

mymc++ is a PlayStation 2 memory card manager for use with .ps2 images created by PCSX2, as well as .mc2 files created by the MemCard PRO2.

It is based on [mymc+](https://git.sr.ht/~thestr4ng3r/mymcplus) by Florian Märkl and the classic [mymc](http://www.csclub.uwaterloo.ca:11068/mymc/) utility created by Ross Ridge.

Changes that have been made from the original code include the following:

* Ported to Python 3 and wxPython Phoenix
* Replaced the natively implemented 3D icon renderer with a cross-platform solution using OpenGL 3.2 Core
* Added support for importing PSV files (as created by the PlayStation 3)
* Added a py.test based test suite
* Many other small refactorings...

Please note that mymc++ is released under the **GPLv3, not Public Domain**!

Here is an overview of most features:

* Read and write the PS2 memory card file system, including extracting and adding files at file system level
* Import save games in MAX Drive (.max), EMS (.psu), SharkPort (.sps), X-Port (.xps), Code Breaker (.cbs) and PSV (.psv) format
* Export save games in MAX Drive (.max) and EMS (.psu) format
* Command line interface
* Optional wxPython based GUI, also displaying the 3D icons

![Screenshot](screenshot.png)

## Installation

mymc++ is available on [PyPI](https://pypi.org/project/mymcplusplus/).
You can install it, including the GUI, using pip:

```
pip install mymcplusplus[gui]
```

If you only wish to install the command line interface, simply omit the
gui extra:

```
pip install mymcplusplus
```

## Usage

If the GUI component is installed (i.e. wxPython can be found), it can
simply be started using the following command:

```
mymcplusplus
```

### Command Line Interface

The command line interface can be used like this:

```
Usage: /usr/bin/mymcplusplus [-ih] memcard.ps2 command [...]

Manipulate PS2 memory card images.

Supported commands:
   add: Add files to the memory card.
   check: Check for file system errors.
   clear: Clear mode flags on files and directories
   delete: Recursively delete a directory (save file).
   df: Display the amount free space.
   dir: Display save file information.
   export: Export save files from the memory card.
   extract: Extract files from the memory card.
   format: Creates a new memory card image.
   gui: Starts the graphical user interface.
   import: Import save files into the memory card.
   ls: List the contents of a directory.
   mkdir: Make directories.
   remove: Remove files and directories.
   set: Set mode flags on files and directories

Options:
  --version         show program's version number and exit
  -h, --help        show this help message and exit
  -i, --ignore-ecc  Ignore ECC errors while reading.
```

It is always necessary to specify the path to a memory card image
with `-i <path>` first. For example:

```
mymcplus -i empty.ps2 format
```

creates the file `empty.ps2` and formats it as an empty memory card.
