# ---------------------------------------- #
# DBVG Coreutils Library                   #
# Written and tested with Python 3.10.8    #
# Originally for use with SearTxT & Texter #
# ---------------------------------------- #

import os
from math import ceil
from random import randint
from datetime import datetime
from traceback import format_exc

# -------------------------- #
# GLOBAL CONSTANTS & CLASSES #
# -------------------------- #

SEPARATOR = '<@v@>'
ARG_SEPARATOR = '='
PATH_SEPARATOR = os.path.sep

class Colors:
    """Base class for terminal colors."""
    RESET = '\033[0m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    CYAN = '\033[1;36m'

class Tips:
    """Custom class for frequently used tips."""
    # Textual tips
    ERROR = f"{Colors.RED}[ERROR]{Colors.RESET}"
    WARNING = f"{Colors.RED}[WARNING]{Colors.RESET}"

    # Symbolic tips
    SUCCESS = f"{Colors.GREEN}##{Colors.RESET}"
    SKIPPED = f"{Colors.BLUE}%%{Colors.RESET}"
    UNSURE1 = f"{Colors.YELLOW}@@{Colors.RESET}"
    UNSURE2 = f"{Colors.YELLOW}||{Colors.RESET}"
    FINISH = f"{Colors.CYAN}$${Colors.RESET}"
    FAIL1 = f"{Colors.RED}XX{Colors.RESET}"
    FAIL2 = f"{Colors.RED}||{Colors.RESET}"

# ----------------------- #
# MISCELLANEOUS FUNCTIONS #
# ----------------------- #

def write_settings(settings_path, arguments, arg_separator=ARG_SEPARATOR):
    """
    Write configuration arguments to a specified settings file.

    Keyword arguments:
    * settings_path (str)  --  the path to the settings file 
    * arguments (dict)     --  the dict of configurations to write
    * arg_separator (str)  --  keyword/parameter separator
                               (default: '=')

    Example:
    * arguments = {'target_dir' : '/home/DBVG/Documents/SearTxT'}
    * arg_separator = '='
    """
    if os.path.exists(settings_path):
        old_settings = f"{settings_path}.old"
        os.replace(settings_path, old_settings)

    with open(settings_path, 'w', encoding='utf8') as file:
        for keyword in arguments:
            parameter = arguments.get(keyword)
            file.write(f"{keyword} {arg_separator} {parameter}\n")
            # the spaces around arg_separator are necessary for read_settings()


def read_settings(settings_path, arguments, no_copy=False):
    """
    Look for the specified keywords & parameters in a settings file.

    Keyword arguments:
    * settings_path (str) --  the path to the settings file
    * arguments (dict)    --  the dict of keywords to search for
                              (refer to write_settings() docstring)
    * no_copy (bool)      --  whether or not to modify arguments directly
    
    Return value:
    * settings_results (dict)  --  the processed dict of keywords & associated parameters
    """
    if not no_copy:
        settings_results = arguments.copy()
    else:
        settings_results = arguments
    with open(settings_path, 'r', encoding='utf8') as file:
        for line in file:
            line_split = tuple(line.strip().split())
            if not line_split:
                continue

            keyword = line_split[0]
            if not keyword or len(line_split) < 3:
                continue
            if keyword not in settings_results:
                continue

            arg_separator = line_split[1]
            cutoff = f"{keyword} {arg_separator} "
            parameter = line[len(cutoff):]
            settings_results[keyword] = parameter.strip()
    return settings_results


def refresh_display(program, version, script_dir, notification='', method=''):
    """
    Clear the display and print out some essential information.

    Keyword arguments:
    (all str)
    * program       --  the program name (duh)
    * version       --  the current program version (also float)
    * script_dir    --  the script/binary actual directory
    * notification  --  any notice to the user
    * method        --  the current search method (SearTxT)
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(f"{Colors.CYAN}***** DBVG {program} ver {version} *****{Colors.RESET}")
    print(f"Script directory: {Colors.CYAN}{script_dir}{Colors.RESET}")

    if method == 'exact_match':
        print(f"Search method: {Colors.CYAN}exact match{Colors.RESET}")
    elif method:
        print(f"Search method: {Colors.CYAN}approximate match{Colors.RESET}")

    if notification:
        print(notification)
    else:
        print()


def get_confirmation(choice):
    """
    Validate the user's answser to y/n questions.

    Keyword argument:
    * choice (str)  --  the user's answer

    Return values:
    * True       --  if the answer is 'y' or 'yes'
    * False      --  if the answer is 'n' or 'no'
    * 'invalid'  --  any other value
    """
    if choice in ('y', 'yes'):
        return True
    if choice in ('n', 'no'):
        return False
    return 'invalid'


def bash_prompt_dir(target_path, home_path):
    """
    Create Bash-like prompt directory.

    Ex: /home/DBVG/SearTxT/example
    ->  ~/example

    Keyword arguments:
    (all str)
    * target_path  --  the full path
    * home_path    --  the path to be abbreviated (e.g. home directory)

    Return values:
    * bash_path (str) -- the shortened path
    """
    if home_path in target_path and home_path != target_path:
        tail_dir = target_path[len(home_path):]
        bash_path = f"~{tail_dir}"
    elif home_path == target_path:
        bash_path = '~'
    else:
        bash_path = target_path

    return bash_path

# ----------------------------- #
# MULTI-THREADING RELATED STUFF #
# ----------------------------- #

class ZeroThreadError(Exception):
    """Custom exception for the misallocation of zero cpu threads."""
    def __init__(self, message="The number of allocated processors must be greater than 0"):
        self.message = message
        super().__init__(self.message)

class TooManyThreadError(Exception):
    """Custom exception for the misallocation of too many cpu threads."""
    def __init__(self, message="The number of allocated processors exceeded that of the system"):
        self.message = message
        super().__init__(self.message)

class ThreadAllocatorArgumentError(Exception):
    """Custom exception for any undefined thread_allocator() arguments."""
    def __init__(self, message="thread_allocator() received an invalid argument"):
        self.message = message
        super().__init__(self.message)

def thread_allocator(user_threads, total_cpu):
    """
    Validate the user's specified number of cpu processes.

    Keyword arguments:
    * user_threads (int/str)  --  the user's given number of cpu threads
    * total_cpu (int)         --  the system's total number of cpus

    Valid inputs:
    * 0 < user_threads <= total_cpu
    * user_threads in: ('-h', '--half')
                       ('-q', '--quarter')
                       ('-a', '--all')

    Return values:
    * ZeroThreadError               --  if user_threads <= 0
    * TooManyThreadError            --  if user_threads > total_cpu
    * ThreadAllocatorArgumentError  --  if user_threads is an unknown arg
    * int(user_threads)             --  if user_threads is valid
    """
    try:
        if int(user_threads) > total_cpu:
            raise TooManyThreadError
        if int(user_threads) <= 0:
            raise ZeroThreadError
    except ValueError:
        VALID_ARGS = ('-h', '--half', '-q', '--quarter', '-a', '--all', '')
        if user_threads not in VALID_ARGS:
            raise ThreadAllocatorArgumentError
        # Ceil ensures that at least 1 cpu thread will always be allocated
        if user_threads in VALID_ARGS[0:1]:
            user_threads = ceil(total_cpu / 2)
        elif user_threads in VALID_ARGS[2:3]:
            user_threads = ceil(total_cpu / 4)
        elif user_threads in VALID_ARGS[4:6]:
            user_threads = total_cpu
    return int(user_threads)

# ---------------------------- #
# PATH TRAVERSAL RELATED STUFF #
# ---------------------------- #

class PathSeparatorError(Exception):
    """Custom exception for mismatching path separators."""
    def __init__(self, message="Invalid path separator found in given path"):
        self.message = message
        super().__init__(self.message)

def change_target(script_dir, user_path, current_target=''):
    """
    Change the current target (working) directory.

    Keyword arguments:
    (all str)
    * script_dir      --  the program's current directory
    * user_path       --  the user's specified directory
    * current_target  --  the current target directory

    Return values:
    * new_target (str)  --  if the processed path is a valid path
    * OSError           --  if the processed path doesn't exist
    * IndexError        --  if traverse_relative_path() fails
    """
    for char in user_path:
        if char in ('/', '\\') and char != PATH_SEPARATOR:
            raise PathSeparatorError

    if user_path in ('.', f'.{PATH_SEPARATOR}'):  # emulate 'cd ./' & 'cd .'
        return current_target
    if not user_path:
        return script_dir

    if user_path.startswith('..'):
        new_target = traverse_relative_path(user_path, current_target)
    elif user_path.startswith('~'):
        new_target = traverse_relative_path(user_path, script_dir)
    else:
        new_target = os.path.join(current_target, user_path)
        # if user_path is an absolute path (e.g. /home/DBVG/Documents)
        # os.path.join() will discard current_target and return user_path

    if os.path.exists(new_target):
        return new_target.strip()
    raise OSError

def traverse_relative_path(relative_path, full_path):
    """
    Translate a relative path into an absolute path based on the current full path.

    Keyword arguments:
    (all str)
    * relative_path  --  the relative path to be processed
    * full_path      --  the absolute path used to process the relative path

    Return values:
    * new_path    --  the newly processed absolute path
    * IndexError  --  if the given relative path is an invalid one
    * OSError     --  if validate_os_path() fails
    """
    relative_path = relative_path.split(PATH_SEPARATOR)
    full_path =  full_path.split(PATH_SEPARATOR)

    if relative_path[0] == '~':
        relative_path.pop(0)
    if not full_path[0]:
        full_path.pop(0)  # Get rid of '' at the beginning

    # Process the relative path
    for dir_name in relative_path:
        if dir_name == '.':
            continue
        if dir_name == '..':
            if not full_path:
                raise IndexError
            full_path.pop()
        elif dir_name not in ('~', '..', ''):
            validate_os_path(dir_name)
            full_path.append(dir_name)

    new_path = ''
    for dir_name in full_path:
        # Ensures compatibility across UNIX and Windows systems
        new_path = os.path.join(PATH_SEPARATOR, new_path + PATH_SEPARATOR, dir_name)
    return new_path

def validate_os_path(file_name):
    """
    Check the validity of a given path.

    Keyword argument:
    * file_name (str)  --  the path to be validated

    Supported platforms:
    * 'nt': illegal file names/characters & no '...(n)'

    Return values:
    * OSError  --  if the given path is invalid
    * Nothing  --  if the given path is valid
    """
    if os.name == 'nt':
        win_illegal_chars = tuple(r'<>:"/\|?*')
        win_illegal_names = (
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        )
        if file_name in win_illegal_names:
            raise OSError
        if file_name.endswith('.') or file_name.endswith(' '):
            raise OSError
        only_periods = True
        for char in file_name:
            if char in win_illegal_chars:
                raise OSError
            # On Windows 10 & 11, os.path.exists('C:\\foo\\bar\\...(n)') yields a valid path
            # but accessing it will crash the program with the following exception:
            # 'FileNotFoundError: [WinError 3]'
            if char != '.' and only_periods:
                only_periods = False
        if only_periods:
            raise OSError

# ------------------------------ #
# LIST_DIRECTORY() RELATED STUFF #
# ------------------------------ #

class ListNumError(Exception):
    """Custom exception for zero or negative ls_num."""
    def __init__(self, message="/ls (column) must be greater than 0"):
        self.message = message
        super().__init__(self.message)

class ListDirError(Exception):
    """Custom exception for invalid ls_dir."""
    def __init__(self, message="Invalid parameter for /ls (dir)"):
        self.message = message
        super().__init__(self.message)

def validate_ls_args(args, columns):
    """
    Validate the arguments used for list_directory().

    Keyword arguments:
    * args (str)     --  the user's given arguments for list_directory()
    * columns (int)  --  the previously used number for ls (column)

    Valid inputs:
    * args[ls_num] > 0
    * args[ls_dir] in: ('')
                       ('-t', '--target')
                       ('-s', '--script')

    Return values:
    * ListDirError  --  if ls_dir is invalid
    * ListNumError  --  if ls_num <= 0
    * columns (int), ls_dir (str)
    """
    ls_num = 0
    ls_dir = '-t'

    # Argument parser - could probably be improved
    for arg in args:
        try:
            ls_num = int(arg)
        except ValueError:
            ls_dir = arg

    if ls_dir not in ('', '-t', '--target', '-s', '--script'):
        raise ListDirError

    if ls_num:
        if ls_num <= 0:
            raise ListNumError
        columns = ls_num
    elif not ls_num and not columns:
        columns = 2

    return columns, ls_dir

def column_sort_lsdir(lsdir_contents, columns_num):
    """
    An extracted snippet of list_directory() for sorting lsdir contents.

    Keyword arguments:
    * lsdir_contents (str)  --  the contents of the working directory
    * columns_num (int)     --  the number of display columns

    Return values:
    (all tuple)
    * multiple_rows   --  the sorted but unprocessed list of lsdir contents
    * columns_widths  --  the maximum widths of different display columns

    Visualization:
    * multiple_rows = (
    |   '<@v@>.hidden_file<@v@>.hidden_too<@v@>.hidden_xxx',
    |   '<@v@>big_file<@v@>file1<@v@>file2',
    |   '<@v@>file3<@v@>long_file<@v@>secret_file'
    | )
    * columns_widths = (12, 11, 11)
    """
    columns_widths = [0] * columns_num
    column_index = 0
    single_row = ''
    multiple_rows = []

    for ls_index, ls_entry in enumerate(lsdir_contents):
        if len(ls_entry) > columns_widths[column_index]:
            columns_widths[column_index] = len(ls_entry)
        single_row = SEPARATOR.join((single_row, f"{ls_entry}"))
        column_index += 1

        if column_index == columns_num or ls_index == len(lsdir_contents) - 1:
            multiple_rows.append(single_row)
            column_index = 0
            single_row = ''

    return tuple(multiple_rows), tuple(columns_widths)

def list_directory(path, columns=2, file_colors='', unsupported_types=''):
    """
    A poor recreation of the UNIX 'ls' command.

    Keyword arguments:
    * path (str)                --  the working directory path
    * columns (int)             --  the number of diplay columns
    * file_colors (dict)        --  color codes for associated file types
    * unsupported_types (iter)  --  a collection of unsupported files

    Visualization:
    * columns = 3
    | .hidden_file  .hidden_too  .hidden_xxx
    | big_file      file1        file2
    | file3         long_file    secret_file
    """    
    ls_entries = os.listdir(path)
    ls_entries.sort(key=str.lower)

    # First separate the sorted entries into different columns
    multiple_rows, max_lens = column_sort_lsdir(ls_entries, columns)

    column_index = 0
    output_string = ''
    # Append additional spaces to the entries depending on their column position
    # Print the entire row once all columns are appended
    for ls_entry in multiple_rows:
        single_row = list(filter(None, ls_entry.split(SEPARATOR)))
        for index, item in enumerate(single_row):
            spaces = ' ' * (max_lens[column_index] - len(item))
            terminus = ' ' * 2
            entry_sep = f"{spaces}{terminus}"
            file_type = os.path.splitext(item)[1]

            if column_index < columns:
                if file_colors and file_type in file_colors:
                    output_string += f"{file_colors.get(file_type)}{item}{Colors.RESET}{entry_sep}"
                elif unsupported_types and file_type in unsupported_types:
                    output_string += f"{Colors.YELLOW}{item}{Colors.RESET}{entry_sep}"
                elif os.path.isdir(os.path.join(path, item)):
                    output_string += f"{Colors.CYAN}{item}{Colors.RESET}{entry_sep}"
                else:
                    output_string += f"{item}{entry_sep}"
            column_index += 1

            if column_index == columns or index == len(single_row) - 1:
                print(output_string.strip())
                column_index = 0
                output_string = ''
    print()

# -------------------------- #
# TRACEBACK CRASH LOGGER >~< #
# -------------------------- #

def write_crashlog(config_dir, program, error):
    """
    Write the traceback exception to a crash log in the config folder.

    Keyword arguments:
    * config_dir (str)   --  the directory where configuration files are stored
    * program (str)      --  the program name (duh)
    * error (exception)  --  the traceback exception
    """
    ran_num = randint(0, 4)
    chances = (1, 3)
    if ran_num in chances:
        crash_messages = (
            r"Oops, sorry mate :(",
            r"I'll try better next time :'(",
            r"Let's have a ~~HUG~~ >.<",
            r"At least your computer didn't blow up right ;)",
            r"Sussy imposter detected in the script >:(",
            r"ごめなさい >~<",
            r"私のコードはちょっと変だね T-T",
            r"何も分からない ¯\_(ツ)_/¯",
            r"今寝る -.- zzZ",
        )
        surprise_message = crash_messages[randint(0, len(crash_messages) - 1)]

    session = f"### {program.upper()} SESSION: {datetime.now()} {'#' * 40}\n"
    dash_border = '-' * len(session) + '\n'

    logging_dir = os.path.join(config_dir, f"{program.lower()}_log.txt")
    with open(logging_dir, 'a', encoding='utf8') as log:
        log.write(session)
        log.write(dash_border)
        log.write(f"{format_exc()}")
        if ran_num in chances:
            log.write(f"\n{surprise_message}")
        log.write(f"\n{dash_border}\n\n")

    print('\n------------------------------------------')
    print(f"{Tips.ERROR} Program terminated by script error")
    print(f"{Tips.ERROR} {error}")
    print(f"{Tips.ERROR} Please inspect {program.lower()}_log.txt in the config folder for more information\n")
