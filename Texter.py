# --------------------------------------------- #
# DBVG Texter                                   #
# Written and tested with Python 3.10.8         #
# Foreign dependencies: pypandoc, pdfminer.six  #
# --------------------------------------------- #

import os
import sys
import logging
from math import ceil
from time import perf_counter
from datetime import datetime
from traceback import format_exc
from multiprocessing import Pool
from multiprocessing import freeze_support

import pypandoc
from pdfminer.high_level import extract_text


# Initialize script directory and other variables
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VERSION = 1.0
SYSTEM_CPUS = os.cpu_count()
allocated_threads = SYSTEM_CPUS
notifications = ''
custom_column_num = 0
softwaring = True
converting = False


class Colors:
    RESET = '\033[0m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    CYAN = '\033[1;36m'


CAT = [
    "        ∧＿∧",
    "  ／＼（ ・∀・）／ヽ",
    "（ ● と    つ ●   ）",
    "  ＼/⊂、  ノ   ＼ノ",
    "      し’",
]

COMMANDS = [
    'Usage: /[command] <required parameter> (optional parameter)\n',
    '/ap <absolute path> : change the convert directory to a folder outside the script directory',
    '/cd <relative path> : change the convert directory to a folder inside the script directory',
    '/ls (column) (dir)  : list all items in the convert directory',
    '/pd                 : download and install the pandoc runtime',
    '/cv                 : start the conversion process',
    '/t <cpu thread>     : specify the number of cpu threads used for conversion',
    '/h                  : display all available commands',
    '/c                  : clear the display',
    '/q                  : terminate the program\n',
]

DEFAULT_UNSUPPORTED_TYPES = [
    '# Officially Unsupported File Types\n',
    '# -----------------------------------------------------------------\n',
    '# To add additional file types, use the following structure:\n',
    '# .file_type1 <SPACE> .file_type2 <SPACE> ... <SPACE> .file_type100\n\n',
    '# Web Development\n',
    '.css .sass .html .htm .js .jsm .mjs .json\n\n',
    '# Markdown & Org Mode\n',
    '.markdown .md .mkd .org\n\n',
    '# Plain\n',
    '.v .asc .log .conf\n\n',
    '# Office\n',
    '.doc\n\n',
    '# Programming Languages\n',
    '.py .py3 .pyi .pyx .py3x .wsgi\n',
    '.rs .vbs .lua .p .pas .kt .java\n',
    '.c .C .cs .c++ .cc .cpp .cxx\n',
    '.lisp .go .hs\n',
]


# Read config file. Generate a default config file and the config directory in case of errors
CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
SETTINGS_DIR = os.path.join(CONFIG_DIR, 'texter.conf')
DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')
def write_settings():
    with open(SETTINGS_DIR, 'w', encoding='utf8') as settings_file:
        settings_file.write(f"{target_dir}\n")

try:
    with open(SETTINGS_DIR, 'r', encoding='utf8') as f:
        target_dir = f.readline().strip()

    if not os.path.exists(target_dir):
        target_dir = DEFAULT_TARGET_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        old_settings = os.path.join(SCRIPT_DIR, 'config/texter_old.conf')
        os.replace(SETTINGS_DIR, old_settings)
        write_settings()
        notifications = "> texter.conf contained invalid configuration. Generated a default template\n"
except FileNotFoundError:
    target_dir = DEFAULT_TARGET_DIR
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    write_settings()
    notifications = "> texter.conf couldn't be found. Generated a default template\n"


# Get the additional file types from the config file. Generate a default template in case of errors
TYPES_DIR = os.path.join(CONFIG_DIR, 'unsupported_types.conf')
UNSUPPORTED_TYPES = []
def fetch_types(types_raw):
    for line in types_raw:
        if line.startswith('#') or not line:
            continue
        for type_ in line.split():
            UNSUPPORTED_TYPES.append(type_)

try:
    with open(TYPES_DIR, 'r', encoding='utf8') as file:
        fetch_types(file)
except FileNotFoundError:
    with open(TYPES_DIR, 'w', encoding='utf8') as f:
        f.writelines(DEFAULT_UNSUPPORTED_TYPES)
    fetch_types(DEFAULT_UNSUPPORTED_TYPES)
    notifications += "> unsupported_types.conf couldn't be found. Generated a default template\n"


def refresh_display():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')
    print(f"{Colors.CYAN}*****DBVG Texter ver {VERSION}*****{Colors.RESET}")
    print(f"Script directory: {Colors.CYAN}{SCRIPT_DIR}{Colors.RESET}")
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
                elif item.endswith(".docx"):
                    output_string += f"{Colors.BLUE}{item}{Colors.RESET}{spaces}  "
                elif item.endswith(".pdf"):
                    output_string += f"{Colors.RED}{item}{Colors.RESET}{spaces}  "
                elif item.endswith(".txt"):
                    output_string += f"{Colors.GREEN}{item}{Colors.RESET}{spaces}  "
                elif os.path.splitext(item)[1] in UNSUPPORTED_TYPES:
                    output_string += f"{Colors.YELLOW}{item}{Colors.RESET}{spaces}  "
                else:
                    output_string += f"{item}{spaces}  "
            row_index += 1

            if row_index == display_columns or item_index == len(raw_list) - 1:
                print(output_string.strip())
                row_index = 0
                output_string = ''


# Convert .docx using pypandoc.convert_file and .pdf with pdfminer.extract_text
# Always delete the original file after a successful conversion
# For unsupported file formats, simply read the original file in plain text mode and write the content to a new .txt
# Skip .txt and everything else not in the UNSUPPORTED_TYPES list
def file_converter(file_name):
    success = 0
    fail = 0
    dupfile_num = 0
    old_dir = os.path.join(target_dir, file_name)
    file_extension = os.path.splitext(old_dir)[1]
    new_dir = f"{os.path.splitext(old_dir)[0]}.txt"

    while os.path.exists(new_dir):
        dupfile_num += 1
        new_dir = f"{os.path.splitext(old_dir)[0]}-dup.{dupfile_num}.txt"

    if file_extension == '.docx':
        try:
            pypandoc.convert_file(old_dir, 'plain', outputfile=new_dir)
            os.remove(old_dir)
            success = 1
            converter_output = f"{Colors.GREEN}##{Colors.RESET} Successfully converted {file_name}"
        except RuntimeError:
            converter_output = f"{Colors.RED}XX{Colors.RESET} Failed to convert {file_name}"
            fail = 1
        except OSError:
            converter_output = f"{Colors.RED}XX{Colors.RESET} Pandoc was not found. Use /pd to download and " \
                               f"install pandoc\n"
            converter_output += f"{Colors.RED}||{Colors.RESET} Failed to convert {file_name}"
            fail = 1
    elif file_extension == '.pdf':
        with open(old_dir, 'rb'):
            extracted_content = extract_text(old_dir)
        with open(new_dir, 'w', encoding='utf8') as new_file:
            new_file.write(extracted_content)
        os.remove(old_dir)
        success = 1
        converter_output = f"{Colors.GREEN}##{Colors.RESET} Successfully converted {file_name}"
    elif file_extension in UNSUPPORTED_TYPES:
        converter_output = f"{Colors.YELLOW}@@{Colors.RESET} {file_extension} is an unsupported file format\n"
        with open(old_dir, 'r', encoding='utf8', errors='replace') as old_file:
            for each_line in old_file:
                with open(new_dir, 'a', encoding='utf8') as new_file:
                    new_file.write(each_line)
        os.remove(old_dir)
        success = 1
        converter_output += f"{Colors.YELLOW}||{Colors.RESET} Tried to convert {file_name}"
    else:
        converter_output = f"{Colors.BLUE}%%{Colors.RESET} Skipped {file_name}"

    return converter_output, success, fail


# Main program loop
if __name__ == '__main__':
    freeze_support()
    refresh_display()
    try:
        while softwaring:
            notifications = ''
            head_dir = os.path.split(target_dir)[0]
            tail_dir = os.path.split(target_dir)[1]
            if head_dir == SCRIPT_DIR:
                prompt_dir = f"~{tail_dir}"
            else:
                prompt_dir = f"{target_dir}"
            user_input = input(f"{Colors.CYAN}[Texter {prompt_dir}]${Colors.RESET} ")

            if user_input == '/cv':
                print(f"{Colors.RED}[WARNING]{Colors.RESET} This will {Colors.RED}PERMANENTLY DELETE{Colors.RESET} "
                      f"the original files")
                print(f"{Colors.RED}[WARNING]{Colors.RESET} Make sure you have a backup in case of error")
                user_input = input("Proceed with conversion? [y/n]: ").lower()
                if user_input in ('yes', 'y'):
                    converting = True
                elif user_input in ('no', 'n'):
                    print("Conversion cancelled")
                else:
                    print("Invalid option. Conversion cancelled")
            elif user_input == '/c':
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
            elif user_input == '/q':
                softwaring = False
            elif user_input == '/h':
                for x in COMMANDS:
                    print(x)
            elif user_input.startswith('/t'):
                allocation_changed = False
                user_input = user_input.lstrip('/t').strip()
                try:
                    if int(user_input) > SYSTEM_CPUS:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Cannot allocate more than ({SYSTEM_CPUS}) "
                              f"cpu threads on this system")
                    elif int(user_input) <= 0:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} The number of allocated processors must be greater "
                              f"than 0")
                    else:
                        allocated_threads = int(user_input)
                        allocation_changed = True
                except ValueError:
                    # ceil ensures that at least 1 cpu thread will always be allocated
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
                    print(f"Allocated ({allocated_threads}) cpu threads to the conversion process")
            elif user_input == '/pd':
                print("[INFO] This will download and install pandoc via the pypandoc library")
                print("[INFO] Make sure you have a stable internet connection")
                user_input = input("Proceed with operation? [y/n]: ").lower()
                if user_input in ('yes', 'y'):
                    print()
                    try:
                        print("[INFO] Attempting to connect to the pandoc github repo ...")
                        pypandoc.download_pandoc()
                        print("[INFO] Pandoc was successfully installed")
                    except TimeoutError:
                        print(f"{Colors.RED}[ERROR]{Colors.RESET} Connection timed out. Could not download pandoc")
                    print()
                elif user_input in ('no', 'n'):
                    print("Download cancelled")
                else:
                    print("Invalid option. Download cancelled")
            elif user_input == '/cat':
                for x in CAT:
                    print(x)
            else:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid command. Type /h to see a list of available commands")

            while converting:
                print()
                print("Starting conversion process...")
                print("------------------------------")
                start_time = perf_counter()
                success_count = 0
                fail_count = 0
                file_names = os.listdir(target_dir)

                # Disable pypandoc error logs
                logging.disable()
                with Pool(allocated_threads) as pool:
                    results = pool.imap_unordered(file_converter, file_names)
                    for output, success_num, fail_num in results:
                        print(output)
                        success_count += success_num
                        fail_count += fail_num
                logging.disable(logging.NOTSET)

                print()
                if success_count > 0:
                    print(f"$$ Successful conversion(s): {Colors.GREEN}{success_count}{Colors.RESET}")
                else:
                    print("$$ No conversion was performed")
                if fail_count > 0:
                    print(f"$$ Failed conversion(s): {Colors.RED}{fail_count}{Colors.RESET}")

                end_time = perf_counter()
                print(f"$$ Finished in {Colors.CYAN}({end_time - start_time:.5f}){Colors.RESET} seconds with "
                      f"{Colors.CYAN}({allocated_threads}){Colors.RESET} cpu threads")
                print("-" * len(f"$$ Finished in ({end_time - start_time:.5f}) seconds with ({allocated_threads}) "
                                f"cpu threads"))
                converting = False
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        LOGGING_DIR = os.path.join(CONFIG_DIR, 'log.txt')
        with open(LOGGING_DIR, 'a', encoding='utf8') as log_file:
            log_file.write(f"###SESSION: {datetime.now()}##############################\n")
            log_file.write("-" * len(f"###SESSION: {datetime.now()}##############################") + "\n")
            log_file.write(f"{format_exc()}\n")
        print("\n------------------------------------------")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Program terminated by script error")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Error type: {err}")
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Please inspect the log file in the config folder for more "
              f"information\n")
        user_input = input("Press <Enter> to exit ")
