# This project was created using Python 3.14.5
# Data handling is managed using Pandas 3.0.6
# NumPy 2.0.3 is used for numerical calculations and array handling
# Data Frames are displayed in terminal using Tabulate 0.10.0
# Data Visualization is handled using Matplotlib 3.11.2
# sys is used for system-specific parameters and functions
# re is used for regular expression operations
# openpyxl 3.1.5 is used for writing (saving) Excel files

# ##################################################################
# Author Name: Chikezie Oguamanam
# Date: 19th October, 2026
# ##################################################################


# ##################################################################
# Preamble
# ##################################################################


# Genome_Clean: beginner-friendly command-line tool for cleaning and
# summarising DNA sequences.

# The program keeps the original table unchanged and creates
# clearly named derived tables. This makes the cleaning
# decisions reversible and lets users compare results.


# ##################################################################
# Imports
# ##################################################################

# pathlib is a python module that helps simplify working with paths.
# It is used in load_csv() to check if the file exists and to expand
# user paths, and in save_session() to suggest a default output
# filename based on the input file's name. I have used it because
# file operations and user input handling using try and except blocks
# was complex and repetitive. The methods in pathlib simplified the
# process. I have added additional comments where it is used in the
# code to explain its purpose.
#
# re was used to create regular # expressions to remove whitespace
# in the gene sequence data because creating a function to loop
# through all possible combinations and remove whitespace would
# be cumbersome and not possible in the time I have. Sources were
# cited as appropriate.

# Using sys.exit to close the program helps with clearing data
# from variables when loading data between sessions
# Using Tabulate makes it easier to draw table borders in terminal
# It was used because the some tables were not easy to read without
# formatting
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate


# ##################################################################
# Constants
# ##################################################################

# I am using Constants to avoid magic numbers and strings in the code.
# There are multiple places in the code where these values are used,
# and using constants makes it easier to update them in one place
# if needed.

VALID_BASES = set("ACGTN")
BASE_COLUMNS = ["A Count", "C Count", "G Count", "T Count", "N Count"]
SYSTEM_CLEAN_NAME = "system_cleaned_data"
USER_CLEAN_NAME = "user_cleaned_data"


# ##################################################################
# Function Definitions
# ##################################################################

# ##################################################################
# Function Name: ask_choice
# Description:  Repeats a prompt until the user inputs one of the
#               accepted choices (case-insensitive).
# In Parameters:prompt: str, choices: list
# Out Type:     str
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial implementation of
#                                          input validation loop
# ##################################################################

def ask_choice(prompt, choices):
    # My original code repeated requesting userinput multiple times,
    # so I investigated a way to make it more efficient.
    # I decided the best thing was to abstract the
    # logic into a reusable function.


    choices = {str(choice).lower() for choice in choices}
    while True:
        # The User Prompt is passed as a parameter when the
        # ask choice function is called. Strip and lower are
        # used to sanitize the input
        answer = input(prompt).strip().lower()
        if answer in choices:
            return answer
        print(f"Invalid input. Please enter one of: {', '.join(sorted(choices))}.")

# ##################################################################
# Function Name: ask_yes_no
# Description:  Prompts the user with a strict yes/no question to
#               prevent accidental triggers.
# In Parameters:prompt: str
# Out Type:     bool
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial implementation
#                                           wrapping ask_choice
# ##################################################################

def ask_yes_no(prompt):
    # Yes/No Questions were used multiple times in the code. This
    # function takes a prompt parameter and calls the ask choice
    # function and streamlines the inclusion of the yes or no options
    # into the prompt
    # Runs the ask_choice function defined earlier and expands the
    # prompt for yes or no questions. I used yes or no questions to
    # replace asking for user input because allowing the user to
    # type in information was generating too much errors.
    # It provides parameters for the function as a list.
    return ask_choice(prompt + " (y/n): ", ["y", "n"]) == "y"

# ##################################################################
# Function Name: print_table
# Description:  Formats and prints a preview of a Pandas DataFrame
#               to the console using tabulate-style layout.
# In Parameters:frame: pd.DataFrame, rows: int
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial console formatting
#                                          implementation
# ##################################################################

def print_table(frame, rows=5):
   # This function takes frame and rows as parameters and outputs a table
   # The if statement is used to handles situations where the function
   # is passed an empty frame
    if frame.empty:
        print("(This table has no rows.)")
    else:
        # This line of code takes the values in the
        # Rows requested and creates an iterable (list)
        data = frame.head(rows).values.tolist()
        # This line of code takes the column names
        # and creates an iterable (list)
        headers = frame.columns.tolist()
        # tabulate requires iterables maxcolwidth was used to
        # keep the table not-too-large
        # tablefmt added borders
        print(tabulate(data, headers= headers,
                       maxcolwidths=36, tablefmt='fancy_grid'))

# ##################################################################
# Function Name: describe_frame
# Description:  Displays summary information about a DataFrame
#               including shape, column types, and preview rows.
# In Parameters:name: str, frame: pd.DataFrame
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial summary implementation
# ##################################################################

