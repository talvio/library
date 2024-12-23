from typing import Final
import os
import re
import shutil
from datetime import datetime
import library_constants as C
import time
from book import Book
#from my_io import self.io.my_input, self.io.my_print
from my_io import InputOutputAndTest

ROWS_RESERVED_FOR_BOILERPLATE   = 6
RESERVED_FOR_COLUMN_GAPS        = 24

DEFAULT_TERMINAL_COLUMNS = 200
DEFAULT_TERMINAL_ROWS = 52

""" 1. User Interface class is the only way for the program to interact with the user.
    It separates the user view and input from 
    2. internal representation of the information in the Library class 
    3. The main loop of the program links the user view (1) and internal model (2)
"""
class UserInterface:
    def __init__(self, library = None, io_recording_file = None, run_recorded = False, record_additional_io = False, rerecord_output = False):
        self.library = library
        self.filter = None
        self.sort_column = "Title"
        self.view_list = []
        self.book_list_top_row_index = 0
        self.io = InputOutputAndTest(io_recording_file, run_recorded, record_additional_io, rerecord_output)
        try:
            books_fit_in_one_view = os.get_terminal_size()[1] - ROWS_RESERVED_FOR_BOILERPLATE
        except:
            books_fit_in_one_view = DEFAULT_TERMINAL_ROWS - ROWS_RESERVED_FOR_BOILERPLATE

    """ The menu numbers are slightly changed from the given assignment. 
    0 is save and exit so that it is the easy first choice. 
    I have added the command for removing a book from the library. 
    I could have split borrowing and returning a book in the main menu, but I 
    kept your combined selection from the assignment. I thought maybe you want 
    to see that I handle the combined case nicely later in the code. 
    """

    def main_menu_command(self):
        command = None
        while command not in range(0,6):
            os.system('clear')
            self.io.my_print("\n=== Library Manager ===")
            self.io.my_print("0. Save and Exit")
            self.io.my_print("1. Add Book")
            self.io.my_print("2. List All Books")
            self.io.my_print("3. Search Books")
            self.io.my_print("4. Borrow/Return Book")
            self.io.my_print("5. Remove book from the library\n")
            command = self.io.my_input("I am listening to your command: ")
            try:
                command = int(command)
            except:
                command = None
        return command 

    def print_book_list_menu(self):
        self.io.my_print("\n (A)uthor sort | (T)itle sort | (I)d sort | (F)ilter | ENTER or Q = main menu.")
 
    def get_command(self, valid_commands, number_is_command = False, default_answer = "", question = " I am listening to your command: "):
        command = self.io.my_input(question) or default_answer
        while not command in valid_commands and (not re.match("^[1-9][0-9]*$", command) and number_is_command):
            command = self.io.my_input(question) or default_answer
        return command

    def print_book_detail_menu(self):
        self.io.my_print("\n           (B)orrow | (R)eturn | re(M)ove | (E)dit ")
        self.io.my_print(" (Q)uit = main menu | ENTER or (L)ist = back to book list\n")

    def ask_book_information(self, title = "", author = "", publication_year = C.YEAR_UNDEFINED, status = ""):
        book_data_valid = False
        while not book_data_valid:
            os.system('clear')
            input_is_valid = False
            while not input_is_valid:
                if title != "":
                    title = self.io.my_input(f"\nWhat is the name of the book [{title}]: ") or title
                else:
                    title = self.io.my_input(f"\nWhat is the name of the book: ") 
                if title != "": input_is_valid = True
            input_is_valid = False
            while not input_is_valid:
                if author != "":
                    author = self.io.my_input(f"\nWhat is the name of the author [{author}]: ") or author
                else:
                    author = self.io.my_input(f"\nWhat is the name of the author: ")
                if author != "": input_is_valid = True
            max_publication_year = datetime.now().year + 1
            input_is_valid = False
            while not input_is_valid:
                self.io.my_print(f"\nValid publication year is between 1 and {max_publication_year}.\n")
                if publication_year > 0:
                    publication_year = self.io.my_input(f"What is the publication year [{publication_year}]: ") or publication_year
                else:
                    publication_year = self.io.my_input(f"What is the publication year: ") 
                try:
                    publication_year = int(publication_year)
                except:
                    publication_year = 0
                if publication_year > 0 and publication_year <= max_publication_year: input_is_valid = True
            input_is_valid = False
            while not input_is_valid:
                if status != "":
                    status = self.io.my_input(f"\nWhat is status of the book? \n 1 = Available\n 2 = Borrowed\n 3 = Unknown\n Status [{status}] :") or status
                else:
                    status = self.io.my_input("\nWhat is status of the book? \n 1 = Available\n 2 = Borrowed\n 3 = Unknown\n Status: ")
                if status == "1" or status == C.AVAILABLE:
                    status = C.AVAILABLE
                elif status == "2" or status == C.BORROWED:
                    status = C.BORROWED
                elif status == "3" or status == C.UNKNOWN:
                    status = C.UNKNOWN
                else:
                    status = ""
                if status in C.VALID_STATUSES:
                    input_is_valid = True
            os.system('clear')
            self.io.my_print(f"\n                 Book title: {title}")
            self.io.my_print(f" Book status in the library: {status}")
            self.io.my_print(f"      Book publication year: {publication_year}")
            self.io.my_print(f"                Book author: {author}\n")
            user_accepts_data = self.io.my_input("  (R)e-enter | (A)ccept |  (C)ancel \n\n  I am listening to your command [R]: ") or C.REENTER[0]
            if user_accepts_data in C.ACCEPT: 
                book_data_valid = True
            if user_accepts_data in C.CANCEL: 
                book_data_valid = True
                C.ISBN_UNDEFINED, title, author, publication_year, status = None, None, None, None, None 
        return C.ISBN_UNDEFINED, title, author, publication_year, status
    
    """ Asks the user how to filter the book list. 
        If the user gives an empty filter string, the book list is shown in full sorted according to the title. 
        Note: If the view was already previously filtered, the new filter can be applied to the already 
        filtered view, not the whole content of the library. This may or may not be desired in the future. 
    """
    def get_filter(self):
        self.filter =  self.io.my_input("\n What words shall I use to filter the titles or authors for you: ") or None

    """ Applies the self.filter regular expression and filters the only the books where self.filter 
        regexp is found either in the book title or the author name. 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def apply_filter(self):
        self.view_list = list(self.library.all_books)
        self.book_list_top_row_index = 0
        if self.filter == None:
            return
        new_view_list = []
        book_filter = re.compile(self.filter, re.IGNORECASE)
        for view_item in self.view_list:
            if (book_filter.search(view_item.title) or 
                book_filter.search(view_item.author)):
                new_view_list.append(view_item)
        self.view_list = new_view_list

    """ Sorts self.view_list using title, author or id
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def book_sort(self, column = None):
        if column != None:
            self.sort_column = column
        if self.sort_column == None:
            self.sort_column = "Title"
        match self.sort_column:
            case "Title":
                def book_sort_title(item):return item.title
                self.view_list.sort(key=book_sort_title)
            case "Author":
                def book_sort_author(item):return item.author
                self.view_list.sort(key=book_sort_author)
            case "Book_id":
                def book_sort_book_id(item):return item.book_id
                self.view_list.sort(key=book_sort_book_id)
        self.book_list_top_row_index = 0

    """ Sorts self.view_list using the book titles 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def title_sort(self):
        self.book_sort("Title")

    """ Sorts self.view_list using the author names 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def author_sort(self):
        self.book_sort("Author")

    """ Sorts self.view_list using the book_id 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def book_id_sort(self):
        self.book_sort("Book_id")

    """ Lists books from the library which may or may not be filtered. 
        The filter is stored in self.filter
        The filtered and sorted book list is in self.view_list
    """
    def list_books(self):
        try:
            books_fit_in_one_view = os.get_terminal_size()[1] - ROWS_RESERVED_FOR_BOILERPLATE
        except:
            books_fit_in_one_view = DEFAULT_TERMINAL_ROWS - ROWS_RESERVED_FOR_BOILERPLATE
        self.books_fit_in_one_view = books_fit_in_one_view
        try:
            column_space_for_books   = os.get_terminal_size()[0] - RESERVED_FOR_COLUMN_GAPS
        except:
            column_space_for_books   = DEFAULT_TERMINAL_COLUMNS - RESERVED_FOR_COLUMN_GAPS
        longest_title = 0
        longest_author = 0

        if self.view_list == []: 
            if self.filter != None:
                os.system('clear')
                self.io.my_input("\n  No matches for the given filter.\n\n  Press any key to cancel filtering. ")
                self.filter = None
                self.apply_filter()
                self.title_sort()

        for book in self.library.all_books:
            if len(book.title) > longest_title: longest_title = len(book.title)
            if len(book.author) > longest_author: longest_author = len(book.author)

        extra_space = column_space_for_books - (longest_title + longest_author)
        if extra_space < 0:
            title_author_length_fraction = longest_title / (longest_author + longest_title)
            longest_title  += round(extra_space * title_author_length_fraction)
            longest_author += round(extra_space * (1 - title_author_length_fraction))

        if type(self.book_list_top_row_index) != int or self.book_list_top_row_index < 0 or self.book_list_top_row_index >= len(self.view_list):
            self.book_list_top_row_index = 0
        books_shown_on_terminal = 0
        book_records = ""
        top_row_index = 0
        for view_item in self.view_list:
            book_record = f"{view_item.book_id} |".rjust(9)
            book_record += f"{view_item.status[:1]}| "
            book_record += view_item.title[:longest_title] + " | ".rjust(longest_title - len(view_item.title) + 3)
            book_record += f"{view_item.publication_year}".rjust(4) + " | "
            book_record += view_item.author[:longest_author] + " |".rjust(longest_author - len(view_item.author) + 2)
            if (self.book_list_top_row_index == top_row_index or books_shown_on_terminal > 0) and books_shown_on_terminal < books_fit_in_one_view:
                book_records += book_record + "\n"
                books_shown_on_terminal += 1
            if books_shown_on_terminal == 0:
                top_row_index += 1
        book_records = book_records[:-1]
        bottom_row_index = top_row_index + books_fit_in_one_view - 1
        if bottom_row_index >= len(self.view_list): bottom_row_index = len(self.view_list) - 1
        what_is_shown = f"{top_row_index + 1}-{bottom_row_index + 1} of {len(self.view_list)}"
        title_line  = f"BOOK ID |S| TITLE"
        title_line += f"(U)p (D)own {what_is_shown} |".rjust(longest_title-3)
        title_line += " YEAR | AUTHOR"
        title_line += "|".rjust(longest_author-4)
        os.system('clear')
        self.io.my_print(title_line)
        self.io.my_print(book_records)
        if self.filter:
            self.io.my_print(f"            -> FILTER: {self.filter}" +  " | ".rjust(longest_title - len(self.filter) - 8))

    """ Show details of a book which has the library book id given
        If book id is out of range, return False. Otherwise, return True. 
    """
    def show_book_details(self, book_id):
        if type(book_id) == str or type(book_id) == int:
            book = self.book_id_to_book(book_id)
        elif isinstance(book_id, Book):
            book = book_id
        else:
            book = None
        if book == None:
            return None
        os.system('clear')
        book_record  = f" Book library id: {book.book_id}\n"
        book_record += f"     Book status: {book.status}\n"
        book_record += f"      Book title: {book.title}\n"
        book_record += f"Publication year: {book.publication_year}\n"
        book_record += f"          Author: {book.author}\n"
        self.io.my_print(book_record)
        return book

    """ The user knows the ID of the book in the library and uses this ID in the UI to identify the book. 
        This method returns a reference to the Book with that book_id in the library.
    """
    def book_id_to_book(self, book_id):
        book_index = int(book_id) - 1
        if book_index < 0 or book_index >= len(self.library.all_books):
            return None
        return self.library.all_books[book_index]

    """ Display details of the given book_id. 
        Check if it is available and if it is, allow it to be marked as borrowed. 
    """
    def borrow_book_id(self, book_id = None):
        book = self.show_book_details(book_id)
        if book == None:
            return
        if book.status == C.BORROWED:
            self.io.my_print("\n This book is already borrowed!")
            time.sleep(C.MESSAGE_FLASH_TIME)
            return
        do_borrow = "No answer"
        while not do_borrow in C.YES + C.NO + C.CANCEL:
            do_borrow = self.io.my_input(" Do you want to mark this book as borrowed? (Y)es or (N)o ", C.CANCEL)
        if do_borrow in C.YES:
            return book
        return None

    def flash_book_details_and_message(self, book_id, message):
        book = self.show_book_details(book_id)
        if book == None:
            return
        self.io.my_print(message)
        time.sleep(C.MESSAGE_FLASH_TIME)
            
    """ Ask if the user wants to return the borrowed book. 
        Return reference to the book if successful and user says Yes. 
        Otherwise return None.
    """
    def return_book_id(self, book_id = None):
        book = self.show_book_details(book_id)
        if book == None:
            return
        if book.status != C.BORROWED:
            self.io.my_print("\n This book is NOT borrowed! Logic dictates it cannot be returned.")
            self.io.my_print("\n If there is an error in the book information, please edit the book data.")
            time.sleep(C.MESSAGE_FLASH_TIME)
            return
        do_borrow = "No answer"
        while not do_borrow in C.YES + C.NO + C.CANCEL:
            do_borrow = self.io.my_input(" Do you want to mark this book as returned? (Y)es or (N)o ", C.CANCEL)
        if do_borrow in C.YES:
            return book
        return None

    """ The first time you start the program, it asks if the location of the library file is acceptable. 
        If not, the program exits. To change the location of the library file, edit library_constants.py
    """
    def approve_creating_library_file(self, library_file):
        os.system('clear')
        self.io.my_print(f"Hi!\n\nLibrary file {library_file} does not exist yet.\n\n")
        user_accepts_library_file = self.io.my_input("Press ENTER to exit. y + enter to create an empty library file: ") or "n"
        os.system('clear')
        if user_accepts_library_file in C.YES:
            return True
        else:
            self.io.my_print("To change the location of the library file, edit library_constants.py")
            self.io.my_input("Press ENTER to exit. ") or "continue"

