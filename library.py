#!/usr/bin/env python3 

from typing import Final
import os
import re
import shutil
import time
import sys
import filecmp

import library_constants as C
from user_interface import UserInterface
from book import Book

""" The class Library containing the books in a class variable "all_books". It's a list type. 
    Information about books added to the library are never complitely removed. Their status
    can be changed to "removed", but information also about removed books are kept.
    In this way the book index and the list index match, except the library index starts from 1, 
    not 0. 
"""
class Library:

    """ Class initiator reads the library from the library file.
    """
    def __init__(self, library_file = None):
        self.all_books: list[Book] = []
        if library_file != None: 
            self.library_file = library_file
        else:
            self.library_file: Final = os.path.normpath(C.LIBRARY_DIR + C.LIBRARY_FILE)
        if not os.path.isfile(self.library_file): self.save_library()
        self.load_library(library_file)

    def load_library(self, library_file):
        book_index = 0
        field_name = None
        isbn, title, author, publication_year, status, line, book_id, pages, description = C.ISBN_UNDEFINED, None, None, None, None, None, None, None, None
        line_number = 0
        with open(self.library_file, 'r') as f:
            while line != "":
                line = f.readline()
                line_number += 1
                if line.strip():
                    previous_field_name = field_name
                    line = line.strip()
                    field_name = line.split()[0]
                    if field_name != "BOOK:" and book_id == None:
                        raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. BOOK: tag is missing.")
                    match field_name:
                        case "BOOK:":
                            if title != None or author != None or publication_year != None or status != None:
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. BOOK_END tag is missing.")
                            book_index += 1
                            try:
                                book_id = int(line.split()[1])
                            except:
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Book number is missing.")
                            if book_index != book_id: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Wrong book id: {book_id}.")
                        case "Title:":
                            if title != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two title lines.")
                            title = line.removeprefix("Title: ")
                        case "Author:":
                            if author != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two author lines.")
                            author = line.removeprefix("Author: ")
                        case "Year:":
                            if publication_year != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two publication years.")
                            publication_year = line.removeprefix("Year:   ")
                            publication_year = int(publication_year)
                        case "Status:":
                            if status != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two statuses.")
                            status = line.removeprefix("Status: ")
                        case "ISBN:":
                            if isbn != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two ISBNs.")
                            isbn = line.removeprefix("ISBN: ")
                        case "Pages:":
                            if pages != None: 
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Found two page counts.")
                            pages = line.removeprefix("Pages: ")
                        case "Description:":
                            if description == None: 
                                description = line.removeprefix("Description: ")
                            else:
                                description += "\n" + line.removeprefix("Description: ")
                        case "BOOK_END":
                            if title == None or author == None or publication_year == None or status == None:
                                raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Mandatory book information is missing.")
                            book = Book(isbn, book_id, title, author, publication_year, status, pages, description)
                            self.all_books.append(book)
                            isbn, title, author, publication_year, status, line, book_id, pages, description = C.ISBN_UNDEFINED, None, None, None, None, None, None, None, None
                        case _:
                            raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. Line begin tag is missing.")
                elif line != "":
                    raise RuntimeError(f"Library file is corrupted at line {line_number}. Line is empty.")
        if title != None or author != None or publication_year != None or status != None:
            raise RuntimeError(f"Library file is corrupted for the book number {book_index} and line {line_number}. BOOK_END tag is missing from the end of the file.")
        f.close()

    """ Add a new book to the library and append it to the library file. 
        New books are always appended to the library file. 
    """
    def add_book(self, book):
        books_in_library = len(self.all_books)
        books_in_library += 1
        book.book_id = books_in_library
        self.all_books.append(book)
        book_record = f"BOOK: {book.book_id}\nTitle:  {book.title}\nAuthor: {book.author}\nYear:   {book.publication_year}\nStatus: {book.status}\nBOOK_END\n"
        f = open(self.library_file, 'a', encoding="utf-8")
        f.write(book_record)
        f.close


    """ Move old library file to a backup file.
        Write new library file with the fresh library data.
    """
    def save_library(self):
        if os.path.isfile(self.library_file):
            shutil.copyfile(self.library_file, self.library_file + ".backup")
        with open(self.library_file, 'w', encoding="utf-8") as f:
            book_index = 0
            for book in self.all_books:
                book_index += 1
                book_record = f"BOOK: {book_index}\n"
                book_record += f"Title: {book.title}\nAuthor: {book.author}\nYear:   {book.publication_year}\nStatus: {book.status}\n"
                if book.isbn != C.ISBN_UNDEFINED: book_record += f"ISBN: {book.isbn}\n"
                if book.pages != None: book_record += f"Pages: {book.pages}\n"
                if book.description != None: book_record += f"Description: {book.description}\n"
                book_record += f"BOOK_END\n"
                f.write(book_record)
        f.close

    """ The user knows the ID of the book in the library and uses this ID in the UI to identify the book. 
        This method returns a reference to the Book with that book_id in the library.
    """
    def book_id_to_book(self, book_id):
        book_index = int(book_id) - 1
        if book_index < 0 or book_index >= len(self.all_books):
            return None
        return self.all_books[book_index]

