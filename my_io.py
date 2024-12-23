import library_constants as C
import time
import difflib
import os

IO_RECORDING_FILE = C.TEST_DATA_DIR + "my_io_recorded"

RUN_RECORDED_SESSION = True
RECORD_ADDITIONAL_IO = False
RERECORD_OUTPUT = False
#THIS_IS_A_TEST = False

my_input_fifo = []
my_observed_output = [""]
my_recorded_output = [""]

if "PYTEST_VERSION" in os.environ:
    STEP_DELAY = 0
else:
    STEP_DELAY = 1


""" InputOutputAndTest captures all print and input commands. 
    For testing, it can 
    1. record all inputs and outputs to a file io_recording_file when record_additional_io = True
       If there was already previous session recorded to that file, this will append additional IO to the end of the file
    2. When run_recorded = True, rather than ask the user for input, the InputOutputAndTest will run the previous recorded
       session from io_recording_file and compare to the output in that previous recording. If the output does not match, 
       it will result in a RuntimeError. If record_additional_io = True and the previous session does not end in program exit, 
       user can continue recording more.
    3. When the program changes and the previously recorded output no longer matches the recorded output, you can set 
       rerecord_output = True and re-record the output with the previous session inputs. Then you can naturally use the new
       output for testing again, set erecord_output = False and run_recorded = True

    All of this makes testing the UserInterface code with pytest possible. 
    You can have several library_file and io_recording_file combinations to divide testing the program to smaller and different
    test sessions. Rerunning them automatically after every change is then trivial. 

    The recording file format is simple. Every input starts with I: Every following output line starts with O: and is a reaction 
    to the previous input up to the next input line, starting with I: again. 
"""
class InputOutputAndTest:

    def __init__(self, io_recording_file = IO_RECORDING_FILE, run_recorded = RUN_RECORDED_SESSION, record_additional_io = RECORD_ADDITIONAL_IO, rerecord_output = RERECORD_OUTPUT):
        self.io_recording_file = io_recording_file
        self.run_recorded = run_recorded
        self.record_additional_io = record_additional_io
        self.rerecord_output = rerecord_output

        self.my_input_fifo = []
        self.my_observed_output = [""]
        self.my_recorded_output = [""]

        if self.run_recorded:
            self.load_recorded_io()
        if self.rerecord_output:
            self.restart_recording_file()

    def load_recorded_io(self):
        if not os.path.isfile(self.io_recording_file): 
            with open(self.io_recording_file, 'w') as f:
                f.close
        with open(self.io_recording_file, 'r') as f:
            line = None
            line = f.readline()
            while line != "":
                line_no_eol = line[:-1]
                if line_no_eol[0] == "I":
                    self.my_input_fifo.append(line_no_eol[2:])
                    self.my_recorded_output.append("")
                elif line_no_eol[0] == "O": 
                    self.my_recorded_output[-1] += line_no_eol[2:] + "\n"
                else:
                    raise RuntimeError("Recorded IO file is corrupted!")
                line = f.readline()       
        f.close
        
    def restart_recording_file(self):
        with open(self.io_recording_file, 'w') as f:
            f.close

    def my_print(self, string = ""):
            print(string)
            self.my_observed_output[-1] += string + "\n"
            if (self.record_additional_io and self.my_input_fifo == []) or self.rerecord_output:
                string = string.replace("\n","\nO:")
                with open(self.io_recording_file, 'a', encoding="utf-8") as f:
                    f.write("O:" + string + "\n")
                f.close

    def compare_output(self):
        latest_recorded_output = self.my_recorded_output.pop(0)
        if latest_recorded_output != self.my_observed_output[-2]:
            print("OUTPUT does not match RECORDED output!")
            print("Difference: \n")
            difference_all = difflib.ndiff(latest_recorded_output.splitlines(keepends=True), self.my_observed_output[-2].splitlines(keepends=True))
            difference_to_show = ""
            for diff in difference_all:
                if diff[:2] != "  ":
                    print("Line: " + diff, end="")
                    difference_to_show += diff
            raise RuntimeError(f"Output does not match recorded output!\nDIFFERENCE:\n{difference_to_show}\nRECORDED:\n{latest_recorded_output}\nOBSERVED:\n{self.my_observed_output[-2]}")

    def my_input(self, question = "", default_input = (None, None)):
        self.my_observed_output[-1] = self.my_observed_output[-1] + question + "\n"
        self.my_observed_output.append("")
        if (self.rerecord_output or self.run_recorded) and self.my_input_fifo != []:
            if not self.rerecord_output: 
                self.compare_output()
            recorded_input = self.my_input_fifo.pop(0)
            print(question + recorded_input)
            time.sleep(STEP_DELAY)
            answer = recorded_input
        else:
            if default_input == (None, None):
                answer =  input(question)
            else:
                answer =  input(question) or default_input
        question = question.replace("\n","\nO:")
        if (self.record_additional_io and self.my_input_fifo == []) or self.rerecord_output:
            with open(self.io_recording_file, 'a', encoding="utf-8") as f:
                f.write("O:" + question + "\n")
                f.write("I:" + answer + "\n")
            f.close
        return answer