def describe_frame(name, frame):
    # The describe frame is used to summarize data frames in the session
    # shape returns row and column length to be used in the summary
    print(f"\n{name}: {frame.shape[0]} rows × {frame.shape[1]} columns")
    print("Column types:")
    # As part of the summary, the datatypes in the columns are printed
    print(frame.dtypes.to_string())
    print("\nFirst five rows:")
    print_table(frame)

# ##################################################################
# Function Name: load_csv
# Description:  Allows interactive loading and validation of a CSV
#               file path with retry options.
# In Parameters: None
# Out Type:     tuple (pd.DataFrame or None, Path or None)
# Author:       Chikezie Oguamanam
# Date Edited:  19th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial implementation
#               with basic file checking
# ##################################################################

def load_csv():
    # This function allows retrying paths and avoids replacing the
    # active data until a file loads.
    while True:
    # data sanitization to remove whitespace and double and single quotes
        file_path = input(
            "\nEnter the CSV file path (or type 'q' to quit): "
        ).strip().strip('"').strip("'")
        if file_path.lower() in {"q", "quit", "exit"}:
            return None, None
        # Path is used here to handle errors with loading a file.
        # It has in-built methods designed for this purpose so I
        # don't need to reinvent the wheel.
        # the expanduser method is used here to help the Path
        # method handle issues of cross-platform compatibility when
        # handling files. i.e so that my code runs without crashing
        # regardless of the os environment it tries to perform file
        # operations.
        path = Path(file_path).expanduser()
        # Error checking to see if path was successful in picking up a file.
        if not path.is_file():
            print("File not found. Check the path and try again.")
            continue
        try:
            frame = pd.read_csv(path)
            if frame.empty:
                print("The CSV has no data rows. Choose another file.")
                continue
            # The resolve method returns the full file path of the file loaded to
            # give the user clarity of the file and folder they are working in
            print(f"\nLoaded: {path.resolve()}")
            print(f"Shape: {frame.shape[0]} rows and {frame.shape[1]} columns")
            # The join method is a string method used to joins the names of the
            # columns together. Map function is used to loop through the list
            # of column names in the frame and convert them to string values.
            print(f"Columns: {', '.join(map(str, frame.columns))}")
            print("\nPreview:")
            print_table(frame)
            if ask_yes_no("Continue with this data?"):
                # .copy() method is used here to create a copy of the data Frame in the CSV
                # file. I ran into contradictions about how to handle editing the original file.
                # You may edit the original CSV during cleaning and thn the original file is lost
                # the user forever. I decided to solve that by creating a copy of the data. Not
                # Not jus a pointer to the data.
                return frame.copy(), path
            print("No problem. Choose another file. Type 'q' at the path prompt to quit.")
        # OSError was added to handle cases where the user does not have the right file permissions.
        # UnicodeError handles Errors where the file has characters that do not have the right encoding
        # pd.errors.ParserError is used to handle situations where the CSV file is to malformed to be
        # made into a pandas DataFrame
        except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as error:
            print(f"Could not read this CSV: {error}")
            print("Check that the file is a readable, comma-separated text file.")

# ##################################################################
# Function Name: choose_column
# Description:  Displays available column names and prompts the user
#               to select one by name or number.
# In Parameters:frame: pd.DataFrame, purpose: str
# Out Type:     str or None
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial menu selection for columns
# ##################################################################

def choose_column(frame, purpose="sequence"):
    # This function shows real column names instead of asking
    # users to memorise their spelling. User input was crashing
    # the program and making me create multiple error handling
    # routines. The solution I found for this is to read the
    # column names and restrict the user to just entering
    # numbers to choose an option.

    while True:
        print("\nAvailable columns:")
        # enumerate is used in this loop to add a counter (number) to the columns menu
        # it is set to start at 1 because menu's generally start at 1 and 0 is used
        # as an option to exit the menu
        for number, name in enumerate(frame.columns, start=1):
            print(f"  {number}. {name}")
        print("  0. Return to the main menu")
        answer = input(f"Choose the column containing {purpose} data: ").strip()
        if answer == "0":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(frame.columns):
            return frame.columns[int(answer) - 1]
        if answer in frame.columns:
            return answer
        print("Invalid selection. Enter a listed number, an exact column name, or 0.")

# ##################################################################
# Function Name:sequence_id_column
# Description:  The function takes  a dataframe as input and returns
#               the name of a
#               column where unique ids are stored.
# In Parameters:<frame:DataFrame>
# Out Type:     <string>
# Author:       <Chikezie Oguamanam>
# Date Edited:  <12th October, 2026>
# Revision History
# Num: <2> Date: <15th October, 2026>    Desc: Function searches columns
#                                             for likely unique id
# ##################################################################

