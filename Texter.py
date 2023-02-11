# --------------------------------------------- #
# DBVG Texter                                   #
# Written and tested with Python 3.10.8         #
# Foreign dependencies: pypandoc, pdfminer.six  #
# --------------------------------------------- #


# native modules
import os
import sys
import logging

from time import perf_counter
from multiprocessing import Pool
from multiprocessing import freeze_support
from multiprocessing import set_start_method


# coreutils custom modules
from coreutils import Tips
from coreutils import Colors
from coreutils import SEPARATOR

from coreutils import write_settings
from coreutils import write_crashlog
from coreutils import refresh_display
from coreutils import thread_allocator
from coreutils import get_confirmation

from coreutils import change_target
from coreutils import PathSeparatorError

from coreutils import ListNumError
from coreutils import ListDirError
from coreutils import validate_ls_args


# foreign modules
from pypandoc import convert_file
from pypandoc import download_pandoc
from pdfminer.high_level import extract_text


# GLOBAL CONSTANTS
VERSION = 1.0
PROGRAM = 'Texter'

CAT = [
    "        ∧＿∧",
    "  ／＼（ ・∀・）／ヽ",
    "（ ● と    つ ●   ）",
    "  ＼/⊂、  ノ   ＼ノ",
    "      し’",
]

COMMANDS = [
    "Usage: /[command] <required parameter> (optional parameter)\n",
    "/ap <absolute path> : change the convert directory to a folder using its full path",
    "/cd <relative path> : change the convert directory to a folder relative to the current directory",
    "/ls (column) (dir)  : list all items in the convert directory",
    "/cv                 : start the conversion process",
    "/pd                 : download and install the pandoc runtime",
    "/c                  : clear the display",
    "/h                  : display all available commands",
    "/q                  : terminate the program",
    "/t (thread)         : specify the number of cpu threads used for conversion\n",
]

DEFAULT_UNSUPPORTED_TYPES = [
    "# Officially Unsupported File Types\n",
    "# -----------------------------------------------------------------\n",
    "# To add additional file types, use the following structure:\n",
    "# .file_type1 <SPACE> .file_type2 <SPACE> ... <SPACE> .file_type100\n\n",
    "# Web Development\n",
    ".css .sass .html .htm .js .jsm .mjs .json\n\n",
    "# Markdown & Org Mode\n",
    ".markdown .md .mkd .org\n\n",
    "# Plain\n",
    ".v .asc .log .conf\n\n",
    "# Office\n",
    ".doc\n\n",
    "# Programming Languages\n",
    ".py .py3 .pyi .pyx .py3x .wsgi\n",
    ".rs .vbs .lua .p .pas .kt .java\n",
    ".c .C .cs .c++ .cc .cpp .cxx\n",
    ".lisp .go .hs\n",
]


def settings_arguments(target_directory):
    settings_args_list = [f"target_dir = {target_directory}"]
    return settings_args_list

def read_settings(settings_directory):
    settings_vars_list = []
    with open(settings_directory, 'r', encoding='utf8') as settings_file:
        for line in settings_file:
            if line.startswith('target_dir = '):
                settings_vars_list.append(line.strip())
    return settings_vars_list

def fetch_types(types_raw):
    unsupported_types = []
    for line in types_raw:
        if line.startswith('#') or not line:
            continue
        for type_ in line.split():
            unsupported_types.append(type_)
    return unsupported_types


# List all entries within a specified directory and alphanumerically arrange them in a number of columns
def list_directory(directory, display_columns=2):
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
        single_row += f"{ls_entry}{SEPARATOR}"
        row_index += 1

        if row_index == display_columns or ls_index == len(ls_entries) - 1:
            multiple_rows.append(single_row)
            row_index = 0
            single_row = ''

    # Append additional spaces to the entries depending on their column position
    # Print the entire row once all columns are appended
    for ls_index, ls_entry in enumerate(multiple_rows, start=0):
        raw_list = list(filter(None, ls_entry.split(SEPARATOR)))
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
    print()