"""
def my_print(string = ""):
    print(string)
    my_observed_output[-1] += string + "\n"
    if (RECORD_ADDITIONAL_IO and my_input_fifo != []) or RERECORD_OUTPUT:
        string = string.replace("\n","\nO:")
        with open(io_recording_file, 'a', encoding="utf-8") as f:
            f.write("O:" + string + "\n")
        f.close

def compare_output():
    latest_recorded_output = my_recorded_output.pop(0)
    if latest_recorded_output != my_observed_output[-2]:
        print("OUTPUT does not match RECORDED output!")
        print("Difference: \n")
        difference_all = difflib.ndiff(latest_recorded_output.splitlines(keepends=True), my_observed_output[-2].splitlines(keepends=True))
        difference_to_show = ""
        for diff in difference_all:
            if diff[:2] != "  ":
                print("Line: " + diff, end="")
                difference_to_show += diff
        raise RuntimeError(f"Output does not match recorded output!\nDIFFERENCE:\n{difference_to_show}\nRECORDED:\n{latest_recorded_output}\nOBSERVED:\n{my_observed_output[-2]}")
        
def my_input(question = "", default_input = (None, None)):
    my_observed_output[-1] = my_observed_output[-1] + question + "\n"
    my_observed_output.append("")
    if (RERECORD_OUTPUT or RUN_RECORDED_SESSION) and my_input_fifo != []:
        if not RERECORD_OUTPUT: 
            compare_output()
        recorded_input = my_input_fifo.pop(0)
        print(question + recorded_input)
        time.sleep(STEP_DELAY)
        answer = recorded_input
    else:
        if default_input == (None, None):
            answer =  input(question)
        else:
            answer =  input(question) or default_input
    question = question.replace("\n","\nO:")
    if RECORD_ADDITIONAL_IO or RERECORD_OUTPUT:
        with open(io_recording_file, 'a', encoding="utf-8") as f:
            f.write("O:" + question + "\n")
            f.write("I:" + answer + "\n")
        f.close
    return answer

if RUN_RECORDED_SESSION:
    with open(io_recording_file, 'r') as f:
        line = None
        line = f.readline()
        while line != "":
            line_no_eol = line[:-1]
            if line_no_eol[0] == "I":
                my_input_fifo.append(line_no_eol[2:])
                my_recorded_output.append("")
            elif line_no_eol[0] == "O": 
                my_recorded_output[-1] += line_no_eol[2:] + "\n"
            else:
                raise RuntimeError("Recorded IO file is corrupted!")
            line = f.readline()       
    f.close

    if RERECORD_OUTPUT:
        with open(io_recording_file, 'w') as f:
            f.close
"""