def sequence_id_column(frame):
    # My first implementation of the function called choose_column() to let the user decide.
    # I ran into a challenge when trying to use the result of that query across multiple functions.
    # Specifically my software began asking to user for the input multiple times.
    # The options I was aware of to manage the user input included using a state caching library or
    # refactoring multiple functions. Due to time constraint, I decided to figure out a way to set it internally.
    # Future versions can improve on this

    for column in frame.columns:
        if str(column).strip().lower() in {
            "sequence id", "sequence_id", "sequenceid", "id", "gene id", "gene_id"
        }:
            return column
    return None

# ##################################################################
# Function Name: ids_for_rows
# Description:  Retrieves identifier strings or row indices for specified rows based on a boolean mask.
# In Parameters:frame: pd.DataFrame, mask: pd.Series
# Out Type:     list
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial implementation for row tracking
# ##################################################################

def ids_for_rows(frame, filter):
    # This function report IDs where possible;
    # row numbers are used as fallback for CSVs without IDs.
    # The software needs to have row ids in order to create a report
    # of rows where operations have been performed. This code abstract
    # that process so it can be used for multiple routines.

    id_column = sequence_id_column(frame)
    # the .loc[] function identifies the position in the data frame of
    # the row for which "filter" returns true. It is used to select rows
    # from the parent data frame.
    selected = frame.loc[filter]
    # If the software is able to find a unique id column
    if id_column is not None:
        # Return the list using the unique id column
        return selected[id_column].astype(str).tolist()
    # If not, use pandas built-in index labels
    return [f"row index {index}" for index in selected.index.tolist()]

# ##################################################################
# Function Name: normalise_sequence
# Description:  Normalises a sequence value by converting it to uppercase and stripping all whitespace.
# In Parameters:value: any
# Out Type:     str
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial string normalisation function
# ##################################################################

def normalise_sequence(value):
    # This function makes all bases uppercase and removes all whitespace # https://stackoverflow.com/questions/3984539/python-use-regular-expression-to-remove-the-white-space-from-all-lines
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", "", str(value)).upper()                               # https://www.youtube.com/watch?v=_mDU0-yivXE

# ##################################################################
# Function Name: clean_sequences
# Description:  Applies automated or user-directed cleaning procedures
#               to sequence data and generates an audit report.
# In Parameters:original: pd.DataFrame, sequence_column: str, mode: str
# Out Type:     tuple (pd.DataFrame, dict)
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial workflow implementation
#                                          for cleaning sequences
# ##################################################################

