from typing import Final

import re

MESSAGE_FLASH_TIME:     Final = 2

## Menu selections
QUIT:                   Final = (0, "q", "Q", "Quit", "quit")
ADD_BOOK:               Final = (1)
LIST_BOOKS:             Final = (2)
SEARCH_BOOK:            Final = (3)
BORROW_RETURN_BOOK:     Final = (4)
REMOVE_BOOK:            Final = (5)
BORROW:                 Final = ("B","b","Borrow","borrow")
RETURN:                 Final = ("R","r","Return","return")
REMOVE:                 Final = ("M","m","Remove","remove")
ACCEPT:                 Final = ("A","a","Accept","accept")
REENTER:                Final = ("R","r","Reenter","reenter")
CANCEL:                 Final = ("C","c","Cancel","cancel")
YES:                    Final = ("Y","y","Yes","yes")
NO:                     Final = ("N","n","No","no")
AUTHOR:                 Final = ("A","a","Author","author")
TITLE:                  Final = ("T","t","Title","title")
ID:                     Final = ("I","i","Id","id")
FILTER:                 Final = ("F","f","Filter","filter")
UP:                     Final = ("U","u")
DOWN:                   Final = ("D","d")
EDIT:                   Final = ("E","e","Edit", "edit")
LIST:                   Final = (2, "L", "l", "List", "list")

VALID_BOOK_LIST_COMMAND = ACCEPT + REENTER + CANCEL + YES + AUTHOR + TITLE + ID + QUIT + FILTER + UP + DOWN

VALID_BOOK_DETAIL_COMMAND = BORROW + RETURN + REMOVE + EDIT + LIST + CANCEL

#VALID_BOOK_LIST_COMMAND_RE = re.compile(r"^[FfBbRrQqAaTtIi]|[0-9]+$")

## Book statuses
UNKNOWN:                Final = "UKNOWN"
AVAILABLE:              Final = "Available"
BORROWED:               Final = "Borrowed"
REMOVED:                Final = "Removed"
VALID_STATUSES:         Final = [UNKNOWN, AVAILABLE, BORROWED, REMOVED]
VALID_LIBRARY_TAGS:     Final = ["BOOK:","Title:", "Author:","Year:","Status:","BOOK_END"]
YEAR_UNDEFINED:         Final = -99999
ISBN_UNDEFINED:         Final = ""
ISBN_INVALID:           Final = -1

## Library file
LIBRARY_DIR:            Final = "/Users/talvio/Nextcloud/projects/MasterSchool-prework/"
LIBRARY_FILE:           Final = "library.txt"
TEST_DATA_DIR:          Final = LIBRARY_DIR + "test_data/"

## ISBN Regular expression
REGEXP_VALID_ISBN10 = re.compile(r"^(?:ISBN(?:-10)?:?\ )?(?=[-0-9X\ ]{13}$|[0-9X]{10}$)[0-9]{1,5}[-\ ]?(?:[0-9]+[-\ ]?){2}[0-9X]$")
REGEXP_VALID_ISBN13 = re.compile(r"^(?:ISBN(?:-13)?:?\ )?(?=[-0-9\ ]{17}$|[0-9]{13}$)97[89][-\ ]?[0-9]{1,5}[-\ ]?(?:[0-9]+[-\ ]?){2}[0-9]$")