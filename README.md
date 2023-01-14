# SearTxT & Texter
These are the improved versions of my original Python Text Searcher, which was unnecessarily bloated, to say the least.

* **SearTxT** is a simple command-line tool to search for virtually any string of text contained within `.txt` files in a user-specified directory.

* **Texter** is a complementary file converter that can convert `.docx` , `.pdf` as well as several other file formats into `.txt` for use with SearTxT.

I wrote these programs mainly to learn the basics of Python (and also for fun), so don't expect the same level of polish and utility that may come with tools such as `fzf` or `grep`. With that said though, I still hope that you would find SearTxT & Texter to be useful somehow.

## Table of Contents
1. [Features](#features)
1. [Installation](#installation)
1. [Usage](#usage)
1. [Quickstart](#quickstart)
1. [Conversion](#conversion)
1. [Building From Source](#building-from-source)
1. Known Issues
1. Acknowledgements

## Features
* 8 times the performance improvement :0
* Support for `.docx`, `.pdf`, `.doc`, and many more (See the Conversion section for more details)
* Automate boring, repetitive tasks with AutoScript (Coming soon)
* Much eye candy >.<
* And many more (probably...)

## Installation
Simply download the latest [release](https://github.com/QingTian1927/SearTxT-and-Texter/releases), extract the content of the `.zip` archive, and launch SearTxT or Texter with the appropriate executable.

### Texter-specific Requirements:
Texter can only convert `.docx` files with the `pandoc` runtime installed, so make sure you download it using the `/pd` command prior to starting the conversion process. 

**Note:** Should the `/pd` command fails for any reason, you can download pandoc directly from the [official website](https://pandoc.org/installing.html) and install it manually.

### Running From Source
Should you want to run SearTxT or Texter directly with the Python Interpreter, make sure that your system satisfies the following prerequisites:  

* Python >= `3.10.8`
* Pip packages (Texter): `pypandoc`, `pdfminer.six`

#### Linux
Simply download Python from your package manager of choice, e.g.:

**APT**
``` shell
sudo apt-get install python
```

**Pacman**
``` shell
sudo pacman -S python
```

#### Windows
You can either download Python from the [official website](https://www.python.org/downloads/) or install it with a package manager such as [scoop](https://scoop.sh/):

``` shell
scoop install python
```

#### Pip
Once you have installed Python and added the installation directory to your `PATH`, download the required packages with:

``` shell
python -m pip install pypandoc pdfminer.six
```

## Usage
```
Usage    : /command <required parameters> [optional parameters]
 or      : <any string of characters>

Examples : /ls
           /ls 4 -s or /ls 4 --script
	   /t -h    or /t --half
```

### General Commands
#### Change the target directory:
```
/ap <absolute path>
``` 
or 
```
/cd <relative path>
``` 
(in relation to the script directory)

#### List the content of a directory:
```
/ls (column: num) (dir: -s / --script ; -t / --target)
``` 
(default: target dir, 3 columns)

#### Configure the number of CPUs used for the multithreaded processes:
```
/t (threads: num ; -a / --all ; -h / --half ; -q / --quarter)
``` 
(default: all threads)

#### Misc:
```
* /c             : clear the display

* /h             : show all available commands

* /q or <CTRL-C> : terminate the program
```

### SearTxT Commands
#### Change the search method:
```
/mt (method: -e / --exact ; -p / --proximity)
``` 
(default: exact match)

### Texter Commands
#### Start the conversion process:
```
/cv
```

#### Download and install pandoc:
```
/pd
```

#### Cat:
```
/cat
```

## Quickstart
### General Guide
SearTxT and Texter are command-line tools, so you will need to type out the exact command of the desired operation. 

#### Configure the target directory
First, start by configuring your `target directory`. This is where SearTxT and Texter will try to search and convert your files respectively.

**Example (Windows file path):**
```
*****DBVG SearTxT ver 1.0*****
Script directory: D:\Downloads\SearTxT 
Search method: exact match

[SearTxT ~example]$ /ap C:\Users\DBVG\Documents\PDF Stuff
<ENTER>
.......
[SearTxT C:\Users\DBVG\Documents\PDF Stuff]$ _
```

**Example (Unix file path):**
```
*****DBVG Texter ver 1.0*****
Script directory: /home/DBVG/SearTxT

[Texter ~example]$ /ap /home/DBVG/Documents/DOCX Stuff
<ENTER>
.......
[Texter /home/DBVG/Documents/DOCX Stuff]$ _
```

To check whether you have entered the correct path, use the `/ls` command to check the content of target directory.

**Note:** The `~` symbol indicates that the current target directory is inside the script directory, hence a relative path.

### Texter Quickstart Guide
Since SearTxT can only search for strings in `.txt` files, you will have to run Texter first to convert other file formats (e.g. `.docx`) into `.txt`.

#### Download and install pandoc
Simply launch Texter and use the `/pd` command. Alternatively, you can also download and install pandoc manually, but make sure you add the installation directory to your `PATH`.

#### Start the conversion
If you have correctly set up and moved your files inside the target directory, simply start the conversion by using the `/cv` command.

**Note:** Make sure to **BACKUP** your files as Texter **PERMANENTLY DELETES** the original file formats after the conversion.

#### Check the results
Simply navigate to the specified target directory and check the newly-converted `.txt` files with your favorite text editor.

### SearTxT Quickstart Guide
This guide assumes that you have already converted your files into `.txt` files.

#### Set the search method
**To search for exact matches of the original query:**
```
/mt -e
```
or
```
/mt --exact
```

**To search for approximate matches of the original query:**
```
/mt -p
```
or
```
/mt --proximity
```

#### Start searching
Simply type in virtually any string of characters and then hit `ENTER`.

**Note:** The search query cannot start with the `/` character, as this is an identifier for commands. If your search query starts with `/`, SearTxT will throw an error message.

#### Check the results
If SearTxT finds any matches, it will print out the results on the screen. Simply use your mouse to scroll through the result list.

## Conversion
As of version `1.0`. Texter officially supports `.docx` and `.pdf` files. However, conversion from `.pdf` to plain text, especially from files with a large number of non-latin characters, can be rather unreliable as it can break the formatting of the original documents.

Unofficially, Texter by default can also *try to* convert the following file formats:
```
-----------------------------------------
.css .sass .html .htm .js .jsm .mjs .json
.markdown .md .mkd .org
.v .asc .log .conf
.doc
.py .py3 .pyi .pyx .py3x .wsgi
.rs .vbs .lua .p .pas .kt .java
.c .C .cs .c++ .cc .cpp .cxx
.lisp .go .hs
-----------------------------------------
```
It accomplishes this by reading these file types in plain text mode, and then copying the entire content to a separate `.txt` file (very ingenious, ikr). If you want additional file formats, simply add them to `unsupported_types.conf`

## Building From Source
If you feel like compiling your own executables, you can theoretically do so with any compatible CPython compilers. Though the official releases were compiled with Nuitka, this section will provides instructions for Nuitka and PyInstaller.

### With Nuitka
#### Prerequisites
* Nuitka >= `1.3.6`
* Python >= `3.10`
* Pip packages (Nuitka): `ordered-set`, `zstandard`
* Pip packages (Texter): `pypandoc`, `pdfminer.six`

**Windows:**
* MSVC v143 - VS2022 C++ x64/x86 build tools (Latest)
* Windows 11 SDK
* Windows Universal C Runtime
* C++ Build Tools core features

**Note:** Python must **not** be installed from the Windows app store.

**(Arch) Linux:**
* `gcc`
* `patchelf`
* `ccache`

Please refer to the [Nuitka User Manual](https://nuitka.net/doc/user-manual.html) for more information.

#### Instructions
**Clone the repository**

Simply download the latest `source.zip` and extract the contents. Alternatively, if you have `git` installed, use the following command:
``` shell
git clone https://github.com/QingTian1927/SearTxT-and-Texter
```

**Install Nuitka**
``` shell
python -m pip install nuitka
```

**Building SearTxT**

Open the extracted `source` directory in the command-line and run:
``` shell
python -m nuitka --standalone --onefile --remove-output --product-name=SearTxT --file-version=<version> <file_name>
```

**Example:**
``` shell
python -m nuitka --standalone --onefile --remove-output --product-name=SearTxT --file-version=1.0 SearTxT.py
```

If you have correctly configured everything, Nuitka should produce an executable within the same directory (`SearTxT.exe` on Windows, `SearTxT.bin` on Linux)

**Note:** Some anti-virus programs (e.g. BitDefender) may falsely flag the newly-produced `.exe` as a virus and then remove it. To avoid this, you can either add the source directory as an exception, or completely disable the anti-virus program (not recommended)