def clean_sequences(original, sequence_column, mode):
    # This function applies cleaning steps in a stable
    # order and retain a row-by-row audit report.
    # it is used by automated and user-directed cleaning
    # original is the file you want to clean.
    # sequence_column is the column to be cleaned
    # mode is user-directed or automated


    # Defining the DataFrame copy to be used,
    # the column in that DataFrame to be cleaned,
    # and the report Dictionary to be populated
    # post cleaning
    result = original.copy()
    raw = result[sequence_column]

    report = {
        "mode": mode,
        "sequence_column": str(sequence_column),
        "leading_or_trailing_N_removed": [],
        "invalid_character_rows_removed": [],
        "internal_N_rows_removed": [],
        "empty_sequence_rows_removed": [],
        "rows_removed": 0,
        "rows_remaining": 0,
    }

    # Run ask_yes_no() for all cleaning steps if it is a user directed clean
    if mode == "user":
        do_normalise = ask_yes_no("Normalise sequences (uppercase bases and remove whitespace)?")
        # In case the user does not want to make cases upper, but wants to remove whitespace.
        # Lower case bases are sometimes useful in gene analysis.
        do_whitespace = ask_yes_no("Remove whitespace inside and around sequences?")
        # If normalisation is declined, preserve letter case; validation is still case-insensitive.
        # The separate whitespace choice is honoured to make the user-directed flow meaningful.
        if do_normalise:
            sequences = raw.map(normalise_sequence)
        else:
            # I have used lambda functions to perform smaller computations within larger
            # operation-critical functions. This is done in order not to create complexities
            # and points-of-failure trying to pass multiple parameters
            sequences = raw.map(lambda value: "" if pd.isna(value) else str(value))
        if do_whitespace:
            # I have used lambda functions to perform smaller computations within larger
            # operation-critical functions. This is done in order not to create complexities
            # and points-of-failure trying to pass multiple parameters
            sequences = sequences.map(lambda value: re.sub(r"\s+", "", value)) #https://www.youtube.com/watch?v=_mDU0-yivXE and https://stackoverflow.com/questions/3984539/python-use-regular-expression-to-remove-the-white-space-from-all-lines
        remove_edge_n = ask_yes_no("Remove leading and trailing N bases?")
        remove_invalid = None
        remove_internal = ask_yes_no("Remove rows containing internal N bases?")
    else:
        sequences = raw.map(normalise_sequence)
        remove_edge_n = True
        remove_invalid = True
        remove_internal = True

    # Record the original missing/blank entries before changing the table.
    # This anonymous (lambda) function checks for empty cells
    empty_mask = sequences.map(lambda value: value.strip() == "")
    report["empty_sequence_rows_removed"] = ids_for_rows(result, empty_mask)
    # The tilde '~' operator is used to perform NOT operation on a boolean array
    # (pandas series). Using the not operator would not work here. It basically
    # flips True to False and vice versa, so we are returned an "opposite" copy
    # of the empty_mask list.
    keep_mask = ~empty_mask
    result = result.loc[keep_mask].copy()
    sequences = sequences.loc[keep_mask].copy()

    # Edge Ns are removed only from the ends; internal Ns are assessed separately below.
    # In Gene Sciences, leading and trailing N can be safely removed because they do not add
    # information to the gene sequence. Internal N values can be removed at the
    # discretion of the researcher with reasons to justify their removal
    # I have used lambda functions to perform smaller computations within larger
    # operation-critical functions. This lambda function checks for the rows
    # with leading and ending "N" values
    edge_changed = sequences.map(lambda value: value.upper().lstrip("N").rstrip("N") != value)
    if remove_edge_n:
        report["leading_or_trailing_N_removed"] = ids_for_rows(result, edge_changed)
        # remove leading and ending "N" values
        sequences = sequences.map(lambda value: value.upper().lstrip("N").rstrip("N"))
        # A sequence made empty by removing edge Ns is treated as empty and removed.
        newly_empty = sequences.map(lambda value: value == "")
        newly_empty_ids = ids_for_rows(result, newly_empty)
        # updates the report of empty rows. Extend is used to keep the list flat
        # i.e in order not to create another dimension by adding this list
        report["empty_sequence_rows_removed"].extend(newly_empty_ids)
        # Tilde is used to perform bitwise negation on pandas series - see line 433
        result = result.loc[~newly_empty].copy()
        sequences = sequences.loc[~newly_empty].copy()

    # Detect invalid characters before internal-N removal so each row has a clear reason.
    # any is used in the line below because it allows me search through the sequences column iteratively
    # and returns True for any row that has a non-valid character
    invalid_mask = sequences.map(lambda value: any(base not in VALID_BASES for base in value.upper()))
    if mode == "system" or remove_invalid is True:
        report["invalid_character_rows_removed"] = ids_for_rows(result, invalid_mask)
        result = result.loc[~invalid_mask].copy()
        sequences = sequences.loc[~invalid_mask].copy()
    elif invalid_mask.any():
        print("\nRows with characters outside A, C, G, T, N:")
        print(report_ids(ids_for_rows(result, invalid_mask)))
        if ask_yes_no("Remove these invalid rows?"):
            report["invalid_character_rows_removed"] = ids_for_rows(result, invalid_mask)
            result = result.loc[~invalid_mask].copy()
            sequences = sequences.loc[~invalid_mask].copy()

    # Internal N means an N remains between the sequence's first and last non-N bases.
    # Internal N is removed at the discretion of the researcher in biological
    # sciences. However, this software implements the removal of internal N when using
    # automated cleaning mode.
    # I have used lambda functions to perform smaller computations within larger
    # operation-critical functions. This is done in order not to create complexities
    # and points-of-failure trying to pass multiple parameters
    internal_mask = sequences.map(lambda value: "N" in value.upper())
    if mode == "system" or remove_internal:
        report["internal_N_rows_removed"] = ids_for_rows(result, internal_mask)
        result = result.loc[~internal_mask].copy()
        sequences = sequences.loc[~internal_mask].copy()

    # Keep the cleaned sequence in the output table, not only in a temporary variable.
    result[sequence_column] = sequences
    report["rows_removed"] = int(len(original) - len(result))
    report["rows_remaining"] = int(len(result))
    return result, report

# ##################################################################
# Function Name: report_ids
# Description:  Formats a list of row identifiers into a clean bulleted string.
# In Parameters:values: list
# Out Type:     str
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial string formatting helper
# ##################################################################

def report_ids(values):
    # This function pre-processes reports of operations. It is abstracted away, because multiple functions use it.
    return "\n".join(f"  - {value}" for value in values) if values else "  (none)"

# ##################################################################
# Function Name: show_clean_report
# Description:  Prints a comprehensive summary report of the data cleaning audit results.
# In Parameters:report: dict
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial summary report printer
# ##################################################################

def show_clean_report(report):
    # This function carries out final formatting for cleaning report
    print("\n========== CLEANING REPORT ==========")
    print(f"Cleaning mode: {report['mode']}")
    print(f"Sequence column: {report['sequence_column']}")
    # This creates an iterable for report information to be looped through
    # This reduces repetitive print and length calculations
    sections = [
        ("Rows with leading/trailing N removed", "leading_or_trailing_N_removed"),
        ("Rows removed for invalid characters", "invalid_character_rows_removed"),
        ("Rows removed for internal N", "internal_N_rows_removed"),
        ("Rows removed for empty sequences", "empty_sequence_rows_removed"),
    ]
    for heading, key in sections:
        print(f"\n{heading} ({len(report[key])}):")
        print(report_ids(report[key]))
    print(f"\nTotal rows removed: {report['rows_removed']}")
    print(f"Rows remaining: {report['rows_remaining']}")
    print("=====================================")

