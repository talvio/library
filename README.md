README Library - A python exercise in automated testing

A command line program with separated Model - Controller and View

Model: Library
Controller: Controller functions
View: UserInterface and InputOutputAndTest class


InputOutputAndTest captures all print and input commands from STDOUT and STDIN

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

The program itself is a simple library management program. 
