# ------------------------------------- #
# DBVG SearTxT (Single-threaded)        #
# Still very much bloated though.       #
# Written and tested with Python 3.10.8 #
# ------------------------------------- #

import os
import sys

from difflib import get_close_matches
from difflib import SequenceMatcher

from time import perf_counter
from datetime import datetime
from traceback import format_exc


# Initialize script directory and other variables
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VERSION = 1.0
notifications = ''
custom_column_num = 0
approx_score = 0.85
softwaring = True
searching = False


class Colors:
    RESET = '\033[0m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    CYAN = '\033[1;36m'

COMMANDS = [
    'Usage: /[command] <required parameters> (optional parameters)',
    '  or:  <search query>\n',
    '/ap <absolute path> : change the search directory to a folder outside the script directory',
    '/cd <relative path> : change the search directory to a folder inside the script directory',
    '/ls (column) (dir)  : list all items in the specified directory',
    '/mt (method)        : change to either approximate or exact searching method',
    '/c                  : refresh the display',
    '/h                  : print out all available commands',
    '/q                  : exit the program\n',
    '/s (score)          : set the minimum score of the approximate searcher results'
]


# Read config file. Generate the default config and create the config directory in case of errors
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
SETTINGS_DIR = os.path.join(CONFIG_DIR, "seartxt.conf")
DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')
def write_settings():
    with open(SETTINGS_DIR, 'w', encoding='utf8') as settings_file:
        settings_file.writelines([f'{target_dir}\n', f'{search_method}\n'])

try:
    rewrite_config = False
    with open(SETTINGS_DIR, 'r', encoding='utf8') as settings:
        target_dir = settings.readline().strip()
        search_method = settings.readline().strip().lower()

    if not os.path.exists(target_dir):
        if not os.path.exists(DEFAULT_TARGET_DIR):
            os.makedirs(DEFAULT_TARGET_DIR)
        target_dir = DEFAULT_TARGET_DIR
        rewrite_config = True

    if search_method not in ("proximity_match", "exact_match"):
        search_method = "exact_match"
        rewrite_config = True

    if rewrite_config:
        write_settings()
        notifications = "> seartxt.conf contained invalid configuration. Generated a default template\n"
except FileNotFoundError:
    target_dir = DEFAULT_TARGET_DIR
    search_method = "exact_match"

    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    write_settings()
    notifications = "> seartxt.conf couldn't be found. Generated a default template\n"


def refresh_display():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

    print(f"{Colors.CYAN}***** DBVG SearTxT ver {VERSION} *****{Colors.RESET}")
    print(f"Script directory: {Colors.CYAN}{SCRIPT_DIR}{Colors.RESET}")

    if search_method == "exact_match":
        print(f"Search method: {Colors.CYAN}exact match{Colors.RESET}")
    else:
        print(f"Search method: {Colors.CYAN}approximate match{Colors.RESET}")

    if notifications:
        print(notifications)
    else:
        print()


# List all entries within a specified directory and alphanumerically arrange them in a number of columns
def list_directory(display_columns=2, directory=target_dir):
    separator = '#$$#'
    max_lens = [0] * display_columns
    row_index = 0
    single_row = ''
    multiple_rows = []
    output_string = ''

    # First separate the sorted entries into different columns
    entries = os.listdir(directory)
    entries.sort(key=str.lower)
    for index, entry in enumerate(entries, start=0):
        if len(entry) > max_lens[row_index]:
            max_lens[row_index] = len(entry)
        single_row += f"{entry}{separator}"
        row_index += 1

        if row_index == display_columns or index == len(entries) - 1:
            multiple_rows.append(single_row)
            row_index = 0
            single_row = ''

    # Append additional spaces to the entries depending on their column position
    # Print the entire row once all columns are appended
    for index, entry in enumerate(multiple_rows, start=0):
        raw_list = list(filter(None, entry.split(separator)))
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
def approximate_searcher(file_name, cutoff):
    found = 0
    file_dir = os.path.join(target_dir, file_name)
    with open(file_dir, 'r', encoding='utf8') as searched_file:
        for index, line in enumerate(searched_file, start=1):
            match = get_close_matches(user_input.lower(), line.lower().split(), 1, float(cutoff))
            if match:
                score = SequenceMatcher(None, user_input, match[0]).ratio()
                print(f"{Colors.YELLOW}@@{Colors.RESET} 1 potential match at {Colors.BLUE} Line({index})"
                      f"{Colors.RESET} of {Colors.BLUE}{file_name}{Colors.RESET}")
                print(f"{Colors.YELLOW}||{Colors.RESET} {line.strip()}")
                print(f"{Colors.YELLOW}||{Colors.RESET} confidence: {Colors.YELLOW} {score:.5f}{Colors.RESET}")
                found += 1

    return found


# Search the file by enumerating through its content line by line
# Only return results that exactly match the search query (case-insensitive)
def exact_searcher(file_name):
    found = 0
    file_dir = os.path.join(target_dir, file_name)
    with open(file_dir, 'r', encoding='utf8') as searched_file:
        for index, line in enumerate(searched_file, start=1):
            if user_input.lower() in line.lower():
                print(f"{Colors.GREEN}##{Colors.RESET} 1 match at {Colors.BLUE}Line({index}) {Colors.RESET} of "
                      f"{Colors.BLUE}{file_name}{Colors.RESET}")
                print(f"{Colors.GREEN}||{Colors.RESET} {line.strip()}")
                found += 1

    return found


# Main program loop
if __name__ == '__main__':
    refresh_display()
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
            user_input = input(f"{Colors.CYAN}[SearTxT {prompt_dir}]%{Colors.RESET} ")

            if user_input == '/c':
                refresh_display()
            elif user_input.startswith('/cd'):
                user_input = user_input.lstrip('/cd').strip()
                relative_dir = os.path.join(SCRIPT_DIR, user_input)
                if os.path.exists(relative_dir):
                    target_dir = relative_dir
                    write_settings()
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} cannot find {user_input} in script directory")
            elif user_input.startswith('/ap'):
                user_input = user_input.lstrip('/ap').strip()
                if os.path.exists(user_input):
                    target_dir = user_input
                    write_settings()
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} {user_input} is an invalid directory")
            elif user_input.startswith('/ls'):
                ListNumError = False
                list_num = 0
                list_dir = '-t'
                list_args = user_input.lstrip('/ls').strip().split()

                for arg in list_args:
                    try:
                        if isinstance(int(arg), int):
                            list_num = arg
                        else:
                            list_dir = arg
                    except ValueError:
                        list_dir = arg

                if not list_num and not custom_column_num:
                    custom_column_num = 2
                elif list_num:
                    if int(list_num) > 0:
                        custom_column_num = int(list_num)
                    else:
                        ListNumError = True
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} /ls (column) must be greater than 0")

                # Additional check to avoid printing two error messages at the same time
                if not ListNumError:
                    if list_dir in ('--target', '-t'):
                        list_directory(custom_column_num, target_dir)
                    elif list_dir in ('--script', '-s'):
                        list_directory(custom_column_num, SCRIPT_DIR)
                    else:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid value for /ls (dir)")
            elif user_input.startswith('/mt'):
                user_input = user_input.lstrip('/mt').strip()
                if user_input in ('-p', '--proximity'):
                    search_method = "proximity_match"
                    write_settings()
                    refresh_display()
                elif user_input in ('-e', '--exact', ''):
                    search_method = "exact_match"
                    write_settings()
                    refresh_display()
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid argument for /mt <method>")
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
            elif user_input == '/q':
                softwaring = False
            elif user_input == '/h':
                for x in COMMANDS:
                    print(x)
            elif user_input.startswith('/'):
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid command. Type /h to see a list of available commands")
            elif user_input:
                searching = True

            while searching:
                print('-' * len(f"[SearTxT {prompt_dir}]$ {user_input}"))
                result_counter = 0
                start_time = perf_counter()

                for file in os.listdir(target_dir):
                    if file.endswith('.txt'):
                        if search_method == "exact_match":
                            result_counter += exact_searcher(file)
                        elif search_method == "proximity_match":
                            result_counter += approximate_searcher(file, approx_score)

                end_time = perf_counter()
                print(f"\n{Colors.CYAN}$${Colors.RESET} Found {Colors.CYAN}{result_counter}{Colors.RESET} results")
                print(f"{Colors.CYAN}$${Colors.RESET} Operation time: {Colors.CYAN}{end_time - start_time:.5f}"
                      f"{Colors.RESET} seconds")
                print('-' * len(f"$$ Operation time: {end_time - start_time:.5f} seconds"))
                searching = False
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        LOGGING_DIR = os.path.join(CONFIG_DIR, 'seartxt_log.txt')
        with open(LOGGING_DIR, 'a', encoding='utf8') as log_file:
            log_file.write(f"###SESSION: {datetime.now()}{'#' * 40}\n")
            log_file.write('-' * len(f"###SESSION: {datetime.now()}{'#' * 40}") + "\n")
            log_file.write(f"{format_exc()}\n")
        print("\n------------------------------------------")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Program terminated by script error")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Error type: {err}")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Please inspect the log file in the config folder for more "
              f"information\n")
        user_input = input("Press <Enter> to exit ")
