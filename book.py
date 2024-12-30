#!/usr/bin/env python 

#from typing import Final
import re
import library_constants as C

class Book:
    _isbn: str = C.ISBN_UNDEFINED

    """ Returns Isbn where self._isbn is a C.ISBN_UNDEFINED if called with C.ISBN_UNDEFINED
    Creates Isbn where self._isbn is a valid ISBN if initiator is called with a valid ISBN
    Otherwises raises an exception """
    def __init__(
        self, 
        init_isbn = C.ISBN_UNDEFINED, 
        book_id = None, 
        title = "", author = "", 
        publication_year = C.YEAR_UNDEFINED, 
        status = C.UNKNOWN, 
        pages = None, description = None
    ):
        self.book_id:           str = book_id
        self.title:             str = title.strip()
        self.author:            str = author.strip()
        self.publication_year:  int = publication_year 
        self.status:            str = status
        self.pages:             int = pages
        self.description:       str = description
        if init_isbn == C.ISBN_UNDEFINED:
            self._isbn = C.ISBN_UNDEFINED
        elif self.validate_isbn(init_isbn) == False:
            raise ValueError(f"Invalid ISBN: {init_isbn}.")
        else:
            self.isbn = init_isbn

    """ ISBN parts can optionally be separated by hyphens or spaces
    Sources for Regexps
    https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html#:~:text=ISBN%2D10%20checksum,Divide%20the%20sum%20by%2011.
    https://regexlib.com/Search.aspx?k=ISBN&AspxAutoDetectCookieSupport=1 """
    @classmethod
    def validate_isbn(cls, isbn_to_validate):
        if type(isbn_to_validate) != str:
            return False
        if (not C.REGEXP_VALID_ISBN10.match(isbn_to_validate) and 
            not C.REGEXP_VALID_ISBN13.match(isbn_to_validate)):
            #print("Failed: " + isbn_to_validate)
            return False
        if not cls.validate_isbn_checksum(isbn_to_validate):
            return False
        checksum  = isbn_to_validate[-1]
        if checksum != cls.calculate_isbn_checksum(isbn_to_validate):
            return False
        return True

    """ As an argument, takes 9 or ISBN 12 characters long ISBN string
    Returns the checksum as a character since checksum 11 == X so integer is not possible
    The method does no checking but forces a result, right or wrong, even when the ISBN given is not a valid one. 
    One should call "validate_isbn" method separately
    Influenced heavily by https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html#:~:text=ISBN%2D10%20checksum,Divide%20the%20sum%20by%2011.
    but I undestand what it does. Simple enough and fairly consice. """
    @classmethod
    def calculate_isbn_checksum(cls, isbn):
        isbn = str(isbn) # Let's make sure we are dealing with a string
        # Remove non ISBN digits
        chars = re.sub("[^0-9X]", "", isbn) # Removes all characters except 0-9 and X
        if len(chars) > 13:
            chars = chars[-13]
        if len(chars) < 9:
            chars.zfill(9)
        old_checksum = ""
        if len(chars) == 10 or len(chars) == 13:
            old_checksum  = chars[-1]
            chars = chars[:-1]
            isbn = isbn[:-1]
        check = ""
        if len(chars) == 9:
              # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"
        check = str(check)
        return check

    """ As an argument, takes an ISBN  but does not check its validity other than that the last character or the explicitly given checksum 
    fullfills the algorithm implemented in the class method calculate_isbn_checksum
    The method does no checking but forces a result, right or wrong, even when the ISBN given is not a valid one. 
    One should call "validate_isbn" method separately """
    @classmethod
    def validate_isbn_checksum(cls, isbn, isbn_checksum = None):
        checksum  = isbn_checksum
        if checksum == None:
            checksum  = isbn[-1]
        if checksum != cls.calculate_isbn_checksum(isbn):
            return False
        return True

    @classmethod
    def standard_isbn_format(cls, isbn):
        standard_isbn = re.sub("[^0-9X]", "", str(isbn)) # Removes all characters except 0-9 and X 
        #if len(standard_isbn) < 13 and len(standard_isbn) > 2:
            #standard_isbn = standard_isbn[:-1] + "-" + standard_isbn[-1]
        #    print("Standard: " + standard_isbn[:-1] + "-" + standard_isbn[-1])
        #elif len(standard_isbn) > 10:
        #    standard_isbn = standard_isbn[:-10] + "-" + standard_isbn[-10:-1] + "-" + standard_isbn[-1]
        #    #print(standard_isbn[:-10] + "-" + standard_isbn[-10:-1] + "-" + standard_isbn[-1])
        standard_isbn = f"{standard_isbn}"
        return standard_isbn

    @property
    def isbn(self):
        return self._isbn

    """ Sets self._isbn to new_isbn IF self._isbn was previously undefined or invalid 
    and returns the new_isbn. If self._isbn is already set, raises an error """
    @isbn.setter
    def isbn(self, new_isbn):
        if new_isbn == C.ISBN_UNDEFINED and self._isbn == C.ISBN_UNDEFINED:
            return self._isbn
        if self.validate_isbn(self._isbn) == True:
            if self._isbn == new_isbn:
                return self._isbn
            else:
                raise RuntimeError("ISBN is already set.")
        if self.validate_isbn(new_isbn) == False:
            raise ValueError(f"Invalid ISBN: {new_isbn}.")
        if self._isbn != C.ISBN_UNDEFINED and self._isbn != C.ISBN_INVALID:
            raise RuntimeError("Previous ISBN not undefined nor invalid.")
        self._isbn = self.standard_isbn_format(new_isbn)
        #print(self._isbn)
        #self._isbn_EAN = self._isbn[:3]
        #self._isbn_GROUP = self._isbn[3:5]
        #self._isbn_PUBLISHER = self._isbn[5:9]
        #self._isbn_TITLE = self._isbn[9:12]
        #self._isbn_CHECK = self._isbn[12:]
        return self._isbn