def file_converter(args):
    """
    Convert DOCX, PDF, etc. into plain text.

    Keyword arguments:
    1. file_name         -- the name of the file to be converted
    2. convert_dir       -- the full path to the convert directory (e.g. target_dir)
    3. unsupported_types -- the list of additional file types to be converted

    Keywords must be added together into a single whole string in the exact order as above. 
    Each keyword being separated by a unique string of characters:
    * example: file1.docx<@#@>/home/DBVG/Documents
    """

    args = args.split(SEPARATOR)
    file_name = args[0]
    convert_dir = args[1]
    unsupported_types = args[2]

    converter_status = ''
    duplicate = 0

    old_dir = os.path.join(convert_dir, file_name)
    old_head = os.path.splitext(old_dir)[0]
    file_extension = os.path.splitext(old_dir)[1]
    new_dir = f"{old_head} ({file_extension.lstrip('.').upper()}).txt"

    while os.path.exists(new_dir):
        duplicate += 1
        new_dir = f"{old_head} ({file_extension.lstrip('.').upper()}) ({duplicate}).txt"

    if file_extension == '.docx':
        try:
            convert_file(old_dir, 'plain', outputfile=new_dir)
            os.remove(old_dir)
            converter_status = 'success'
        except RuntimeError:
            converter_output = f"{Tips.FAIL1} Experienced a pandoc runtime error\n"
            converter_status = 'fail'
        except OSError:
            converter_output = f"{Tips.FAIL1} Pandoc couldn't be found. Please install pandoc\n"
            converter_status = 'fail'
    elif file_extension == '.pdf':
        with open(old_dir, 'rb'):
            extracted_contents = extract_text(old_dir)
        with open(new_dir, 'w', encoding='utf8') as new_file:
            new_file.write(extracted_contents)
        os.remove(old_dir)
        converter_status = 'success'
    elif file_extension in unsupported_types and os.path.isfile(old_dir):
        with open(old_dir, 'r', encoding='utf8', errors='replace') as old_file:
            for each_line in old_file:
                with open(new_dir, 'a', encoding='utf8') as new_file:
                    new_file.write(each_line)
        os.remove(old_dir)
        converter_output = f"{Tips.UNSURE1} ({file_extension}) is an unsupported file format\n"
        converter_output += f"{Tips.UNSURE2} Tried to convert {file_name}"
        converter_status = 'unsure'
    else:
        converter_output = f"{Tips.SKIPPED} Skipped {file_name}"
        converter_status = 'skip'

    if converter_status == 'success':
        converter_output = f"{Tips.SUCCESS} Successfully converted {file_name}"
    elif converter_status == 'fail':
        converter_output += f"{Tips.FAIL2} Failed to convert {file_name}"
        # The cause of failure must always be printed out first

    return converter_output, converter_status


