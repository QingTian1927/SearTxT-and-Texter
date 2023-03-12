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

# foreign modules
from pypandoc import convert_file
from pypandoc import download_pandoc
from pdfminer.high_level import extract_text

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
PROGRAM = 'Texter'

CAT = (
    "        ∧＿∧",
    "  ／＼（ ・∀・）／ヽ",
    "（ ● と    つ ●   ）",
    "  ＼/⊂、  ノ   ＼ノ",
    "      し’",
)

COMMANDS = (
    "Usage: /command <required parameter> [optional parameter]\n",
    "/cd [path]          : change the convert directory to another directory",
    "/ls [column] [dir]  : list all items in the convert directory",
    "/cv [verbosity]     : start the conversion process",
    "/pd                 : download and install the pandoc runtime",
    "/c                  : clear the display",
    "/h                  : display all available commands",
    "/q                  : terminate the program",
    "/t [thread]         : specify the number of cpu threads used for conversion\n",
)

DEFAULT_UNSUPPORTED_TYPES = (
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
)

# ------------------------- #
# TEXTER-SPECIFIC FUNCTIONS #
# ------------------------- #

def fetch_types(raw_types):
    """Parse file types and return a tuple."""
    processed_types = []
    for line in raw_types:
        if line.startswith('#') or not line:
            continue
        for each_type in line.split():
            processed_types.append(each_type)
    return tuple(processed_types)


def file_converter(args):
    """
    Convert DOCX, PDF, etc. into plain text.

    Keyword arguments:
    1. file_name         --  the name of the file to be converted
    2. convert_dir       --  the full path to the convert directory (e.g. target_dir)
    3. unsupported_types --  the list of additional file types to be converted

    Keywords must be added together into a single whole string in the exact order as above. 
    Each keyword must be separated by a unique string of characters:
    * example: file1.docx<@#@>/home/DBVG/Documents
    """

    args = args.split(SEPARATOR)
    file_name = args[0]
    convert_dir = args[1]
    unsupported_types = args[2]

    old_path = os.path.join(convert_dir, file_name)
    old_head = os.path.splitext(old_path)[0]
    file_ext = os.path.splitext(old_path)[1]
    init_ext = file_ext.lstrip('.').upper()
    new_path = f"{old_head} ({init_ext}).txt"

    duplicate_count = 0
    while os.path.exists(new_path):
        duplicate_count += 1
        new_path = f"{old_head} ({init_ext}) ({duplicate_count}).txt"

    converter_status = ''
    converter_output = ''
    if file_ext == '.docx':
        converter_status, converter_output = docx_handler(old_path, new_path)
    elif file_ext == '.pdf':
        converter_status, converter_output = pdf_handler(old_path, new_path)
    elif file_ext in unsupported_types and os.path.isfile(old_path):
        # the isfile check prevents Windows from opening a folder as a file
        converter_status, converter_output = unsupported_handler(old_path, new_path, file_ext, file_name)
    else:
        converter_status = 'skip'
        converter_output = f"{Tips.SKIPPED} Skipped {file_name}"

    if converter_status in ('success', 'unsure'):
        os.remove(old_path)
        if converter_status == 'success' and not converter_output:
            converter_output = f"{Tips.SUCCESS} Successfully converted {file_name}"
    elif converter_status == 'fail':
        converter_output += f"{Tips.FAIL2} Failed to convert {file_name}"
        # The cause of failure must always be printed out first

    return converter_output, converter_status

def docx_handler(original_path, new_path):
    """Convert DOCX into TXT and return the conversion status & converter message."""
    try:
        convert_file(original_path, 'plain', outputfile=new_path)
        handler_status = 'success'
        handler_output = ''
    except RuntimeError:
        handler_status = 'fail'
        handler_output = f"{Tips.FAIL1} Experienced a pandoc runtime error\n"
    except OSError:
        handler_status = 'fail'
        handler_output = f"{Tips.FAIL1} Pandoc couldn't be found. Please install pandoc\n"
    return handler_status, handler_output

def pdf_handler(original_path, new_path):
    """Convert PDF into TXT and return the conversion status & converter message."""
    with open(original_path, 'rb'):
        extracted_contents = extract_text(original_path)
    with open(new_path, 'w', encoding='utf8') as new_file:
        new_file.write(extracted_contents)
    handler_status = 'success'
    handler_output = ''
    return handler_status, handler_output