# ##################################################################
# Function Name: add_or_replace_frame
# Description:  The function searches the list of current data frames.
#               If the name already exists, it replaces the existing data Frame with the new dataframe.
#               If it doesn't exist it appends the new DataFrame to the list
# In Parameters:[session_data_frames:List, name: string, frame: DataFrame]
# Out Type:     List
# Author:       <Chikezie Oguamanam>
# Date Edited:  <13th October, 2026>
# Revision History
# Num: 1 Date: 19th October, 2026    Desc: This function manages the addition of Data Frames
#                                          to the Data Frame list
# ##################################################################

def add_or_replace_frame(session_data_frames, name, frame):
    # This first line filters the list in place using the
    # value of the name parameter.
    session_data_frames[:] = [
        item for item in session_data_frames if item[0] != name
    ]
    # This line appends a copy of the (new) frame to the list
    session_data_frames.append((name, frame.copy()))

# ##################################################################
# Function Name: run_cleaning
# Description:
# In Parameters: [original, session_data_frames, mode]
# Out Type:     [Report, None]
# Author:       Chikezie Oguamanam
# Date Edited:  15th Ocober, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: This function runs the cleaning
#                                              and updates the list of Data
# ##################################################################

def run_cleaning(original, session_data_frames, mode):
    # Frames in the session
    column = choose_column(original, "gene sequence")
    if column is None:
        return None
    # clean_sequences has two return values. This assigns them to variables
    cleaned, report = clean_sequences(original, column, mode)
    name = SYSTEM_CLEAN_NAME if mode == "system" else USER_CLEAN_NAME
    add_or_replace_frame(session_data_frames, name, cleaned)
    show_clean_report(report)
    print(f"\nSaved in this session as: {name}")
    return report

# ##################################################################
# Function Name: choose_frame
# Description:  Presents a selection menu for available DataFrames in the session.
# In Parameters:session_data_frames: list, original: pd.DataFrame
# Out Type:     tuple (str or None, pd.DataFrame or None)
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial selection menu for session dataframes
# ##################################################################

def choose_frame(session_data_frames, original):
    # This create a dictionary of frames to be dynamically updated this
    # is done because the list of available Dataframes changes throughout
    # a user session
    frames = {"original_data": original}
    frames.update({name: frame for name, frame in session_data_frames})
    print("\nAvailable data frames:")
    # This dynamically creates a selection menu from the dictionary of names
    for index, name in enumerate(frames, start=1):
        print(f"  {index}. {name}")
    print("  0. Cancel")
    # This runs the menu selection loop the dynamically created dictionary
    while True:
        answer = input("Choose a data frame: ").strip()
        if answer == "0":
            return None, None

        if answer.isdigit() and 1 <= int(answer) <= len(frames):
            name = list(frames)[int(answer) - 1]
            return name, frames[name]
        if answer in frames:
            return answer, frames[answer]
        print("Invalid selection. Choose a listed number/name or 0.")

# ##################################################################
# Function Name: view_frame_info
# Description:  Displays structural metadata and preview rows for any selected DataFrame in the session.
# In Parameters:original: pd.DataFrame, session_data_frames: list
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial frame info viewer workflow
# ##################################################################

def view_frame_info(original, session_data_frames):
    # This function summarizes information about frames in the session
    while True:
        print("\nData frame information")
        print("  1. System-generated cleaned data")
        print("  2. User-directed cleaned data")
        print("  3. Original data")
        print("  0. Return to main menu")
        choice = ask_choice("Choose an option: ", ["0", "1", "2", "3"])
        if choice == "0":
            return
        if choice == "3":
            describe_frame("original_data", original)
            return
        target = SYSTEM_CLEAN_NAME if choice == "1" else USER_CLEAN_NAME
        exists = any(name == target for name, _ in session_data_frames)
        if not exists:
            print(f"{target} has not been created in this session.")
            if not ask_yes_no("Would you like to generate it now?"):
                continue
            run_cleaning(original, session_data_frames, "system" if choice == "1" else "user")
            exists = any(name == target for name, _ in session_data_frames)
        if exists:
            # creates a dictionary from session  data frames, searches for "target" & assigns its value to frame
            frame = dict(session_data_frames)[target]
            # Prints the summary
            describe_frame(target, frame)
            return

# ##################################################################
# Function Name: valid_sequence_column
# Description:  Validates whether a chosen sequence column contains only valid bases and no empty entries.
# In Parameters:frame: pd.DataFrame, column: str
# Out Type:     pd.Series or None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial validation check for sequences
# ##################################################################

