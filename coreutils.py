# ---------------------------------------- #
# DBVG Coreutils Library                   #
# Written and tested with Python 3.10.8    #
# Originally for use with SearTxT & Texter #
# ---------------------------------------- #

import os
from math import ceil
from datetime import datetime
from traceback import format_exc

# GLOBAL CONSTANTS
SEPARATOR = '<@v@>'

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


def write_settings(settings_directory, arguments):
    """
    Write configuration arguments to a specified settings file.

    Keyword arguments:
    * settings_directory (str)  --  the path to the settings file 
    * arguments (list)          --  the list of arguments to write
    """
    if os.path.exists(settings_directory):
        old_settings = f"{settings_directory}.old"
        os.replace(settings_directory, old_settings)

    with open(settings_directory, 'w', encoding='utf8') as file:
        for line in arguments:
            file.write(f"{line}\n")


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
    Validate the user's anwser to y/n questions.

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
    * False              --  any invalid value (also print error message)
    * int(user_threads)  --  if user_threads was successfully verified
    """
    user_threads = user_threads.lstrip('/t').strip()
    try:
        if int(user_threads) > total_cpu:
            print(f"{Tips.ERROR} Cannot allocate more than ({total_cpu}) cpu threads on this system")
            return False
        if int(user_threads) <= 0:
            print(f"{Tips.ERROR} The number of allocated processors must be greater than 0")
            return False
    except ValueError:
        # Ceil ensures that at least 1 cpu thread will always be allocated
        if user_threads in ('-h', '--half'):
            user_threads = ceil(total_cpu / 2)
        elif user_threads in ('-q', '--quarter'):
            user_threads = ceil(total_cpu / 4)
        elif user_threads in ('-a', '--all', ''):
            user_threads = total_cpu
        else:
            print(f"{Tips.ERROR} Invalid option for /t (cpu thread)")
            return False
    return int(user_threads)


# Custom exceptions for the "/cd" function
class PathSeparatorError(Exception):
    def __init__(self, message="Invalid path separator found in given path"):
        self.message = message
        super().__init__(self.message)

PATH_SEPARATOR = os.path.sep

def change_target(script_dir, user_path, path_type, current_target=''):
    """
    Change the current target (working) directory.

    Keyword arguments:
    (all str)
    * script_dir      --  the program's current directory
    * user_path       --  the user's specified directory
    * path_type       --  the type of path given:
                            '/cd' relative path
                            '/ap' absolute path
    * current_target  --  the current target directory

    Return values:
    * new_target (str)  --  if the processed path is a valid path
    * OSError           --  if the processed path doesn't exist
    * IndexError        --  if traverse_relative_path() fails
    """
    user_path = user_path.lstrip(path_type).strip()
    for char in user_path:
        if char in ('/', '\\') and char != PATH_SEPARATOR:
            raise PathSeparatorError

    if path_type == '/cd':
        if user_path in ('.', f'.{PATH_SEPARATOR}'):
            return current_target
        if not user_path:
            return script_dir

        if user_path.startswith('..'):
            new_target = traverse_relative_path(user_path, current_target)
        elif user_path.startswith('~'):
            new_target = traverse_relative_path(user_path, script_dir)
        else:
            new_target = os.path.join(current_target, user_path)
    elif path_type == '/ap':
        new_target = user_path
    
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
        elif dir_name == '..':
            if full_path:
                full_path.pop()
            else:
                raise IndexError
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

    WIN_ILLEGAL_CHARS = list('<>:"/\|?*')
    WIN_ILLEGAL_NAMES = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
    ]

    if os.name == 'nt':
        if file_name in WIN_ILLEGAL_NAMES:
            raise OSError
        if file_name.endswith('.') or file_name.endswith(''):
            raise OSError
        only_periods = True
        for char in file_name:
            if char in WIN_ILLEGAL_CHARS:
                raise OSError
            # On Windows 10 & 11, os.path.exists('C:\\foo\\bar\\...(n)') yields a valid path
            # but accessing it will crash the program with the following exception:
            # 'FileNotFoundError: [WinError 3]'
            if char != '.' and only_periods:
                only_periods = False
        if only_periods:
            raise OSError


# Custom exceptions for the "/ls" function
class ListNumError(Exception):
    def __init__(self, message="/ls (column) must be greater than 0"):
        self.message = message
        super().__init__(self.message)

class ListDirError(Exception):
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
    args = args.lstrip('/ls').strip().split()
    ls_num = 0
    ls_dir = '-t'

    # Argument parser - could probably be improved
    for arg in args:
        try:
            if isinstance(int(arg), int):
                ls_num = arg
        except ValueError:
            ls_dir = arg

    if ls_dir not in ('', '-t', '--target', '-s', '--script'):
        raise ListDirError

    if ls_num:
        if int(ls_num) <= 0:
            raise ListNumError
        columns = int(ls_num)
    elif not ls_num and not columns:
        columns = 2
    
    return columns, ls_dir


def write_crashlog(config_dir, program, error):
    """
    Write the traceback exception to a crash log in the config folder.

    Keyword arguments:
    * config_dir (str)   --  the directory where configuration files are stored
    * program (str)      --  the program name (duh)
    * error (exception)  --  the traceback exception
    """
    LOGGING_DIR = os.path.join(config_dir, f"{program.lower()}_log.txt")
    with open(LOGGING_DIR, 'a', 'utf8') as log:
        log.write(f"### {program.upper()} SESSION: {datetime.now()} {'#' * 40}\n")
        log.write('-' * len(f"### {program.upper()} SESSION: {datetime.now()} {'#' * 40}") + '\n')
        log.write(f"{format_exc()}\n\n")
    print(f"{Tips.ERROR} Program terminated by script error")
    print(f"{Tips.ERROR} {error}")
    print(f"{Tips.ERROR} Please inspect {program.lower()}_log.txt in the config folder for more information\n")
