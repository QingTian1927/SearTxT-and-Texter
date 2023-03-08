# ------------------------------------- #
# DBVG SearTxT                          #
# Still very much bloated though.       #
# Written and tested with Python 3.10.8 #
# ------------------------------------- #


import os
import sys

from math import ceil
from time import perf_counter
from datetime import datetime
from traceback import format_exc

from difflib import SequenceMatcher
from difflib import get_close_matches

from multiprocessing import Pool
from multiprocessing import freeze_support
from multiprocessing import set_start_method


class Colors:
    RESET = '\033[0m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    CYAN = '\033[1;36m'

VERSION = 1.0
SEPARATOR = '#@$@#'

COMMANDS = [
    'Usage: /[command] <required parameters> (optional parameters)',
    '  or:  <search query>\n',
    '/ap <absolute path> : change the search directory to a folder outside the script directory',
    '/cd <relative path> : change the search directory to a folder inside the script directory',
    '/ls (column) (dir)  : list all items in the specified directory',
    '/mt (method)        : change to either approximate or exact searching method',
    '/c                  : refresh the display',
    '/h                  : print out all available commands',
    '/q                  : exit the program',
    '/s (score)          : set the minimum score of the approximate searcher results',
    '/t (thread)         : allocate a number of cpu threads to the searching process\n'
]


def settings_arguments(directory, method):
    settings_args_list = [f"target_dir = {directory}", f"method = {method}"]
    return settings_args_list


def write_settings(settings_dir, arguments):
    if os.path.exists(settings_dir):
        old_file = f"{settings_dir}.old"
        os.replace(settings_dir, old_file)

    with open(settings_dir, 'w', encoding='utf8') as file:
        for line in arguments:
            file.write(f"{line}\n")


def read_settings(settings_dir):
    settings_target_dir = ''
    settings_search_method = ''
    with open(settings_dir, 'r', encoding='utf8') as file:
        for line in file:
            if line.startswith('target_dir = '):
                settings_target_dir = line.strip()
            elif line.startswith('method = '):
                settings_search_method = line.strip()
    return settings_target_dir, settings_search_method


def refresh_display(script_dir, method, notification):
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')
    print(f"{Colors.CYAN}***** DBVG SearTxT ver {VERSION} *****{Colors.RESET}")
    print(f"Script directory: {Colors.CYAN}{script_dir}{Colors.RESET}")

    if method == "exact_match":
        print(f"Search method: {Colors.CYAN}exact match{Colors.RESET}")
    else:
        print(f"Search method: {Colors.CYAN}approximate match{Colors.RESET}")

    if notification:
        print(notification)
    else:
        print()


# List all entries within a specified directory and alphanumerically arrange them in a number of columns
def list_directory(directory, display_columns=2):
    separator = '#$$#'
    max_lens = [0] * display_columns
    row_index = 0
    single_row = ''
    multiple_rows = []
    output_string = ''

    # First separate the sorted entries into different columns
    ls_entries = os.listdir(directory)
    ls_entries.sort(key=str.lower)
    for ls_index, ls_entry in enumerate(ls_entries, start=0):
        if len(ls_entry) > max_lens[row_index]:
            max_lens[row_index] = len(ls_entry)
        single_row += f"{ls_entry}{separator}"
        row_index += 1

        if row_index == display_columns or ls_index == len(ls_entries) - 1:
            multiple_rows.append(single_row)
            row_index = 0
            single_row = ''

    # Append additional spaces to the entries depending on their column position
    # Print the entire row once all columns are appended
    for ls_index, ls_entry in enumerate(multiple_rows, start=0):
        raw_list = list(filter(None, ls_entry.split(separator)))
        for item_index, item in enumerate(raw_list, start=0):
            spaces = " " * (max_lens[row_index] - len(item))

            if row_index < display_columns:
                if os.path.isdir(os.path.join(directory, item)):
                    output_string += f"{Colors.CYAN}{item}{Colors.RESET}{spaces}  "
                elif item.endswith(".txt"):
                    output_string += f"{Colors.GREEN}{item}{Colors.RESET}{spaces}  "
                else:
                    output_string += f"{item}{spaces}  "
            row_index += 1

            if row_index == display_columns or item_index == len(raw_list) - 1:
                print(output_string.strip())
                row_index = 0
                output_string = ''
    print()


# Search the file by enumerating through its content line by line
# and check for potential matches using the difflib library
# Only return results that have a confidence score higher than 0.75 (reasonably good enough)
# Multi-threaded
def approximate_search(args):
    args = args.split(SEPARATOR)
    found = 0
    search_output = ''

    file_name = args[0]
    query = args[1]
    search_dir = args[2]
    close_match_cutoff = float(args[3])

    if file_name.endswith('.txt'):
        file_dir = os.path.join(search_dir, file_name)
        with open(file_dir, 'r', encoding='utf8') as searched_file:
            for index, line in enumerate(searched_file, start=1):
                match = get_close_matches(query.lower(), line.lower().split(), 1, close_match_cutoff)
                if match:
                    score = SequenceMatcher(None, query, match[0]).ratio()
                    search_output += f"{Colors.YELLOW}@@{Colors.RESET} 1 potential match at {Colors.BLUE}" \
                                     f"Line({index}){Colors.RESET} of {Colors.BLUE}{file_name}{Colors.RESET}\n"
                    search_output += f"{Colors.YELLOW}||{Colors.RESET} {line.strip()}\n"
                    search_output += f"{Colors.YELLOW}||{Colors.RESET} confidence: {Colors.YELLOW}" \
                                     f"{score:.5f}{Colors.RESET}\n"
                    found += 1
    return search_output, found


# Search the file by enumerating through its content line by line
# Only return results that exactly match the search query (case-insensitive)
# Multi-threaded
def exact_search(args):
    args = args.split(SEPARATOR)
    found = 0
    search_output = ''

    file_name = args[0]
    query = args[1]
    search_dir = args[2]

    if file_name.endswith('.txt'):
        file_dir = os.path.join(search_dir, file_name)
        with open(file_dir, 'r', encoding='utf8') as searched_file:
            for index, line in enumerate(searched_file, start=1):
                if query.lower() in line.lower():
                    search_output += f"{Colors.GREEN}##{Colors.RESET} 1 match at {Colors.BLUE}Line({index})" \
                                     f"{Colors.RESET} of {Colors.BLUE}{file_name}{Colors.RESET}\n"
                    search_output += f"{Colors.GREEN}||{Colors.RESET} {line.strip()}\n"
                    found += 1
    return search_output, found


if __name__ == '__main__':
    freeze_support()           # Required for binary compilation
    set_start_method('spawn')  # Ensure compatibility with Windows (and macOS)

    # Custom exceptions for the "/ls" function
    class ListNumError(Exception):
        def __init__(self, message="/ls (column) must be greater than 0"):
            self.message = message
            super().__init__(self.message)

    class ListDirError(Exception):
        def __init__(self, message="Invalid parameter for /ls (dir)"):
            self.message = message
            super().__init__(self.message)

    # Initialize script directory
    if getattr(sys, 'frozen', False):
        SCRIPT_DIR = os.path.dirname(sys.executable)
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # GLOBAL VARIABLES
    softwaring = True
    searching = False

    notifications = ''
    ls_column = 0
    approx_score = 0.85
    SYSTEM_CPUS = os.cpu_count()
    allocated_threads = SYSTEM_CPUS

    CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
    SETTINGS_DIR = os.path.join(CONFIG_DIR, 'seartxt.conf')
    DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')

    # Read config file. Generate the default config and create the config directory in case of errors
    try:
        rewrite_config = False
        settings_results = read_settings(SETTINGS_DIR)

        # This weird setup is to account for strip() accidentally stripping away the first character of a relative path
        # Example (Python Console):
        # >>> target_dir = "example"
        # >>> target_dir.lstrip('target_dir =').strip()
        # 'xample'
        target_dir = settings_results[0].lstrip('target_dir').strip().lstrip('=').strip()  # Could definitely be
        search_method = settings_results[1].lstrip('method').strip().lstrip('=').strip()   # improved a lot

        if not os.path.exists(target_dir):
            if not os.path.exists(DEFAULT_TARGET_DIR):
                os.makedirs(DEFAULT_TARGET_DIR)
            target_dir = DEFAULT_TARGET_DIR
            rewrite_config = True

        if search_method not in ('exact_match', 'proximity_match'):
            search_method = 'exact_match'
            rewrite_config = True

        if rewrite_config:
            write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
            notifications = "> seartxt.conf contained invalid configuration. Generated a default template\n"
    except FileNotFoundError:
        target_dir = DEFAULT_TARGET_DIR
        search_method = 'exact_match'
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
        notifications = "> seartxt.conf couldn't be found. Generated a default template\n"

    # Main program loop
    refresh_display(SCRIPT_DIR, search_method, notifications)
    try:
        while softwaring:
            # Bash-like prompt
            # Relative paths are abbreviated with '~'
            # Ex: /home/DBVG/SearTxT/example
            # ->  ~example
            notifications = ''
            tail_dir = os.path.split(target_dir)[1]
            if os.path.exists(os.path.join(SCRIPT_DIR, tail_dir)) and target_dir != SCRIPT_DIR:
                prompt_dir = f"~{tail_dir}"
            elif target_dir == SCRIPT_DIR:
                prompt_dir = "~"
            else:
                prompt_dir = target_dir
            user_input = input(f"{Colors.CYAN}[SearTxT {prompt_dir}]${Colors.RESET} ")

            # Handling user_input
            if user_input == '/c':
                refresh_display(SCRIPT_DIR, search_method, notifications)
            elif user_input.startswith('/cd'):
                user_input = user_input.lstrip('/cd').strip()
                relative_dir = os.path.join(SCRIPT_DIR, user_input)
                if user_input == '~':
                    target_dir = SCRIPT_DIR
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
                elif os.path.exists(relative_dir):
                    target_dir = relative_dir
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} cannot find {user_input} in script directory")
            elif user_input.startswith('/ap'):
                user_input = user_input.lstrip('/ap').strip()
                if os.path.exists(user_input):
                    target_dir = user_input
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} {user_input} is an invalid directory")
            elif user_input.startswith('/ls'):
                ls_num = 0
                ls_dir = '-t'
                ls_args = user_input.lstrip('/ls').strip().split()

                # Argument handler: could probably be improved
                for arg in ls_args:
                    try:
                        if isinstance(int(arg), int):
                            ls_num = arg
                        else:
                            ls_dir = arg
                    except ValueError:
                        ls_dir = arg

                # Send the right parameters to list_directory()
                try:
                    if not ls_num and not ls_column:
                        ls_column = 2
                    elif ls_num:
                        if int(ls_num) > 0:
                            ls_column = int(ls_num)
                        else:
                            raise ListNumError

                    if ls_dir in ('-t', '--target'):
                        list_directory(target_dir, ls_column)
                    elif ls_dir in ('-s', '--script'):
                        list_directory(SCRIPT_DIR, ls_column)
                    else:
                        raise ListDirError
                except ListNumError:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} /ls (column) must be greater than 0")
                except ListDirError:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid value for /ls (dir)")
            elif user_input.startswith('/mt'):
                user_input = user_input.lstrip('/mt').strip()
                if user_input in ('-e', '--exact', ''):
                    search_method = 'exact_match'
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
                    refresh_display(SCRIPT_DIR, search_method, notifications)
                elif user_input in ('-p', '--proximity'):
                    search_method = 'proximity_match'
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir, search_method))
                    refresh_display(SCRIPT_DIR, search_method, notifications)
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid argument for /mt (method)")
            elif user_input.startswith('/t'):
                allocation_changed = False
                user_input = user_input.lstrip('/t').strip()
                try:
                    if int(user_input) > SYSTEM_CPUS:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Cannot allocate more than ({SYSTEM_CPUS})"
                              f" cpu threads on this system")
                    elif int(user_input) <= 0:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} The number of allocated processors must be greater "
                              f"than 0")
                    else:
                        allocated_threads = int(user_input)
                        allocation_changed = True
                except ValueError:
                    # Ceil ensures that at least 1 cpu thread will always be allocated
                    if user_input in ('--half', '-h'):
                        allocated_threads = ceil(SYSTEM_CPUS / 2)
                        allocation_changed = True
                    elif user_input in ('--quarter', '-q'):
                        allocated_threads = ceil(SYSTEM_CPUS / 4)
                        allocation_changed = True
                    elif user_input in ('--all', '-a', ''):
                        allocated_threads = SYSTEM_CPUS
                        allocation_changed = True
                    else:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid option for /t <cpu thread>")
                if allocation_changed:
                    print(f"Allocated ({allocated_threads}) cpu threads to the searching process")
            elif user_input.startswith('/s'):
                user_input = user_input.lstrip('/s').strip()
                try:
                    if 0 <= float(user_input) <= 1:
                        approx_score = user_input
                        print(f"Set the approximate searcher confidence score to {approx_score}")
                    else:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} /s (score) must be between 0 and 1")
                except ValueError:
                    if user_input == '':
                        approx_score = 0.85
                        print(f"Set the approximate searcher confidence score to {approx_score}")
                    else:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid parameter for /ls (score)")
            elif user_input == '/h':
                for command in COMMANDS:
                    print(command)
            elif user_input == '/q':
                softwaring = False
            elif user_input.startswith('/'):
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid command. Type /h to see a list of available commands")
            elif user_input:
                print('-' * len(f"[SearTxT {prompt_dir}]$ {user_input}"))
                searching = True

            # Search loop
            while searching:
                result_counter = 0
                end_time = 0
                search_args = []
                start_time = perf_counter()

                if search_method == 'exact_match':
                    for file_entry in os.listdir(target_dir):
                        search_args.append(f"{file_entry}{SEPARATOR}{user_input}{SEPARATOR}{target_dir}")
                    with Pool(allocated_threads) as pool:
                        for output, found_num in pool.imap_unordered(exact_search, search_args):
                            if not output or not found_num:
                                # Filter out empty return results
                                # This will (probably) be re-implemented in the future
                                continue
                            print(f"{output.strip()}")
                            result_counter += found_num
                    end_time = perf_counter()
                elif search_method == 'proximity_match':
                    for file_entry in os.listdir(target_dir):
                        search_args.append(f"{file_entry}{SEPARATOR}{user_input}{SEPARATOR}{target_dir}{SEPARATOR}"
                                           f"{approx_score}")
                    with Pool(allocated_threads) as pool:
                        for output, found_num in pool.imap_unordered(approximate_search, search_args):
                            if not output or not found_num:
                                # Same as exact_search
                                continue
                            print(f"{output.strip()}")
                            result_counter += found_num
                    end_time = perf_counter()

                print(f"\n{Colors.CYAN}$${Colors.RESET} Found {Colors.CYAN}{result_counter}{Colors.RESET} results")
                print(f"{Colors.CYAN}$${Colors.RESET} Finished in {Colors.CYAN}{end_time - start_time:.5f}"
                      f"{Colors.RESET} seconds with {Colors.CYAN}({allocated_threads}){Colors.RESET} cpu threads")
                print('-' * len(f"$$ Finished in {end_time - start_time:.5f} seconds with ({allocated_threads}) "
                                f"cpu threads"))
                searching = False
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        LOGGING_DIR = os.path.join(CONFIG_DIR, 'seartxt_log.txt')
        with open(LOGGING_DIR, 'a', encoding='utf8') as log_file:
            log_file.write(f"###SESSION: {datetime.now()}{'#' * 40}\n")
            log_file.write('-' * len(f"###SESSION: {datetime.now()}{'#' * 40}") + "\n")
            log_file.write(f"{format_exc()}\n\n")
        print("\n------------------------------------------")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Program terminated by script error")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {err}")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Please inspect the log file in the config folder for more "
              f"information\n")
        user_input = input("Press <Enter> to exit ")