def unsupported_handler(original_path, new_path, file_extension, file_name):
    """Convert UNSUPPORTED into TXT and return the conversion status & converter message."""
    with open(original_path, 'r', encoding='utf8', errors='replace') as old_file:
        for each_line in old_file:
            with open(new_path, 'a', encoding='utf8') as new_file:
                new_file.write(each_line)
    handler_status = 'unsure'
    handler_output = f"{Tips.UNSURE1} ({file_extension}) is an unsupported file format\n"
    handler_output += f"{Tips.UNSURE2} Tried to convert {file_name}"
    return handler_status, handler_output

# -------------------------- #
# COMMANDS RELATED FUNCTIONS #
# -------------------------- #

def pd_command():
    """Ask for user permission before calling download_pypandoc()."""
    print("[INFO] This will download and install pandoc via the pypandoc library")
    print("[INFO] Make sure you have a stable internet connection")
    usr_input = input("Proceed with operation? [y/n]: ").lower()
    user_permission = get_confirmation(usr_input)

    if user_permission == 'invalid':
        print("Invalid option. Download cancelled")
        return
    if not user_permission:
        print("Download cancelled")
        return

    print()
    try:
        print("[INFO] Attempting to connect to the pandoc github repo ...")
        download_pandoc()
        print("[INFO] Pandoc was successfully installed")
    except TimeoutError:
        print(f"{Tips.ERROR} Connection timed out. Couldn't download pandoc")
    print()


