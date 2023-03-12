# ------------------------------------- #
# DBVG SearTxT                          #
# Still very much bloated though.       #
# Written and tested with Python 3.10.8 #
# ------------------------------------- #

# native modules
import os
import sys

from time import perf_counter
from difflib import SequenceMatcher
from difflib import get_close_matches

from multiprocessing import Pool
from multiprocessing import freeze_support
from multiprocessing import set_start_method

# ----------------------- #
# COREUTILS CUSTOM MODULE #
# ----------------------- #

# Shared constants & classes
from coreutils import Tips
from coreutils import Colors
from coreutils import SEPARATOR

# Miscellaneous functions
from coreutils import refresh_display
from coreutils import get_confirmation

# Program configuration
from coreutils import read_settings
from coreutils import write_settings
from coreutils import write_crashlog

# Processors allocation
from coreutils import ZeroThreadError
from coreutils import thread_allocator
from coreutils import TooManyThreadError
from coreutils import ThreadAllocatorArgumentError

# Path traversal & manipulation
from coreutils import change_target
from coreutils import bash_prompt_dir
from coreutils import PathSeparatorError

# Directory listing
from coreutils import ListNumError
from coreutils import ListDirError
from coreutils import list_directory
from coreutils import validate_ls_args

# ---------------- #
# GLOBAL CONSTANTS #
# ---------------- #

VERSION = 1.0
PROGRAM = 'SearTxT'

COMMANDS = (
    'Usage: /command <required parameters> [optional parameters]',
    '  or:  <search query>\n',
    '/cd [path]          : change the search directory to another directory',
    '/ls [column] [dir]  : list all items in the specified directory',
    '/mt [method]        : search for approximate or exact matches',
    '/c                  : refresh the display',
    '/h                  : print out all available commands',
    '/q                  : exit the program',
    '/s [score]          : set the minimum score of the approximate searcher results',
    '/t [thread]         : allocate a number of cpu threads to the searching process\n'
)

# -------------------------- #
# SEARTXT-SPECIFIC FUNCTIONS #
# -------------------------- #

def exact_search(args):
    args = tuple(args.split(SEPARATOR))
    found = 0
    search_output = ''

    file_name = args[0]
    query = args[1]
    search_dir = args[2]

    if not file_name.endswith('.txt'):
        return search_output, found

    file_dir = os.path.join(search_dir, file_name)
    with open(file_dir, 'r', encoding='utf8') as searched_file:
        for index, line in enumerate(searched_file, start=1):
            if query.lower() not in line.lower():
                continue
            search_output = ''.join((search_output, f"{Tips.SUCCESS} 1 match at {Colors.BLUE}Line({index}){Colors.RESET} of {Colors.BLUE}{file_name}{Colors.RESET}\n"))
            search_output = ''.join((search_output, f"{Colors.GREEN}||{Colors.RESET} {line.strip()}\n"))
            found += 1
    return search_output, found 


def approximate_search(args):
    args = tuple(args.split(SEPARATOR))
    found = 0
    search_output = ''

    file_name = args[0]
    query = args[1]
    search_dir = args[2]
    close_match_cutoff = float(args[3])

    if not file_name.endswith('.txt'):
        return search_output, found

    file_dir = os.path.join(search_dir, file_name)
    result_num = 1
    with open(file_dir, 'r', encoding='utf8') as searched_file:
        for index, line in enumerate(searched_file, start=1):
            match = get_close_matches(query.lower(), line.lower().split(), result_num, close_match_cutoff)
            if not match:
                continue
            score = SequenceMatcher(None, query, match[0]).ratio()
            search_output = ''.join((search_output, f"{Tips.UNSURE1} 1 potential match at {Colors.BLUE}Line({index}){Colors.RESET} of {Colors.BLUE}{file_name}{Colors.RESET}\n"))
            search_output = ''.join((search_output, f"{Tips.UNSURE2} {line.strip()}\n"))
            search_output = ''.join((search_output, f"{Tips.UNSURE2} confidence: {Colors.YELLOW}{score:.5f}{Colors.RESET}\n"))
            found += 1
    return search_output, found


# ------------------------------- #
# INTERACTIVE SESSION ENTRY POINT #
# ------------------------------- #