if __name__ == '__main__':
    freeze_support()           # Required for binary compilation
    set_start_method('spawn')  # Ensure compatibility with Windows (and macOS)


    # Initialize script directory
    if getattr(sys, 'frozen', False):
        SCRIPT_DIR = os.path.dirname(sys.executable)
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


     # GLOBAL VARIABLES
    softwaring = True
    converting = False

    notifications = ''
    ls_column = 0
    SYSTEM_CPUS = os.cpu_count()
    allocated_threads = SYSTEM_CPUS
    converter_verbose_output = False

    CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
    SETTINGS_DIR = os.path.join(CONFIG_DIR, f"{PROGRAM.lower()}.conf")
    DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')
    TYPES_DIR = os.path.join(CONFIG_DIR, 'unsupported_types.conf')


    # Read config file. Generate the default config and create the config directory in case of errors
    try:
        settings_results = read_settings(SETTINGS_DIR)
        # This weird setup is to account for strip() accidentally stripping away the first character of a relative path
        # Example (Python Console):
        # >>> test = "target_dir = example"
        # >>> test.lstrip('target_dir =').strip()
        # 'xample'
        if settings_results:
            target_dir = settings_results[0].lstrip('target_dir').strip().lstrip('=').strip()
        else:
            target_dir = 'error'

        if not os.path.exists(target_dir) or target_dir == 'error':
            if not os.path.exists(DEFAULT_TARGET_DIR):
                os.makedirs(DEFAULT_TARGET_DIR)
            target_dir = DEFAULT_TARGET_DIR
            write_settings(SETTINGS_DIR, settings_arguments(target_dir))
            notifications = f"> {PROGRAM.lower()}.conf contained invalid configuration. Generated a default template\n"
    except FileNotFoundError:
        target_dir = DEFAULT_TARGET_DIR
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        write_settings(SETTINGS_DIR, settings_arguments(target_dir))
        notifications = f"> {PROGRAM.lower()}.conf couldn't be found. Generated a default template\n"


    # Get the additional file types from the config file. Generate a default template in case of errors
    try:
        with open(TYPES_DIR, 'r', encoding='utf8') as types_file:
            UNSUPPORTED_TYPES = fetch_types(types_file)
    except FileNotFoundError:
        with open(TYPES_DIR, 'w', encoding='utf8') as types_file:
            types_file.writelines(DEFAULT_UNSUPPORTED_TYPES)
        UNSUPPORTED_TYPES = fetch_types(DEFAULT_UNSUPPORTED_TYPES)
        notifications += "> unsupported_types.conf couldn't be found. Generated a default template\n"


    # Main program loop
    refresh_display(PROGRAM, VERSION, SCRIPT_DIR, notifications)
    notifications = ''  # reset notifications for later loops
    try:
        while softwaring:
            # Bash-like prompt
            # Relative paths are abbreviated with '~'
            # Ex: /home/DBVG/SearTxT/example
            # ->  ~/example
            if SCRIPT_DIR in target_dir and SCRIPT_DIR != target_dir:
                tail_dir = target_dir[len(SCRIPT_DIR):]
                prompt_dir = f"~{tail_dir}"
            elif SCRIPT_DIR == target_dir:
                prompt_dir = '~'
            else:
                prompt_dir = target_dir
            user_input = input(f"{Colors.CYAN}[{PROGRAM} {prompt_dir}]${Colors.RESET} ")

            # Handling user input
            if user_input == '/c':
                refresh_display(PROGRAM, VERSION, SCRIPT_DIR)
            elif user_input.startswith('/ls'):
                try:
                    ls_column, ls_dir = validate_ls_args(user_input, ls_column)
                    if ls_dir in ('-t', '--target'):
                        list_directory(target_dir, ls_column)
                    elif ls_dir in ('-s', '--script'):
                        list_directory(SCRIPT_DIR, ls_column)
                except ListNumError:
                    print(f"{Tips.ERROR} /ls (column) must be greater than 0")
                except ListDirError:
                    print(f"{Tips.ERROR} Invalid value for /ls (dir)")
            elif user_input.startswith('/cd'):
                try:
                    target_dir = change_target(SCRIPT_DIR, user_input, '/cd', target_dir)
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir))
                    refresh_display(PROGRAM, VERSION, SCRIPT_DIR)
                except OSError:
                    print(f"{Tips.ERROR} Couldn't find {user_input} in the current directory")
                except IndexError:
                    print(f"{Tips.ERROR} {user_input} is an invalid relative path")
                except PathSeparatorError:
                    print(f"{Tips.ERROR} {user_input} contains invalid path separator")
            elif user_input.startswith('/ap'):
                try:
                    target_dir = change_target(SCRIPT_DIR, user_input, '/ap')
                    write_settings(SETTINGS_DIR, settings_arguments(target_dir))
                    refresh_display(PROGRAM, VERSION, SCRIPT_DIR)
                except OSError:
                    print(f"{Tips.ERROR} {user_input} is an invalid directory")
            elif user_input.startswith('/cv'):
                user_input = user_input.lstrip('/cv').strip()
                if user_input in ('-v', '--verbose'):
                    converter_verbose_output = True
                elif user_input in ('-b', '--brief', ''):
                    converter_verbose_output = False
                print(f"{Tips.WARNING} This will {Colors.RED}PERMANENTLY DELETE{Colors.RESET} the original files")
                print(f"{Tips.WARNING} Make sure you have a BACKUP in case of errors")
                user_input = input("Proceed with conversion? [y/n]: ").lower()
                user_permission = get_confirmation(user_input)
                if user_permission == 'invalid':
                    print("Invalid option. Conversion cancelled")
                elif not user_permission:
                    print("Conversion cancelled")
                else:
                    converting = True
            elif user_input.startswith('/t'):
                allocator_output = thread_allocator(user_input, SYSTEM_CPUS)
                if allocator_output:
                    allocated_threads = allocator_output
                    print(f"Allocated ({allocated_threads}) cpu threads to the conversion process")
            elif user_input.startswith('/pd'):
                print("[INFO] This will download and install pandoc via the pypandoc library")
                print("[INFO] Make sure you have a stable internet connection")
                user_input = input("Proceed with operation? [y/n]: ").lower()
                user_permission = get_confirmation(user_input)
                if user_permission == 'invalid':
                    print("Invalid option. Download cancelled")
                elif not user_permission:
                    print("Download cancelled")
                else:
                    print()
                    try:
                        print("[INFO] Attempting to connect to the pandoc github repo ...")
                        download_pandoc()
                        print("[INFO] Pandoc was successfully installed")
                    except TimeoutError:
                        print(f"{Tips.ERROR} Connection timed out. Couldn't download pandoc")
                    print()
            elif user_input == '/h':
                for command in COMMANDS:
                    print(command)
            elif user_input == '/q':
                softwaring = False
            elif user_input == '/cat':
                for line in CAT:
                    print(line)
            else:
                print(f"{Tips.ERROR} Invalid command. Type /h to see a list of available commands")

            while converting:
                print("\nStarting conversion process...")
                print("------------------------------")
                converter_args = []
                success_count = 0
                fail_count = 0
                unsure_count = 0
                skip_count = 0

                logging.disable()  # disable pypandoc error logs
                start_time = perf_counter()
                for each_file in os.listdir(target_dir):
                    converter_args.append(f"{each_file}{SEPARATOR}{target_dir}{SEPARATOR}{UNSUPPORTED_TYPES}")
                with Pool(allocated_threads) as pool:
                    for output, status in pool.imap_unordered(file_converter, converter_args):
                        print(output)
                        if status == 'success':
                            success_count += 1
                        elif status == 'fail':
                            fail_count += 1
                        elif status == 'unsure':
                            unsure_count += 1
                        elif status == 'skip':
                            skip_count += 1
                end_time = perf_counter()
                logging.disable(logging.NOTSET)

                print()
                if converter_verbose_output:
                    if success_count > 0:
                        print(f"{Tips.SUCCESS} Successful conversion(s): {Colors.GREEN}{success_count}{Colors.RESET}")
                    if fail_count > 0:
                        print(f"{Tips.FAIL1} Failed conversion(s): {Colors.RED}{fail_count}{Colors.RESET}")
                    if unsure_count > 0:
                        print(f"{Tips.UNSURE1} Attempted conversion(s): {Colors.YELLOW}{unsure_count}{Colors.RESET}")
                    if skip_count > 0:
                        print(f"{Tips.SKIPPED} Skipped file(s): {Colors.BLUE}{skip_count}{Colors.RESET}")
                else:
                    print(f"{Tips.FINISH} Operation result(s): "
                          f"{Colors.GREEN}#{success_count}{Colors.RESET} "
                          f"{Colors.RED}X{fail_count}{Colors.RESET} "
                          f"{Colors.YELLOW}@{unsure_count}{Colors.RESET} "
                          f"{Colors.BLUE}%{skip_count}{Colors.RESET}"
                    )

                print(f"{Tips.FINISH} Finished in {Colors.CYAN}{end_time - start_time:.5f}{Colors.RESET} seconds with"
                      f" ({allocated_threads}) cpu threads")
                print('-' * len(f"$$ Finished in {end_time - start_time:.5f} seconds with ({allocated_threads}) "
                                f"cpu threads"))
                converting = False
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        write_crashlog(CONFIG_DIR, PROGRAM, err)
        user_input = input("Press <ENTER> to exit ")