def t_command(usr_input, system_cpus, current_cpus):
    """The extracted function for '/t (threads)'"""
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
        print(f"{Tips.ERROR} Invalid option for /t (cpu thread)")
    return current_cpus

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

    SYSTEM_CPUS = os.cpu_count()
    allocated_threads = SYSTEM_CPUS

    CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
    SETTINGS_DIR = os.path.join(CONFIG_DIR, f"{PROGRAM.lower()}.conf")
    DEFAULT_TARGET_DIR = os.path.join(SCRIPT_DIR, 'example')
    TYPES_DIR = os.path.join(CONFIG_DIR, 'unsupported_types.conf')

    # Program configurations
    TARGET_DIR_KEYWORD = 'target_dir'
    SETTINGS_ARGS = {TARGET_DIR_KEYWORD : DEFAULT_TARGET_DIR}

    # ------------------------- #
    # INITIALIZE CONFIGURATIONS #
    # ------------------------- #

    # Read config file. Generate the default config and create the config directory in case of errors
    try:
        program_settings = read_settings(SETTINGS_DIR, SETTINGS_ARGS)
        target_dir = program_settings[TARGET_DIR_KEYWORD]

        if not os.path.exists(target_dir):
            notifications = f"> {PROGRAM.lower()}.conf contained invalid configuration. Generated a default template\n"
    except FileNotFoundError:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        notifications = f"> {PROGRAM.lower()}.conf couldn't be found. Generated a default template\n"

    if notifications:
        target_dir = DEFAULT_TARGET_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        write_settings(SETTINGS_DIR, SETTINGS_ARGS)

    # Get the additional file types from the config file. Generate a default template in case of errors
    try:
        with open(TYPES_DIR, 'r', encoding='utf8') as types_file:
            UNSUPPORTED_TYPES = fetch_types(types_file)
    except FileNotFoundError:
        with open(TYPES_DIR, 'w', encoding='utf8') as types_file:
            types_file.writelines(DEFAULT_UNSUPPORTED_TYPES)
        UNSUPPORTED_TYPES = fetch_types(DEFAULT_UNSUPPORTED_TYPES)
        notifications += "> unsupported_types.conf couldn't be found. Generated a default template\n"

    # --------------------------- #
    # CONVERTER WRAPPER FUNCTIONS #
    # --------------------------- #

    def prepare_converter_args(operation_dir):
        """Pack all arguments into a single string before calling file_converter()."""
        converter_args = []
        for file in os.listdir(operation_dir):
            converter_args.append(f"{file}{SEPARATOR}{operation_dir}{SEPARATOR}{UNSUPPORTED_TYPES}")
        return tuple(converter_args)


    def converter_pool(workers, args):
        """Multithreading support for file_converter()."""
        report_statuses = {'success' : 0, 'fail' : 0, 'unsure' : 0, 'skip' : 0}
        with Pool(workers) as pool:
            for output, status in pool.imap_unordered(file_converter, args):
                print(output)
                if status in report_statuses:
                    report_statuses[status] += 1
        return report_statuses


    def converter_wrapper(convert_dir, threads, verbose_output=''):
        """The extracted wrapper for file_converter()."""
        print("\nStarting conversion process...")
        print("------------------------------")

        logging.disable()  # disable pypandoc error logs
        start_time = perf_counter()

        converter_args = prepare_converter_args(convert_dir)
        statuses = converter_pool(threads, converter_args)

        end_time = perf_counter()
        logging.disable(logging.NOTSET)

        success_count = statuses['success']
        fail_count = statuses['fail']
        unsure_count = statuses['unsure']
        skip_count = statuses['skip']

        print()
        if not verbose_output:
            print(f"{Tips.FINISH} Operation result(s): "
                  f"{Colors.GREEN}#{success_count}{Colors.RESET} "
                  f"{Colors.RED}X{fail_count}{Colors.RESET} "
                  f"{Colors.YELLOW}@{unsure_count}{Colors.RESET} "
                  f"{Colors.BLUE}%{skip_count}{Colors.RESET}"
                )
        else:
            if success_count > 0:
                print(f"{Tips.SUCCESS} Successful conversion(s): {Colors.GREEN}{success_count}{Colors.RESET}")
            if fail_count > 0:
                print(f"{Tips.FAIL1} Failed conversion(s): {Colors.RED}{fail_count}{Colors.RESET}")
            if unsure_count > 0:
                print(f"{Tips.UNSURE1} Attempted conversion(s): {Colors.YELLOW}{unsure_count}{Colors.RESET}")
            if skip_count > 0:
                print(f"{Tips.SKIPPED} Skipped file(s): {Colors.BLUE}{skip_count}{Colors.RESET}")

        operation_time = end_time - start_time
        print(f"{Tips.FINISH} Finished in {Colors.CYAN}{operation_time:.5f}{Colors.RESET} seconds "
              f"with ({threads}) cpu threads")
        print('-' * len(f"{Tips.FINISH} Finished in {operation_time:.5f} seconds with ({threads}) cpu threads"))

    # -------------------------- #
    # COMMANDS RELATED FUNCTIONS #
    # -------------------------- #

    def refresh_display_wrapper():
        refresh_display(PROGRAM, VERSION, SCRIPT_DIR, notifications)


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
            FILE_COLORS = {'.docx' : Colors.BLUE, '.pdf' : Colors.RED, '.txt' : Colors.GREEN}
            if ls_dir in ('-t', '--target'):
                list_directory(target_dir, ls_num, FILE_COLORS, UNSUPPORTED_TYPES)
            elif ls_dir in ('-s', '--script'):
                list_directory(SCRIPT_DIR, ls_num, FILE_COLORS, UNSUPPORTED_TYPES)
            return ls_num
        except ListNumError:
            print(f"{Tips.ERROR} /ls (column) must be greater than 0")
        except ListDirError:
            print(f"{Tips.ERROR} Invalid value for /ls (dir)")
        return ls_column


    def cv_command(usr_input):
        usr_input = usr_input.lstrip('/cv').strip()
        if usr_input not in ('-v', '--verbose', '-b', '--brief', ''):
            print(f"{Tips.WARNING} Invalid option for /cv (verbosity)")
            return

        if usr_input in ('-b', '--brief', ''):
            verbose_output = False
        elif usr_input in ('-v', '--verbose'):
            verbose_output = True

        print(f"{Tips.WARNING} This will {Colors.RED}PERMANENTLY DELETE{Colors.RESET} the original files")
        print(f"{Tips.WARNING} Make sure you have a BACKUP in case of errors")
        usr_input = input("Proceed with conversion? [y/n]: ").lower()
        user_permission = get_confirmation(usr_input)

        if user_permission == 'invalid':
            print("Invalid option. Conversion cancelled")
            return
        if not user_permission:
            print("Conversion cancelled")
            return
        converter_wrapper(target_dir, allocated_threads, verbose_output)

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

            if user_input.startswith('/cv'):
                cv_command(user_input)
                continue

            if user_input.startswith('/pd'):
                pd_command()
                continue

            if user_input == '/c':
                refresh_display_wrapper()
                continue

            if user_input == '/h':
                for line in COMMANDS:
                    print(line)
                continue

            if user_input == '/cat':
                for line in CAT:
                    print(line)
                continue

            if user_input == '/q':
                sys.exit(0)
            else:
                print(f"{Tips.ERROR} Invalid command. Type /h to see a list of available commands")
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
    except Exception as err:
        write_crashlog(CONFIG_DIR, PROGRAM, err)
        user_input = input("Press <ENTER> to exit ")