if __name__ == '__main__':
    freeze_support()           # Required for binary compilation
    set_start_method('spawn')  # Ensure compatibility with Windows (and macOS)

    # Initialize script directory
    if getattr(sys, 'frozen', False):
        SCRIPT_DIR = os.path.dirname(sys.executable)
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # ------------------------------------ #
    # INTERACTIVE SESSION GLOBAL VARIABLES #
    # ------------------------------------ #

    notifications = ''
    saved_columns = 0
    approx_score = 0.85

    SYSTEM_CPUS = os.cpu_count()
    allocated_threads = SYSTEM_CPUS

    CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
    SETTINGS_DIR = os.path.join(CONFIG_DIR, f"{PROGRAM.lower()}.conf")
    DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')

    # Program configurations
    TARGET_DIR_KEYWORD = 'target_dir'
    METHOD_KEYWORD = 'method'
    SEARCH_METHODS = ('exact_match', 'proximity_match')
    DEFAULT_SETTINGS_ARGS = {TARGET_DIR_KEYWORD : DEFAULT_TARGET_DIR, METHOD_KEYWORD : SEARCH_METHODS[0]}

    # ------------------------- #
    # INITIALIZE CONFIGURATIONS #
    # ------------------------- #

    # Read config file. Generate the default config and create the config directory in case of errors
    try:
        program_settings = read_settings(SETTINGS_DIR, DEFAULT_SETTINGS_ARGS)
        target_dir = program_settings[TARGET_DIR_KEYWORD]
        search_method = program_settings[METHOD_KEYWORD]

        if not os.path.exists(target_dir) or search_method not in SEARCH_METHODS:
            notifications = f"> {PROGRAM.lower()}.conf contained invalid configuration. Generated a default template\n"
    except FileNotFoundError:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        notifications = f"> {PROGRAM.lower()}.conf couldn't be found. Generated a default template\n"

    if notifications:
        target_dir = DEFAULT_TARGET_DIR
        program_settings = DEFAULT_SETTINGS_ARGS
        if not os.path.exists(DEFAULT_TARGET_DIR):
            os.makedirs(DEFAULT_TARGET_DIR)
        write_settings(SETTINGS_DIR, DEFAULT_SETTINGS_ARGS)

    # -------------------------- #
    # SEARCHER RELATED FUNCTIONS #
    # -------------------------- #

    def parse_search_results(imap_results, results):
        for output, found in imap_results:
            if not output or not found:
                continue
            print(f"{output.strip()}")
            results += found
        return results


    def exact_pool(arguments, workers):
        results = 0
        with Pool(workers) as pool:
            results = parse_search_results(pool.imap_unordered(exact_search, arguments), results)
        return results


    def approx_pool(arguments, score, workers):
        results = 0
        with Pool(workers) as pool:
            results = parse_search_results(pool.imap_unordered(approximate_search, arguments), results)
        return results


    def searchers_wrapper(search_dir, method, query, score, threads):
        arguments = []
        start_time = perf_counter()
        
        if method == 'exact_match':
            for file in os.listdir(search_dir):
                arguments.append(f"{file}{SEPARATOR}{query}{SEPARATOR}{search_dir}")
            arguments = tuple(arguments)
            results = exact_pool(arguments, threads)
            end_time = perf_counter()
        elif method == 'proximity_match':
            for file in os.listdir(search_dir):
                arguments.append(f"{file}{SEPARATOR}{query}{SEPARATOR}{search_dir}{SEPARATOR}{score}")
            arguments = tuple(arguments)
            results = approx_pool(arguments, score, threads)
            end_time = perf_counter()

        print(f"\n{Tips.FINISH} Found {Colors.CYAN}{results}{Colors.RESET} results")
        print(f"{Tips.FINISH} Finished in {Colors.CYAN}{end_time - start_time:.5f}{Colors.RESET} seconds with {Colors.CYAN}({threads}){Colors.RESET} processorsn")
        print(f"-" * len(f"$$ Finished in {end_time - start_time:.5f} seconds with ({threads}) processors") + '\n')

    # -------------------------- #
    # COMMANDS RELATED FUNCTIONS #
    # -------------------------- #

    def refresh_display_wrapper():
        refresh_display(PROGRAM, VERSION, SCRIPT_DIR, notifications, search_method)


    def t_command(usr_input, system_cpus, current_cpus):
        usr_input = usr_input.lstrip('/t').strip()
        try:
            allocator_output = thread_allocator(usr_input, system_cpus)
            print(f"Allocated ({allocator_output}) cpu threads to the conversion process")
            return allocator_output
        except TooManyThreadError:
            print(f"{Tips.ERROR} Cannot allocate more than ({system_cpus}) cpu threads on this system")
        except ZeroThreadError:
            print(f"{Tips.ERROR} The number of allocated processors must be greater than 0")
        except ThreadAllocatorArgumentError:
            print(f"{Tips.ERROR} Invalid option for /t [thread]")
        return current_cpus


    def mt_command(usr_input):
        usr_input = usr_input.lstrip('/mt').strip()
        VALID_ARGS = ('-p', '--proximity', '-e', '--exact', '')
        if usr_input not in VALID_ARGS:
            print(f"{Tips.ERROR} Invalid argument for /mt [method]")
            return 'invalid'

        if usr_input in VALID_ARGS[0:1]:
            method = 'proximity_match'
        elif usr_input in VALID_ARGS[2:4]:
            method = 'exact_match'
        
        program_settings[METHOD_KEYWORD] = method
        write_settings(SETTINGS_DIR, program_settings)
        return method


    def s_command(usr_input, current_score):
        usr_input = usr_input.lstrip('/s').strip()
        try:
            if float(usr_input) < 0 or float(usr_input) > 1:
                print(f"{Tips.ERROR} /s [score] must be between 0 and 1")
                return current_score
            current_score = usr_input
        except ValueError:
            if usr_input != '':
                print(f"{Tips.ERROR} Invalid parameter for /ls [score]")
                return current_score
            current_score = 0.85
        print(f"Set the approximate searcher confidence score to {current_score}")
        return current_score


    def cd_command(usr_input, current_dir):
        usr_input = usr_input.lstrip('/cd').strip()
        try:
            new_path = change_target(SCRIPT_DIR, usr_input, current_dir)
            program_settings[TARGET_DIR_KEYWORD] = new_path
            write_settings(SETTINGS_DIR, program_settings)
            refresh_display_wrapper()
            return new_path
        except OSError:
            print(f"{Tips.ERROR} Couldn't find {usr_input}")
        except IndexError:
            print(f"{Tips.ERROR} {usr_input} is an invalid relative path")
        except PathSeparatorError:
            print(f"{Tips.ERROR} {usr_input} contains invalid path separator")
        return current_dir


    def ls_command(ls_args, ls_column):
        ls_args = ls_args.lstrip('/ls').strip().split()
        try:
            ls_num, ls_dir = validate_ls_args(ls_args, ls_column)
            FILE_COLORS = {'.txt' : Colors.GREEN}
            if ls_dir in ('-t', '--target'):
                list_directory(target_dir, ls_num, FILE_COLORS)
            elif ls_dir in ('-s', '--script'):
                list_directory(SCRIPT_DIR, ls_num, FILE_COLORS)
            return ls_num
        except ListNumError:
            print(f"{Tips.ERROR} /ls [column] must be greater than 0")
        except ListDirError:
            print(f"{Tips.ERROR} Invalid value for /ls [dir]")
        return ls_column

    # ----------------- #
    # MAIN PROGRAM LOOP #
    # ----------------- #

    refresh_display_wrapper()
    try:
        notifications = ''  # reset notifications for later loops
        while True:
            prompt_dir = bash_prompt_dir(target_dir, SCRIPT_DIR)
            user_input = input(f"{Colors.CYAN}[{PROGRAM} {prompt_dir}]${Colors.RESET} ")

            # Handling user input
            if user_input.startswith('/ls'):
                saved_columns = ls_command(user_input, saved_columns)
                continue

            if user_input.startswith('/cd'):
                target_dir = cd_command(user_input, target_dir)
                continue

            if user_input.startswith('/t'):
                allocated_threads = t_command(user_input, SYSTEM_CPUS, allocated_threads)
                continue

            if user_input.startswith('/s'):
                approx_score = s_command(user_input, approx_score)
                continue

            if user_input.startswith('/mt'):
                output = mt_command(user_input)
                if output != 'invalid':
                    search_method = output
                    refresh_display_wrapper()
                continue

            if user_input == '/c':
                refresh_display_wrapper()
                continue

            if user_input == '/h':
                for line in COMMANDS:
                    print(line)
                continue

            if user_input == '/q':
                sys.exit(0)
            elif user_input.startswith('/'):
                print(f"{Tips.ERROR} Invalid command. Type /h to see a list of available commands")
            elif user_input:
                print('-' * len(f"[{PROGRAM} {prompt_dir}]$ {user_input}"))
                searchers_wrapper(target_dir, search_method, user_input, approx_score, allocated_threads)
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        write_crashlog(CONFIG_DIR, PROGRAM, err)
        user_input = input("Press <ENTER> to exit ")