def valid_sequence_column(frame, column):
    # This function checks for blank and non-DNA values before counts are performed.
    # The columns for performing ACGTN and GC counts need to be cleaned before hand
    # to avoid misleading results. This rejects a colum choice with bad data and
    # prompts the user to perform a clean

    # This line maps over the specified column in the frame using normalise_sequence
    values = frame[column].map(normalise_sequence)
    # Using the pandas .eq() method allows me filter the values DataFrame and create an empty one
    empty = values.eq("")
    # I have used lambda functions to perform smaller computations within larger
    # operation-critical functions. This loops through the values object and returns any row
    # that contains invalid objects
    invalid = values.map(lambda value: any(base not in VALID_BASES for base in value))

    if empty.any() or invalid.any():
        # We are printing out reports about empty and invalid rows check and prompt the user
        #
        print("This column contains empty sequences or characters outside A, C, G, T, N.")
        print("Choose another column, or enter 0 to return and use Automated Data Clean.")
        # This reports rows with empty or invalid data
        if empty.any():
            print(f"Empty rows: {report_ids(ids_for_rows(frame, empty))}")
        if invalid.any():
            print(f"Invalid rows: {report_ids(ids_for_rows(frame, invalid))}")
        return None
    return values

# ##################################################################
# Function Name: add_base_counts
# Description:  Calculates and appends individual base count columns (A, C, G, T, N) for each sequence.
# In Parameters:frame: pd.DataFrame, column: str, output_name: str or None
# Out Type:     pd.DataFrame
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial implementation of base frequency counting
# ##################################################################

def add_base_counts(frame, column, output_name=None):
    # Count bases from each sequence; N is tracked but excluded from GC percentage
    sequences = frame[column].map(normalise_sequence)
    result = frame.copy()
    # The zip() function is used the match the ACGTN and BASE_COLUMNS according to their
    # corresponding rows in the loop. The Alternative would have been embedded loops, but this is easier to
    # read and handles sorting better.
    for base, output_column in zip("ACGTN", BASE_COLUMNS):
        # An lambda function is used here because setting up an entirely new function to
        # count the individual bases then pass that as information to this function would
        # be tedious
        result[output_column] = sequences.map(lambda value, b=base: value.count(b))
    if output_name:
        result.attrs["generated_from"] = output_name
    return result

# ##################################################################
# Function Name: base_count_report
# Description:  Generates a statistical summary of base counts across sequences in the dataset.
# In Parameters:frame: pd.DataFrame
# Out Type:     str
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial implementation of base count statistics report
# ##################################################################

def base_count_report(frame):
    # This function loops through base counts (ACGTN) and calculates standard deviation and average
    # It also reports rows where there is an anomaly in the Base value distribution
    lines = ["BASE-COUNT SUMMARY"]
    for column in BASE_COLUMNS:
        if column in frame.columns:
            # The else condition in average and std are used to avoid the software crashing if the
            # Data Frame is completely empty
            average = float(frame[column].mean()) if len(frame) else float("nan")
            std = float(frame[column].std(ddof=0)) if len(frame) else float("nan")
            # This ensures that the std is finite and > 0 to avoid crashing in the next step
            if np.isfinite(std) and std > 0:
                # We check for outliers using the 3 sigma rule because bio-scientists would want to
                # identify such anomaly in their report. Row indexes are stored in a list called unusual
                unusual = frame.index[(frame[column] - average).abs() > 3 * std].tolist()
            else:
                unusual = []
            # This returns a string report. The average is reported to 3 decimal places to take care of infinite decimals
            # values are appended to the lines list
            lines.append(f"{column}: average={average:.3f}; rows >3 SD from average={unusual or 'none'}")
    # The report per Base Column is neatly printed on separate lines
    return "\n".join(lines)

# ##################################################################
# Function Name: calculate_base_counts
# Description:  Orchestrates the selection and execution of per-base counting for a session dataset.
# In Parameters:original: pd.DataFrame, session_data_frames: list
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial workflow wrapper for base counting
# ##################################################################

def calculate_base_counts(original, session_data_frames):
    name, frame = choose_frame(session_data_frames, original)
    if frame is None:
        return
    column = choose_column(frame, "gene sequence")
    if column is None:
        return
    sequences = valid_sequence_column(frame, column)
    if sequences is None:
        return
    result = add_base_counts(frame, column, name)
    add_or_replace_frame(session_data_frames, "base_count_data", result)
    report = base_count_report(result)
    print("\n" + report)
    # Saving the report in the data frame collection keeps it available for later export.
    result.attrs["base_count_report"] = report

# ##################################################################
# Function Name: calculate_gc
# Description:  Computes GC content percentages using existing A, C, G, and T count columns.
# In Parameters:frame: pd.DataFrame
# Out Type:     pd.DataFrame
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial vectorised GC content calculation
# ##################################################################

def calculate_gc(frame):
    result = frame.copy()
    required = BASE_COLUMNS[:4]
    # Check to ensure we have all the data we need to perform the GC content analysis
    if not all(column in result.columns for column in required):
        raise ValueError("A, C, G, and T count columns are required to calculate GC content.")
    denominator = result["A Count"] + result["C Count"] + result["G Count"] + result["T Count"]
    # N bases are excluded from the denominator because they do not identify a known base.
    result["GC Content (%)"] = np.where(
        denominator > 0,
        100 * (result["G Count"] + result["C Count"]) / denominator,
        np.nan,
    )
    return result

