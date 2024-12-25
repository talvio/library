#!/usr/bin/env python 

import pytest
import os
import random
import string
import shutil

import library_constants as C
from library import Library, UserInterface
from library import main as run_main

from my_io import RUN_RECORDED_SESSION, RECORD_ADDITIONAL_IO, RERECORD_OUTPUT


TEST_LIBRARY_VALID_1 = "test_library.txt"
CORRUPTED_TEST_LIBRARY_1 = "corrupted_test_library_1.txt"
TEMP_LIBRARY_SAVE_FILE = "temp_test_library.txt"
TEMP_TEST_RECORDING_FILE = "temp_test_recording.txt"

library_test_files = [
    ("test_library_1.txt", "Library file is corrupted for the book number 3 and line 18. BOOK_END tag is missing."),
    ("test_library_2.txt", "Library file is corrupted for the book number 2 and line 7. Book number is missing."),
    ("test_library_3.txt", "Library file is corrupted for the book number 4 and line 19. Wrong book id: 5."),
    ("test_library_4.txt", "Library file is corrupted for the book number 2 and line 11. Found two publication years."),
    ("test_library_5.txt", "Library file is corrupted for the book number 2 and line 11. Found two publication years."),
    ("test_library_6.txt", "Library file is corrupted for the book number 4 and line 23. Mandatory book information is missing."),
    ("test_library_7.txt", "Library file is corrupted at line 30. Line is empty."),
    ("test_library_8.txt", "Library file is corrupted for the book number 5 and line 30. Line begin tag is missing."),
    ("test_library_9.txt", "Library file is corrupted for the book number 4 and line 24. BOOK_END tag is missing from the end of the file."),
]

@pytest.mark.parametrize("test_library_file, run_time_error", library_test_files)
def test_library_init_broken_file(test_library_file, run_time_error):
    test_library_file = os.path.normpath(C.TEST_DATA_DIR + test_library_file)
    with pytest.raises(RuntimeError, match=run_time_error):library = Library(test_library_file) 

def test_library_init():
    test_library_file_valid = os.path.normpath(C.TEST_DATA_DIR + TEST_LIBRARY_VALID_1)
    test_library = Library(test_library_file_valid) 
    assert len(test_library.all_books) == 4
    assert test_library.all_books[0].author == "Douglas Adams"
    assert test_library.all_books[3].title == "The Sirens Of Titan"
    
def test_randomly_corrupted_library_file():
    for i in range(1,100):
        with pytest.raises(RuntimeError, match="Library file is corrupted"):library = Library(make_corrupted_test_library())

""" Creates a library test file which is a copy of a valid library file except 
    one line is randomly either 
     1. duplicated 
     2. omitted
     3. Random text is added 
"""
def make_corrupted_test_library(test_library_file_valid = None, test_data_dir = None, corrupted_test_library_file = None):
    if test_data_dir == None: test_data_dir = C.TEST_DATA_DIR
    if test_library_file_valid == None: test_library_file_valid = TEST_LIBRARY_VALID_1
    test_library_file_valid = os.path.normpath(test_data_dir + test_library_file_valid)
    if corrupted_test_library_file == None: 
        corrupted_test_library_file = os.path.normpath(test_data_dir + CORRUPTED_TEST_LIBRARY_1)
    else: 
        corrupted_test_library_file = os.path.normpath(test_data_dir + corrupted_test_library_file)
    lines = []
    line = None
    with open(test_library_file_valid, 'r') as f:
        while line != "":
            line = f.readline()
            lines.append(line)
    f.close()
    random_0to2 = random.randint(0,2)
    random_line_number = random.randint(1,len(lines)-1)
    line_number = 0
    f = open(corrupted_test_library_file, 'w', encoding="utf-8")
    #print("Random line number: " + str(random_line_number))
    for line in lines:
        line_number +=1
        if line_number == random_line_number:
            if random_0to2 == 0:
                f.write(line)
                f.write(line)
            elif random_0to2 == 1:
                f.write(''.join(random.choices(string.printable, k=100)) + "\n")
        else:
            f.write(line)
    f.close
    return corrupted_test_library_file

def test_save_library():
    test_library_file_valid = os.path.normpath(C.TEST_DATA_DIR + TEST_LIBRARY_VALID_1)
    test_library_file_temp = os.path.normpath(C.TEST_DATA_DIR + TEMP_LIBRARY_SAVE_FILE)
    shutil.copyfile(test_library_file_valid, test_library_file_temp)
    test_library = Library(test_library_file_temp)
    test_library.save_library()


""" You can record new tests from command line with "./library.py library.txt test_recording.txt"
    1. opy library.txt and test_recording.txt to test_data folder
    2. add them to the list recorded_library_test_files below
    3. next time you run pytest, your previous recording will be rerun. 
    You don't need to worry about returning the library file to the starting state. Go wild. 
"""
recorded_library_test_files = [
    ("test_library_10.txt", "test_library_10.recorded"),
    ("test_library_11.txt", "test_library_11.recorded"),
    ("test_library_12.txt", "test_library_12.recorded"),
    ("test_library_13.txt", "test_library_13.recorded"),
    ("test_library_14.txt", "test_library_14.recorded"),
    ("test_library_15.txt", "test_library_15.recorded"),
    ("test_library_16.txt", "test_library_16.recorded"),
]
@pytest.mark.parametrize("test_library_file, recorded_test_file", recorded_library_test_files)
def test_run_recorded_io(test_library_file, recorded_test_file):
    test_library_file = os.path.normpath(C.TEST_DATA_DIR + test_library_file)
    test_library_file_temp = os.path.normpath(C.TEST_DATA_DIR + TEMP_LIBRARY_SAVE_FILE)
    shutil.copyfile(test_library_file, test_library_file_temp)
    recorded_test_file = os.path.normpath(C.TEST_DATA_DIR + recorded_test_file)
    #temp_test_recording_file = os.path.normpath(C.TEST_DATA_DIR + TEMP_TEST_RECORDING_FILE)
    #shutil.copyfile(recorded_test_file, temp_test_recording_file)
    assert run_main(test_library_file_temp, recorded_test_file) == None



