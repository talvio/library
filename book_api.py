import requests
import library_constants as C

MOCK_RETURN = [
    ["title_1", "subtitle_1", "author_1", 1000, 100, "print_type", ["test 1"], "Klingon", "isbn10", "978-0-596-52068-7"],
    ["title_2", "subtitle_2", "author_2", 1001, 101, "papyrus", ["test 2"], "en", "isbn10", "isbn13"],
    ["title_3", "subtitle_3", "author_3", 2000, 102, "clay", ["test 3"], "fi", "isbn10", "isbn13"],
    ['Contact', 'A Novel', 'Carl Sagan', '1985', 436, 'BOOK', ['Fiction'], 'en', '0671434004', '9780671434007'],
    ['Kontak (Contact)', None, 'Carl Sagan', '2020', 460, 'BOOK', ['Fiction'], 'id', '6020638979', '9786020638973'],
    ['Contact SF.', None, 'Carl Sagan', '1985', 0, 'BOOK', [], 'en', '0671434004', '9780671434007'],
    ["The Hitchhiker's Guide to the Galaxy", None, 'Douglas Adams', '2009', 233, 'BOOK', ['Fiction'], 'en', '0330513087', '9780330513081'],
    ["The Ultimate Hitchhiker's Guide to the Galaxy", None, 'Douglas Adams', '2002', 836, 'BOOK', ['Fiction'], 'en', '0345453743', '9780345453747'],
    ["The Ultimate Hitchhiker's Guide to the Galaxy", 'Five Novels in One Outrageous Volume', 'Douglas Adams', '2010', 1016, 'BOOK', ['Fiction'], 'en', '0307498468', '9780307498465'],
    ["The Hitchhiker's Guide to the Galaxy: The Illustrated Edition", None, 'Douglas Adams', '2007', 258, 'BOOK', ['Fiction'], 'en', '0307417131', '9780307417138'],
    ["The Hitchhiker's Guide to the Galaxy Illustrated Edition", None, 'Douglas Adams', '2021', 233, 'BOOK', ['Juvenile Fiction'], 'en', '1529046149', '9781529046144'],
]

"""
intitle: Returns results where the text following this keyword is found in the title.
inauthor: Returns results where the text following this keyword is found in the author.
inpublisher: Returns results where the text following this keyword is found in the publisher.
subject: Returns results where the text following this keyword is listed in the category list of the volume.
isbn: Returns results where the text following this keyword is the ISBN number.
lccn: Returns results where the text following this keyword is the Library of Congress Control Number.
oclc: Returns results where the text following this keyword is the Online Computer Library Center number.
"""

def google_books_api(title = "", author = ""):
    url  = C.GOOGLE_API
    url += f"intitle:{title}"
    url += f"+inauthor:{author}"
    url += f"&key={C.GOOGLE_API_KEY}"
    url += f"&timeout={C.API_TIMEOUT}"
    url += f"&maxResults={C.API_MAXRESULTS}"

    #return MOCK_RETURN

    # Make the request
    try:
        response = requests.get(url)
    except:
        return [None, f"Error: Unable to connect to Google Books API"]

    if response.status_code != 200:
        return [None, f"Error: {response.status_code} - {response.text}"]

    found_books = response.json()
    return_book_list = []
    for api_book in found_books.get('items', []):
        #print(str(api_book))
        #exit()
            
        book = api_book.get('volumeInfo', {})

        title = book.get('title')
        subtitle = book.get('subtitle')
        author = ', '.join(book.get('authors',[]))
        publishing_year = book.get('publishedDate', "")[:4]
        try:
            publishing_year = int(publishing_year)
        except:
            publishing_year = C.YEAR_UNDEFINED
        description = book.get('description')
        page_count = book.get('pageCount')
        print_type = book.get('printType')
        categories = book.get('categories',[])
        language = book.get('language')
        for identifier in book.get('industryIdentifiers', []):
            if identifier['type'] == "ISBN_10":
                isbn10 = identifier.get('identifier')
            elif identifier['type'] == "ISBN_13":
                isbn13 = identifier.get('identifier')
        """     
        print(f"title {title}")
        print(f"sub_title {subtitle}")
        print(f"author {author}")
        print(f"publishing_year {publishing_year}")
        print(f"page_count {page_count}")
        print(f"print_type {print_type}")
        print(f"categories {categories}")
        print(f"language {language}")
        print(f"isbn10 {isbn10}")
        print(f"isbn13 {isbn13}")
        print("---------------------------")
        """
        return_book_list.append([title, subtitle, author, publishing_year, page_count, print_type, categories, language, isbn10, isbn13, description])

    return return_book_list


if __name__ == "__main__":
    title = input("Book title to query: ")
    author = input("Book author to include in the query: ")
    for book in google_books_api(title, author):
        print(str(book))
