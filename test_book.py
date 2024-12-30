#!/usr/bin/env python 

import pytest
from book import Book
import library_constants as C

# Fixture to provide a fresh Book class instance for each test.
@pytest.fixture
def test_book():
    return Book(C.ISBN_UNDEFINED)

isbn_test_values = [
    ("0-596-52068-9", True),
    ("978-0-596-52068-7", True),
    ("978-0-596-52068-6", False),
    ("0 596 52068 9", True),
    ("978 0 596 52068 7", True),
    ("ISBN 0-596-52068-9", True),
    ("ISBN 0-596-52068-0", False),
    ("ISBN 978-0-596-52068-7", True),
    ("ISBN: 978-0-596-52068-7", True),
    ("ISBN 0596520689", True),
    ("ISBN 9780596520687", True),
    ("ISBN 9770596520687", False),
    ("ISBN 978059652087", False),
    ("0596520689", True),
    ("123", False),
    ("9780596520687", True),
    (C.ISBN_INVALID, False),
    ("A", False),
    ("None", False),
    (123456789, False),
]

@pytest.mark.parametrize("isbn_to_test, is_valid", isbn_test_values)
def test_isbn_init(test_book, isbn_to_test, is_valid):
    if(is_valid):
        book = Book(isbn_to_test)
        assert book.isbn == test_book.standard_isbn_format(isbn_to_test)
    else:
        with pytest.raises(ValueError, match="Invalid ISBN."):Book(isbn_to_test)

def test_isbn_init_undefined():
    book = Book(C.ISBN_UNDEFINED)
    assert book.isbn == C.ISBN_UNDEFINED

@pytest.mark.parametrize("isbn_to_test, is_valid", isbn_test_values)
def test_validate_isbn(test_book, isbn_to_test, is_valid):
    assert test_book.validate_isbn(isbn_to_test) == is_valid

isbn_checksum_test_values = [
    ("0-596-52068", "9", True),
    ("978-0-596-52068-7", "7", True),
    ("978-0-596-52068", "7", True),
    ("978-0-596-52068-8", "7", True),
    ("978-0-596-52068-7", "8", False),
]

@pytest.mark.parametrize("naked_isbn, checksum, is_checksum_correct", isbn_checksum_test_values)
def test_calculate_isbn_checksum(test_book, naked_isbn, checksum, is_checksum_correct):
    if is_checksum_correct:
    	assert test_book.calculate_isbn_checksum(naked_isbn) == checksum
    else:
        assert test_book.calculate_isbn_checksum(naked_isbn) != checksum

@pytest.mark.parametrize("naked_isbn, checksum, is_checksum_correct", isbn_checksum_test_values)
def test_validate_isbn_checksum(test_book, naked_isbn, checksum, is_checksum_correct):
    assert test_book.validate_isbn_checksum(naked_isbn, checksum) == is_checksum_correct

@pytest.mark.parametrize("isbn_to_test, is_valid", isbn_test_values)
def test_isbn_setter(test_book, isbn_to_test, is_valid):
    if is_valid:
        test_book.isbn = isbn_to_test
        assert test_book.isbn == test_book.standard_isbn_format(isbn_to_test)
        test_book.isbn = test_book.standard_isbn_format(isbn_to_test)
        assert test_book.isbn == test_book.standard_isbn_format(isbn_to_test)
        with pytest.raises(RuntimeError, match="ISBN is already set"):test_book.isbn = test_book.standard_isbn_format("9780671434007")
        #test_isbn.isbn = 123
        #with pytest.raises(RuntimeError, match="Previous ISBN not undefined nor invalid."):test_isbn.isbn = isbn_to_test
    else:
        with pytest.raises(ValueError, match="Invalid ISBN."):test_book.isbn = test_book.standard_isbn_format(isbn_to_test)
        assert test_book.isbn == C.ISBN_UNDEFINED