# ##################################################################
# Function Name: gc_report
# Description:  Generates a statistical summary string for calculated GC content values.
# In Parameters:frame: pd.DataFrame
# Out Type:     str
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial GC content statistics summary generator
# ##################################################################

def gc_report(frame):
    values = frame["GC Content (%)"].dropna()
    excluded = int(frame["GC Content (%)"].isna().sum())
    if values.empty:
        summary = "No GC values could be calculated."
    else:
        # Reports the Minimum, Maximum, Median and Standard Deviation Values of the GC Content Analysis
        summary = (
            f"Minimum: {values.min():.2f}%\n"
            f"Maximum: {values.max():.2f}%\n"
            f"Median: {values.median():.2f}%\n"
            f"Standard deviation: {values.std(ddof=0):.2f}%"
        )
    return (
        "GC CONTENT SUMMARY\n" + summary +
        f"\nExcluded rows: {excluded} (empty/zero-length sequence after counting, so A+C+G+T = 0)."
    )

# ##################################################################
# Function Name: calculate_gc_content
# Description:  Interactive coordinator function to compute and store GC content percentages.
# In Parameters:original: pd.DataFrame, session_data_frames: list
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial workflow wrapper for GC content calculation
# ##################################################################

def calculate_gc_content(original, session_data_frames):
    name, frame = choose_frame(session_data_frames, original)
    if frame is None:
        return
    # I am checking if the A/C/G/T values have been computed prior to save compute and
    # not wear the user out with questions
    has_counts = all(column in frame.columns for column in BASE_COLUMNS[:4])
    if has_counts and ask_yes_no("This data frame already has A/C/G/T count columns. Use them?"):
        result = calculate_gc(frame)
    else:
        column = choose_column(frame, "gene sequence")
        if column is None:
            return
        sequences = valid_sequence_column(frame, column)
        if sequences is None:
            return
        prepared = frame.copy()
        prepared[column] = sequences
        result = calculate_gc(add_base_counts(prepared, column, name))
    add_or_replace_frame(session_data_frames, "gc_content_data", result)
    report = gc_report(result)
    result.attrs["gc_report"] = report
    print("\n" + report)
    print("\nFirst five rows with GC content:")
    print_table(result)

# ##################################################################
# Function Name: create_histogram
# Description:  Generates and saves a matplotlib histogram visualizing the distribution of GC content.
# In Parameters:original: pd.DataFrame, session_data_frames: list, output_folder: Path
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  12th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial Matplotlib histogram plotter
# ##################################################################

def create_histogram(original, session_data_frames, output_folder):
    name, frame = choose_frame(session_data_frames, original)
    if frame is None:
        return
    if "GC Content (%)" not in frame.columns:
        column = choose_column(frame, "gene sequence")
        if column is None:
            return
        sequences = valid_sequence_column(frame, column)
        if sequences is None:
            return
        prepared = frame.copy()
        prepared[column] = sequences
        frame = calculate_gc(add_base_counts(prepared, column, name))
        add_or_replace_frame(session_data_frames, "gc_content_data", frame)
    values = frame["GC Content (%)"].dropna()
    if values.empty:
        print("There are no valid GC content values to plot.")
        return
    # I am creating a folder to save files to to reduce the chance of conflict with the original file
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / "gc_content_histogram.png"
    # Fixed 10% bins make the chart directly comparable between datasets.
    plt.figure(figsize=(9, 5))
    plt.hist(values, bins=np.arange(0, 111, 10), edgecolor="black")
    plt.xlim(0, 100)
    plt.xticks(np.arange(0, 101, 10))
    plt.xlabel("GC content (%)")
    plt.ylabel("Number of sequences")
    plt.title("Distribution of GC content")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    # I used the savefig function so the user can have a copy once they close the application
    plt.savefig(output_path, dpi=150)
    print(f"Histogram saved to: {output_path.resolve()}")
    try:
        plt.show()
    except Exception:
        print("A display window is unavailable; the PNG file has still been saved.")
    finally:
        plt.close()

# ##################################################################
# Function Name: save_session
# Description:  Exports all active session DataFrames into a single multi-sheet Excel workbook.
# In Parameters:original: pd.DataFrame, session_data_frames: list, current_path: Path
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial Excel multi-sheet export writer
# ##################################################################