""" Controls actions when displaying book details. 
"""
def book_details_control(library, user_interface, book_id):
    if not user_interface.show_book_details(book_id):
        return
    user_interface.print_book_detail_menu()
    next_command = user_interface.get_command(C.VALID_BOOK_DETAIL_COMMAND, False, default_answer = "List", question = " I am listening to your command: ")
    if next_command in C.BORROW:
        book = user_interface.borrow_book_id(book_id)
        if book != None: 
            book.status = C.BORROWED
            user_interface.flash_book_details_and_message(book, "\n Your keyboard is my master!")
    elif next_command in C.RETURN:
        book = user_interface.return_book_id(book_id)
        if book != None: 
            book.status = C.AVAILABLE
            user_interface.flash_book_details_and_message(book, "\n Your keyboard is my master!")
    elif next_command in C.EDIT:
        book = library.book_id_to_book(book_id)
        if book != None:
            (
                new_isbn, 
                new_title, 
                new_author, 
                new_publication_year, 
                new_status, 
                new_pages, 
                new_description
            ) = user_interface.ask_book_information(
                book.isbn,
                book.title, 
                book.author, 
                book.publication_year, 
                book.status, 
                book.pages, 
                book.description
            )
            if new_title != None:
                book.isbn, book.title, book.author, book.publication_year, book.status, book.pages, book.description = new_isbn, new_title, new_author, new_publication_year, new_status, new_pages, new_description
            user_interface.flash_book_details_and_message(book, "\n Your keyboard is my master!")
    elif next_command in C.REMOVE:
        book = user_interface.remove_book_id(book_id)
        if book != None: 
            book.status = C.REMOVED
            user_interface.flash_book_details_and_message(book, "\n Your keyboard is my master!")
    return next_command

""" Controls actions when displaying book list, filtered or full. 
    The list does not need to fit on the screen. 
    User can use (u)p and (d)own to scroll.
"""
def book_list_control(library, user_interface, command = None):
    user_interface.view_list = list(user_interface.library.all_books)
    user_interface.filter = None
    user_interface.title_sort()
    while not command in C.QUIT:
        user_interface.list_books()
        user_interface.print_book_list_menu()
        if command == None:
            command = user_interface.get_command(
                C.VALID_BOOK_LIST_COMMAND, 
                number_is_command = True, 
                default_answer = "q", 
                question = " I am listening to your command: ")
        if command in C.AUTHOR:
            if user_interface.sort_column == C.AUTHOR_SORT:
                user_interface.reverse_sort = not user_interface.reverse_sort
            else:
                user_interface.reverse_sort = False
            user_interface.author_sort()
        elif command in C.TITLE:
            if user_interface.sort_column == C.TITLE_SORT:
                user_interface.reverse_sort = not user_interface.reverse_sort
            else:
                user_interface.reverse_sort = False
            user_interface.title_sort() 
        elif command in C.ID:
            if user_interface.sort_column == C.BOOK_ID_SORT:
                user_interface.reverse_sort = not user_interface.reverse_sort
            else:
                user_interface.reverse_sort = False
            user_interface.book_id_sort() 
        elif command in C.YEAR:
            if user_interface.sort_column == C.YEAR_SORT:
                user_interface.reverse_sort = not user_interface.reverse_sort
            else:
                user_interface.reverse_sort = False
            user_interface.publication_year_sort() 
        elif command in C.FILTER:
            user_interface.list_books()
            user_interface.get_filter() 
            user_interface.apply_filter()
        elif command in C.UP:
            user_interface.book_list_top_row_index -= user_interface.books_fit_in_one_view
        elif command in C.DOWN:
            user_interface.book_list_top_row_index += user_interface.books_fit_in_one_view
        elif re.match("^[1-9][0-9]*$", command):
            book_id = command
            command = book_details_control(library, user_interface, book_id)
        if not command in C.QUIT:
            command = None

def main(library_file=None,io_recording_file=None,rerecord=False):
    if library_file == None:
        library_file = os.path.normpath(C.LIBRARY_DIR + C.LIBRARY_FILE)
    if io_recording_file != None:
        user_interface = UserInterface(
            library = None, 
            io_recording_file = io_recording_file, 
            run_recorded = True, 
            record_additional_io = True, 
            rerecord_output = rerecord
        )
    else:
        user_interface = UserInterface()
    if not os.path.isfile(library_file): 
        if not user_interface.approve_creating_library_file(library_file):
            exit()
    library = Library(library_file)
    user_interface.library = library
    next_command = None
    while not next_command in C.QUIT:
        match next_command:
            case C.ADD_BOOK: 
                new_isbn, new_title, new_author, new_publication_year, new_status, new_pages, new_description = user_interface.ask_book_information()
                if new_title != None:
                    book = Book(new_isbn, None, new_title, new_author, new_publication_year, new_status, new_pages, new_description)
                    library.add_book(book)
            case C.LIST_BOOKS | C.BORROW_RETURN_BOOK | C.REMOVE_BOOK:
                book_list_control(library, user_interface)
            case C.SEARCH_BOOK:
                book_list_control(library, user_interface, C.FILTER[0])
            case _:
                next_command = C.QUIT
        next_command = user_interface.main_menu_command()
    library.save_library()
    return None

if __name__ == "__main__":
    library_file, io_recording_file, rerecord = None, None, None
    command_line_arguments = sys.argv[1:]
    if command_line_arguments != []: 
        library_file = command_line_arguments.pop(0)
    if command_line_arguments != []: 
        io_recording_file = command_line_arguments.pop(0)
    if command_line_arguments != []: 
        rerecord = command_line_arguments.pop(0)
        if rerecord == "True":
            rerecord = True
        else:
            rerecord = "False"
    main(library_file, io_recording_file, rerecord)

