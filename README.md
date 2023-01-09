# SearTxT & Texter

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Quickstart](#quickstart)
6. [Conversion](#conversion)
7. Building From Source
8. Known Issues
9. Acknowledgements

## Introduction
These are the improved versions of my original Python Text Searcher, which was unnecessarily bloated, to say the least.

* **SearTxT** is a simple command-line tool to search for virtually any string of text contained within `.txt` files in a user-specified directory.

* **Texter** is a complementary file converter that can convert `.docx` , `.pdf` as well as several other file formats into `.txt` for use with SearTxT.

I wrote these programs just for fun, so don't expect the same level of polish and utility that may come with tools such as `fzf` or `grep`. With that said though, I still hope that you would find SearTxT & Texter to be useful somehow.

## Features
* 8 times the performance improvement :0
* Support for `.docx`, `.pdf`, `.doc`, and many more (See the Conversion section for more details)
* Automate boring, repetitive tasks with AutoScript (Coming soon)
* Much eye candy >.<
* And many more (probably...)

## Installation
Simply download the latest release, extract the content of the `.zip` archive, and launch SearTxT or Texter with the appropriate executable.

### Texter-specific requirements:
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
You can either download Python from the [official website](https://www.python.org/downloads/) or install it with a package manager such as `scoop`:

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

#### Configure the number of cpus used for the multithreaded processes:
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
Since SearTxT can only search for strings in `.txt` files, you will have to run Texter first to convert other file formats (e.g. `.docx`, `.pdf`, `.doc`, etc.) into `.txt`.

#### Download and install pandoc
Simply launch Texter and use the `/pd` command. Alternative, you can also download and install pandoc manually, but make sure you add the installation directory to your `PATH`.

#### Start the conversion
If you have correctly set up and moved your files inside the target directory, simply start the conversion by using the `/cv` command.

**Note (ver `1.0`):** Make sure to **BACKUP** your files as Texter **PERMANENTLY DELETES** the original file formats after the conversion.

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
