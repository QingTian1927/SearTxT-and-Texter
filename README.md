# SearTxT & Texter
These are the improved versions of my original Python Text Searcher, which was unnecessarily bloated, to say the least.

* **SearTxT** is a simple command-line tool to search for virtually any string of text contained within `.txt` files in a user-specified directory.

* **Texter** is a complementary file converter that can convert `.docx`, `.pdf` as well as several other file formats into `.txt` for use with SearTxT.

I wrote these programs mainly to learn the basics of Python (and also for fun), so don't expect the same level of polish and utility that may come with tools such as `fzf` or `grep`. With that said though, I still hope that you would find SearTxT & Texter to be useful somehow.

## With Special Thanks To
These wonderful people have provided invaluable help and support in the creation of SearTxT & Texter:

* **Master Harry Dreamer:** testing & bug reporting
* **Master Eltidee:** testing
* **OBP Corp:** listening to my perpetual ramblings about the benefits of Free and Open Source Software

## Table of Contents
1. [Features](#features)
1. [Installation](#installation)
1. [Usage](#usage)
1. [Quickstart](#quickstart)
1. [Conversion](#conversion)
1. [Building From Source](#building-from-source)
1. [Differences Between the Branches](#differences-between-the-branches)
1. [Known Issues](#known-issues)

## Features
* 8 times the performance improvement :0
* Support for `.docx`, `.pdf`, `.doc`, and many more (See the Conversion section for more details)
* Automate boring, repetitive tasks with AutoScript (Coming soon)
* Much eye candy >.<
* And many more (probably...)

## Installation
Simply download the latest [release](https://github.com/QingTian1927/SearTxT-and-Texter/releases), extract the content of the `.zip` archive, and launch SearTxT or Texter with the appropriate executable.

**Note:** Some anti-virus programs may falsely flag the executable as a virus and then quarantine it. To avoid this, you can either add the SearTxT directory as an exception, or completely disable the anti-virus software (not recommended)

### Texter-specific Requirements:
Texter can only convert `.docx` files with the `pandoc` runtime installed, so make sure you download it using the `/pd` command before starting the conversion process. 

**Note:** Should the `/pd` command fails for any reason, you can download pandoc directly from the [official website](https://pandoc.org/installing.html) and install it manually.

### Running From Source
If you want to run SearTxT or Texter directly with the Python Interpreter, make sure that your system satisfies the following requirements:  

* Python >= `3.10.8`
* Pip packages (Texter): `pypandoc`, `pdfminer.six`

#### Linux
Simply download Python from your package manager of choice, e.g.:

**APT**
``` shell
sudo apt install python-is-python3
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

You may also have to upgrade pip first:
``` shell
python -m pip install --upgrade pip
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
/cd <relative path>  # (in relation to the script directory)

/cd ~ or just /cd    # To quickly change to the script folder

/cd ..               # To go up a directory

/cd ../../..         # To go up a number of directories
    ..\..\..         (Windows)

/cd ../example       # To go up a number of directories and enter the specified directory
    ..\example       (Windows)
```

#### List the content of a directory:
```
/ls (column: num > 0) (dir: -s / --script ; -t / --target)
``` 
(default: target dir, 3 columns)

#### Configure the number of CPUs used for the multi-threaded processes:
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

#### Change the minimum confidence score for approximate matches:
```
/s (score: 0 < float < 1)
```
(default: 0.85)

### Texter Commands
#### Start the conversion process:
```
/cv (output: -v / --verbose ; -b / --brief)
```
(default: brief final output)

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

To check whether you have entered the correct path, use the `/ls` command to check the content of the target directory.

**Note:** The `~` symbol indicates that the current target directory is inside the script directory, hence a relative path.

### Texter Quickstart Guide
Since SearTxT can only search for strings in `.txt` files, you will have to run Texter first to convert other file formats (e.g. `.docx`) into `.txt`.

#### Download and install pandoc
Simply launch Texter and run the `/pd` command. Alternatively, you can also download and install pandoc manually, but make sure you add the installation directory to your `PATH`.

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

**Note:** The search query cannot start with the `/` character. If your search query starts with `/`, SearTxT will throw an error message.

#### Check the results
If SearTxT finds any matches, it will print out the results on the screen. Simply use your mouse to scroll through the result list.

## Conversion
As of version `1.0`. Texter officially supports `.docx` and `.pdf` files. However, conversion from `.pdf` to plain text, especially from files with a large number of non-Latin characters, can be rather unreliable as it can break the formatting of the original documents.

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
It accomplishes this by reading these files in plain text mode, and then copying the entire content to a separate `.txt` file (very *ingenious*, ikr). If you want additional file formats, simply add them to `unsupported_types.conf`

## Building From Source
If you feel like compiling your own executables, you can theoretically do so with any compatible CPython compilers. Though the official releases were compiled with Nuitka, this section will provide instructions for Nuitka and PyInstaller.

**Note:** I don't recommend building SearTxT or running the SearTxT binary on a Linux system due to potential memory leaks and just being very buggy in general.

### With Nuitka
#### Prerequisites
* Nuitka >= `1.3.6`
* Python >= `3.10`
* Pip packages (Nuitka): `ordered-set`, `zstandard`
* Pip packages (Texter): `pypandoc`, `pdfminer.six`

**Windows:**
* MSVC v143 - VS2022 C++ x64/x86 build tools (Latest)
* Windows 11 SDK

**Note:** Python must **NOT** be installed from the Windows app store.

**(Arch) Linux:**
* `gcc`
* `patchelf`
* `ccache`

Please refer to the [Nuitka User Manual](https://nuitka.net/doc/user-manual.html) for more information.

#### Instructions
**Clone the repository**

Simply download the latest `Source code` archive and extract the contents. Alternatively, if you have `git` installed, use the following command:
``` shell
git clone https://github.com/QingTian1927/SearTxT-and-Texter
```

**Install Nuitka**
``` shell
python -m pip install nuitka
```

**Building SearTxT**

Open the extracted `Source code` directory in the command line and run:
``` shell
python -m nuitka --standalone --onefile --remove-output --windows-icon-from-ico=<icon_path> <source_file>
```

**Example (Windows):**
``` shell
python -m nuitka --standalone --onefile --remove-output --windows-icon-from-ico=assets/floppy.ico .\SearTxT.py
```

If you have correctly configured everything, Nuitka should produce an executable within the same directory (`SearTxT.exe` on Windows, `SearTxT.bin` on Linux)

## Differences Between the Branches
### Mix-threaded 
In this branch, the `exact searcher` is single-threaded, whereas the `approximate searcher` is multi-threaded.

During my testing, I noticed that the exact searcher performs significantly better single-threaded than multi-threaded when the search database is relatively small (~ `0.01807s` vs. `0.02647s`). 

However, this doesn't scale well at all with large databases, and using the exact searcher becomes rather tedious when it has to go through hundreds of files at once (took roughly 2s to return 220 results from a set of 81 files)

### Single-threaded
In this branch, both the `exact searcher` and the `approximate searcher` are single-threaded.

This helps to reduce the size of the executable as well as the amount of memory that is used. However, the searchers perform *very* poorly and the searching process becomes *very* tedious.

I don't really recommend using this branch for production purposes as it is maintained with minimal effort.

## Known Issues
### Repeating arguments
When there are several parameters for an argument, commands that accept multiple arguments (e.g. `/ls`) will only use the latest parameter in the series:
```
[SearTxT ~example]$ /ls 2 3 -s -a
file1.txt  file2.txt  file3.txt
file4.txt  file5.txt  file6.txt
file7.txt  ...        ...
```
Discovered by Master Harry Dreamer

**Solution:** just don't repeat the same arguments. I won't fix this issue in the foreseeable future because I simply don't think it is enough of a problem yet. I may *eventually* fix it though.

### False positives
Some anti-virus providers may falsely flag the SearTxT & Texter executables as viruses and then quarantine them.

**Solution:** add an exception to the anti-virus program or disable it completely (not recommended)