def save_session(original, session_data_frames, current_path):
    # Export all tables into one Excel workbook so no generated result is lost.
    suggested = current_path.with_name(f"{current_path.stem}_gene_cleaned.xlsx")
    raw = input(f"Enter output filename [.xlsx] (default: {suggested.name}): ").strip()
    output = Path(raw).expanduser() if raw else suggested
    # This is used to ensure that the file is saved in .xlsx format
    if output.suffix.lower() != ".xlsx":
        output = output.with_suffix(".xlsx")

    try:
    # The ExcelWriter and openpyxl engine are used to write multiple sheets to a single workbook.
    # The design of my software is such that it uses multiple data frames in a single session,
    # and the user may want to save all of them together for later analysis.
    # Saving multiple CSV files would be complex and less user-friendly, so I chose to use Excel format for convenience.
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            original.to_excel(writer, sheet_name="original_data", index=False)
            for name, frame in session_data_frames:
                # Excel sheet names have a 31-character limit.
                sheet = name[:31]
                frame.to_excel(writer, sheet_name=sheet, index=False)
        print(f"Session saved to: {output.resolve()}")
    except (OSError, ValueError, ImportError) as error:
        print(f"Could not save the session: {error}")
        print("Check folder permissions and confirm openpyxl is installed.")

# ##################################################################
# Function Name: has_generated_data
# Description:  Checks whether any derived dataframes have been generated during the current session.
# In Parameters:session_data_frames: list
# Out Type:     bool
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 15th October, 2026    Desc: Initial check helper for session state
# ##################################################################

# This is used to check if any dataframes have been created in the
# session. The return value is used by the exit menu option to
# decide if to call the save_session function.
def has_generated_data(session_data_frames):
    return bool(session_data_frames)

# ##################################################################
# Main Menu Loop
# ##################################################################

# ##################################################################
# Function Name: main
# Description:  Manages the primary command-line interface loop,
#               menu routing, and top-level execution logic.
# In Parameters:None
# Out Type:     None
# Author:       Chikezie Oguamanam
# Date Edited:  15th October, 2026
# Revision History
# Num: 1 Date: 12th October, 2026    Desc: Initial CLI menu orchestration loop
# ##################################################################

def main():
    #This is used to make the greeting distinguishable in terminal
    print("=" * 62)
    # I have print statements to control how the greeting appears in
    # terminal regardless of the system the software runs on.
    print("Welcome to Genome_Clean — DNA sequence cleaning and analysis")
    print("This software performs data analysis and visualization using")
    print("python and data in a csv file. If you are seeing this message,")
    print("then you have appropriately set up the software. To begin")
    print("processing data, you would need to provide a csv file of your")
    print("data. Put the file in the same directory from where you have")
    print("run this software. At the prompt provide the name of your data")
    print("file. Include the file extension, for Example \"test_data.csv\".")
    print("Tip: type Ctrl+C at any time to interrupt the program.")
    print("=" * 62)
    while True:
        original, current_path = load_csv()
        if original is None:
            print("Goodbye. No session was started.")
            return
        # A new session begins with the original table; generated tables are kept separately.
        session_data_frames = []
        while True:
            #Change the name variable to be more descriptive. Use data_frame_names.
            names = ["original_data"] + [name for name, _ in session_data_frames]
            print("\n" + "=" * 62)
            print(f"CURRENT FILE: {current_path.name}")
            print(f"DATA FRAMES IN THIS SESSION: {', '.join(names)}")
            print("1. Automated Data Clean")
            print("2. User Directed Data Clean")
            print("3. View Data Frame (Summary) Information")
            print("4. Calculate A, C, G, T, N per-base values")
            print("5. Calculate GC content")
            print("6. Create a Histogram of GC content")
            print("7. Load another data file")
            print("8. Exit")
            choice = ask_choice("Select an option (1-8): ", [str(i) for i in range(1, 9)])
            try:
                if choice == "1":
                    run_cleaning(original, session_data_frames, "system")
                elif choice == "2":
                    run_cleaning(original, session_data_frames, "user")
                elif choice == "3":
                    view_frame_info(original, session_data_frames)
                elif choice == "4":
                    calculate_base_counts(original, session_data_frames)
                elif choice == "5":
                    calculate_gc_content(original, session_data_frames)
                elif choice == "6":
                    create_histogram(original, session_data_frames, Path("output"))
                elif choice == "7":
                    if has_generated_data(session_data_frames) and ask_yes_no(
                        "Save generated tables before loading another file?"
                    ):
                        save_session(original, session_data_frames, current_path)
                    # Reinitialising the session on the next loop prevents old results mixing with new data.
                    break
                elif choice == "8":
                    if has_generated_data(session_data_frames) and ask_yes_no(
                        "Save original and generated tables before exiting?"
                    ):
                        save_session(original, session_data_frames, current_path)
                    print("Thank you for using Genome_Clean. Goodbye!")
                    return
            except KeyboardInterrupt:
                print("\nOperation interrupted. Returning to the main menu.")
            except (KeyError, ValueError, TypeError) as error:
                print(f"\nThat operation could not be completed: {error}")
                print("Your original data has not been changed. Please try another option.")

# ##################################################################
# Main Program Execution
# ##################################################################

# This is a convention in python programing. See https://google.github.io/styleguide/pyguide.html#316-naming
# Running my main function in the __main__ top level environment
# allows my code to be re-used by other software and not run the
# risk of immediately running once it is imported.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGenome_Clean interrupted. Goodbye!")
        sys.exit(0)
