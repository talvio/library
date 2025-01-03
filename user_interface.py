from typing import Final
import os
import re
import shutil
from datetime import datetime
import library_constants as C
import time
from book import Book
from my_io import InputOutputAndTest
from book_api import google_books_api

ROWS_RESERVED_FOR_BOILERPLATE   = 6
RESERVED_FOR_COLUMN_GAPS        = 24

DEFAULT_TERMINAL_COLUMNS = 200
DEFAULT_TERMINAL_ROWS = 28

""" 1. User Interface class is the only way for the program to interact with the user.
    It separates the user view and input from 
    2. internal representation of the information in the Library class 
    3. The main loop of the program links the user view (1) and internal model (2)
"""
class UserInterface:
    def __init__(self, library = None, io_recording_file = None, run_recorded = False, record_additional_io = False, rerecord_output = False):
        self.library = library
        self.filter = None
        self.sort_column = C.TITLE_SORT
        self.reverse_sort = False
        self.view_list = []
        self.book_list_top_row_index = 0
        self.io = InputOutputAndTest(io_recording_file, run_recorded, record_additional_io, rerecord_output)
        self.books_fit_in_one_view = 1

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
        self.io.my_print("\n (A)uthor sort | (T)itle sort | (I)d sort | (Y)ear sort | (F)ilter | ENTER or Q = main menu.")
        self.io.my_print(" Book ID number to BORROW, RETURN, REMOVE and VIEW and EDIT all book details.") 
 
    def get_command(self, valid_commands, number_is_command = False, default_answer = "", question = " I am listening to your command: "):
        command = self.io.my_input(question) or default_answer
        while not command in valid_commands and (not re.match("^[1-9][0-9]*$", command) and number_is_command):
            command = self.io.my_input(question) or default_answer
        return command

    def print_book_detail_menu(self):
        self.io.my_print("\n           (B)orrow | (R)eturn | re(M)ove | (E)dit ")
        self.io.my_print(" (Q)uit = main menu | ENTER or (L)ist = back to book list\n")

    def ask_title(self, title):
        input_is_valid = False
        while not input_is_valid:
            if title != "":
                title = self.io.my_input(f"\nWhat is the name of the book [{title}]: ") or title
            else:
                title = self.io.my_input(f"\nWhat is the name of the book: ") 
            if title != "": input_is_valid = True
        return title

    def ask_author(self, author):
        input_is_valid = False
        while not input_is_valid:
            if author != "":
                author = self.io.my_input(f"\nWhat is the name of the author [{author}]: ") or author
            else:
                author = self.io.my_input(f"\nWhat is the name of the author: ")
            if author != "": input_is_valid = True
        return author

    def get_publication_year(self, publication_year):
        max_publication_year = datetime.now().year + 1
        input_is_valid = False
        while not input_is_valid:
            if publication_year != None and publication_year > 0 and publication_year <= max_publication_year: 
                input_is_valid = True
            else:
                self.io.my_print(f"\nValid publication year is between 1 and {max_publication_year}.")
            if publication_year != None and publication_year > 0:
                publication_year = self.io.my_input(f"\nWhat is the publication year [{publication_year}]: ") or publication_year
            else:
                publication_year = self.io.my_input(f"\nWhat is the publication year: ") 
            try:
                publication_year = int(publication_year)
            except:
                publication_year = None
        return publication_year

    def get_status(self, status):
        input_is_valid = False
        while not input_is_valid:
            if status != "":
                status = self.io.my_input(f"\nWhat is status of the book? \n 1 = Available\n 2 = Borrowed\n 3 = Unknown\n 4 = Removed\n Status [{status}]: ") or status
            else:
                status = self.io.my_input("\nWhat is status of the book? \n 1 = Available\n 2 = Borrowed\n 3 = Unknown\n 4 = Removed\n Status: ")
            if status == "1" or status == C.AVAILABLE:
                status = C.AVAILABLE
            elif status == "2" or status == C.BORROWED:
                status = C.BORROWED
            elif status == "3" or status == C.UNKNOWN:
                status = C.UNKNOWN
            elif status == "4" or status == C.REMOVED:
                status = C.REMOVED
            else:
                status = ""
            if status in C.VALID_STATUSES:
                input_is_valid = True
        return status

    def ask_book_information(self, book_isbn = C.ISBN_UNDEFINED, title = "", author = "", publication_year = C.YEAR_UNDEFINED, status = "", pages = None, description = None):
        book_data_valid = False
        while not book_data_valid:
            os.system('clear')
            title = self.ask_title(title)
            author = self.ask_author(author)
            google_books = google_books_api(title, author)
            if google_books != [] and google_books[0] != None:
                book_isbn, title, author, publication_year, status, pages, description = self.select_book(
                    google_books, 
                    book_isbn, 
                    title, 
                    author,
                    publication_year, 
                    status, 
                    pages, 
                    description
                )
            publication_year = self.get_publication_year(publication_year)
            status = self.get_status(status)

            os.system('clear')
            self.io.my_print(f"\n                 Book title: {title}")
            self.io.my_print(f" Book status in the library: {status}")
            self.io.my_print(f"      Book publication year: {publication_year}")
            self.io.my_print(f"                Book author: {author}")
            self.io.my_print(f"                      Pages: {pages}")
            self.io.my_print(f"                       ISBN: {book_isbn}\n")
            self.io.my_print(f"                Description: {description}\n")
            user_accepts_data = self.io.my_input("  (R)e-enter | (A)ccept |  (C)ancel \n\n  I am listening to your command [R]: ") or C.REENTER[0]
            if user_accepts_data in C.ACCEPT: 
                book_data_valid = True
            if user_accepts_data in C.CANCEL: 
                book_data_valid = True
                title, author, publication_year, status = None, None, None, None 
        return book_isbn, title, author, publication_year, status, pages, description
    
    """ Asks the user how to filter the book list. 
        If the user gives an empty filter string, the book list is shown in full sorted according to the title. 
        Note: If the view was already previously filtered, the new filter can be applied to the already 
        filtered view, not the whole content of the library. This may or may not be desired in the future. 
    """
    def get_filter(self):
        self.filter =  self.io.my_input("\n What words shall I use to filter the titles or authors for you: ") or None

    """ Applies the self.filter regular expression and filters the only the books where self.filter 
        rep is found either in the book title or the author name. 
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
    def book_sort(self, column = None, reverse_sort=None):
        if reverse_sort == None: 
            reverse_sort = self.reverse_sort
        else:
            self.reverse_sort = reverse_sort
        if column != None:
            self.sort_column = column
        if self.sort_column == None:
            self.sort_column = C.TITLE
        match self.sort_column:
            case C.TITLE_SORT:
                def book_sort_title(item):return item.title
                self.view_list.sort(key=book_sort_title)
            case C.AUTHOR_SORT:
                def book_sort_author(item):return item.author
                self.view_list.sort(key=book_sort_author)
            case C.BOOK_ID_SORT:
                def book_sort_book_id(item):return item.book_id
                self.view_list.sort(key=book_sort_book_id)
            case C.YEAR_SORT:
                def book_sort_publication_year(item):return item.publication_year
                self.view_list.sort(key=book_sort_publication_year)
        if reverse_sort:
            self.view_list.reverse()
        self.book_list_top_row_index = 0

    """ Sorts self.view_list using the book titles 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def title_sort(self, reverse_sort=None):
        self.book_sort(C.TITLE_SORT, reverse_sort)

    """ Sorts self.view_list using the author names 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def author_sort(self, reverse_sort=None):
        self.book_sort(C.AUTHOR_SORT, reverse_sort)

    """ Sorts self.view_list using the book_id 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def book_id_sort(self, reverse_sort=None):
        self.book_sort(C.BOOK_ID_SORT, reverse_sort)

    """ Sorts self.view_list using the publication_year 
        self.view_list is a list referring to all or some of the books in 
        self.library.all_books 
    """
    def publication_year_sort(self, reverse_sort=None):
        self.book_sort(C.YEAR_SORT, reverse_sort)

    """ Lists books from the library which may or may not be filtered. 
        The filter is stored in self.filter
        The filtered and sorted book list is in self.view_list
    """
    def list_books(self):
        if C.PYTEST_RUNNING or self.io.run_recorded:
            books_fit_in_one_view = DEFAULT_TERMINAL_ROWS - ROWS_RESERVED_FOR_BOILERPLATE    
            column_space_for_books   = DEFAULT_TERMINAL_COLUMNS - RESERVED_FOR_COLUMN_GAPS    
        else:
            books_fit_in_one_view = os.get_terminal_size()[1] - ROWS_RESERVED_FOR_BOILERPLATE
            column_space_for_books   = os.get_terminal_size()[0] - RESERVED_FOR_COLUMN_GAPS
        self.books_fit_in_one_view = books_fit_in_one_view
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
            book = self.library.book_id_to_book(book_id)
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
        book_record += f"           Pages: {book.pages}\n"
        book_record += f"            ISBN: {book.isbn}\n\n"
        book_record += f"     Description: {book.description}\n\n"
        self.io.my_print(book_record)
        return book

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
        elif book.status != C.AVAILABLE:
            self.io.my_print("\n This book is currently not available and cannot be borrowed!")
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
        do_return = "No answer"
        while not do_return in C.YES + C.NO + C.CANCEL:
            do_return = self.io.my_input(" Do you want to mark this book as returned? (Y)es or (N)o ", C.CANCEL)
        if do_return in C.YES:
            return book
        return None

    """ Ask if the user wants to return the borrowed book. 
        Return reference to the book if successful and user says Yes. 
        Otherwise return None.
    """
    def remove_book_id(self, book_id = None):
        book = self.show_book_details(book_id)
        if book == None:
            return
        if book.status == C.REMOVED:
            self.io.my_print("\n This book is already removed. Logic dictates it cannot be removed twice.")
            self.io.my_print("\n If there is an error in the book information, please edit the book data.")
            time.sleep(C.MESSAGE_FLASH_TIME)
            return
        do_remove = "No answer"
        while not do_remove in C.YES + C.NO + C.CANCEL:
            do_remove = self.io.my_input(" Do you want to mark this book as removed from the library? (Y)es or (N)o ", C.CANCEL)
        if do_remove in C.YES:
            return book
        return None

    """ The first time you start the program, it asks if the location of the library file is acceptable. 
        If not, the program exits. To change the location of the library file, edit library_constants.py
    """
    def approve_creating_library_file(self, library_file):
        os.system('clear')
        self.io.my_print(f"Hi!\n\nLibrary file {library_file} does not exist yet.\n\n")
        user_accepts_library_file = self.io.my_input("Press ENTER to exit. y + enter to create an empty library file: ", C.NO[0]) 
        os.system('clear')
        if user_accepts_library_file in C.YES:
            return True
        else:
            self.io.my_print("To change the location of the library file, edit library_constants.py")
            self.io.my_input("Press ENTER to exit. ") or "continue"


    def search_google_books(self):
        self.io.my_print("\n Would you like to search for the book and more details about it in Google's book database?")
        do_search = "No answer"
        while not do_search in C.YES + C.NO + C.CANCEL:
            do_search = self.io.my_input(" (Y)es or (No) [No]: ", C.NO)
        if do_search in C.YES:
            return True
        return False


    """ Each item in book_list is a lists containing details of a book in this order from [0] to [10]:
        title, subtitle, author, publishing_year, page_count, print_type, categories, language, isbn10, isbn13, description 
        The default values are returned if the user cancels and does not choose any of the books in book_list
        The default values are also used as the first book in the list unless the default values are None. 
    """
    def select_book(
        self, 
        book_list = None, 
        default_isbn = None, 
        default_title = None, 
        default_author = None, 
        default_publication_year = None, 
        default_status = None, 
        default_pages = None, 
        default_description = None
    ):
        row_number = 0
        if default_title != None:
            row_number += 1
            self.io.my_print("\nWhat you have previously entered as the book information.\n")
            self.io.my_print(f"   {row_number} {default_author} ({default_publication_year}): {default_title}, {default_pages} pages")
        self.io.my_print("\nFollowing books in Google books database match your title and author.")
        self.io.my_print("Which one do you wish to list in the library.\n")
        for book in book_list:
            row_number += 1
            book_isbn = book[8]
            if book[9] is not None: book_isbn = book[9]
            self.io.my_print(f"   {row_number} {book[2]} ({book[3]}) {book_isbn}: {book[0]}, {book[4]} pages")
            
        book_selection = self.get_command(C.CANCEL, number_is_command = True, default_answer = "1", question = "\nGive a number or (C)ancel: ")
        if book_selection in C.CANCEL or book_selection == "1":
            return default_isbn, default_title, default_author, default_publication_year, default_status, default_pages, default_description
        else:
            book_selection = int(book_selection) - 2
            book = book_list[book_selection]
            return book[9], book[0], book[2], book[3], default_status, book[4], book[10]
