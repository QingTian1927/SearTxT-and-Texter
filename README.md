# SearTxT & Texter

## Table of Contents
1. Introduction
2. Features
3. Installation
4. Quickstart
5. Commands
6. Conversion
7. Building From Source

## Introduction
* **SearTxT** is a simple command-line tool to search for virtually any string of text contained within `.txt` files in a user-specified directory.

* **Texter** is a complementary file converter that can convert `.docx` , `.pdf` as well as several other file formats into `.txt` for use with SearTxT.

These are the improved versions of my original Python Text Searcher, which was unnecessarily bloated, to say the least.

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

**Note:** If the `/pd` command fails for any reason, you can download pandoc directly from the [official website](https://pandoc.org/installing.html) and install it manually.

### Running From Source
Should you want to run SearTxT or Texter directly with the Python Interpreter, make sure that your system satisfies the following prerequisites:  

* Python >= `3.10.8`
* Pip packages (Texter): `pypandoc`, `pdfminer.six`

#### Linux
Simply download Python from your package manager of choice e.g:

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





