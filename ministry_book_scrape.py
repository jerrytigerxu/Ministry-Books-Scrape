from selenium import webdriver
import webbrowser, os, requests, bs4, pdfkit
from selenium.common.exceptions import NoSuchElementException


# Create a function that checks if an element you are searching for exists (focus on searching for link by text)
def link_exists(search_text): # based on browser.find_element_by_partial_link_text() method
    elementDisplayed = False # This is the default
    try:
        browser.find_element_by_partial_link_text(search_text)
        elementDisplayed = True
    except NoSuchElementException:
        elementDisplayed = False
    return elementDisplayed


# Function that checks if there are no more sections in the book (allowing the program to move on to the next book)
def no_more_sections():
    noSections = False
    try:
        browser.find_element_by_css_selector("a[class='button radius disabled']")
        if browser.find_element_by_css_selector("a[class='button radius disabled']").text == 'prev section':
            noSections = False
        else:
            noSections = True
    except NoSuchElementException:
        noSections = False
    return noSections


browser = webdriver.Chrome()  # Opens to the chrome browser
next_chapter_link = 'next chapter'
next_section_link = 'next section'
clickSpeed = 0.03  # Amount of time for browser to wait before clicking link
homePage = 'https://www.ministrybooks.org/life-studies.cfm'
# First going to the "home page" -> in this case it is the life studies page
bookname_links = []

browser.get(homePage)  # This is the starting point
browser.implicitly_wait(clickSpeed)

list_div = browser.find_element_by_class_name('large-10')  # div element where all of the booknames are located
links = list_div.find_elements_by_partial_link_text('Life-Study')  # Get all of the links from the div that have the words 'Life-Study'

# the browser finds all of the book names based on the links and appends them to the bookname_links list
for link in links:
    bookname_links.append(link.text)


# Saving the html files in the Documents folder
os.chdir('/Users/zane/Documents/ministry_book_texts')

# loops through the process for every single book on the bookname_links list
for bookNum in range(len(bookname_links)):
    browser.get(homePage)
    browser.implicitly_wait(clickSpeed)

    # Create an html file that stores all of the text you scrape
    html_string = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    
        <style>
            body {
                font-family: 'Times New Roman';
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
    """

    savePrefix = './ministry_text_%s' % (bookname_links[bookNum])
    saveFile = savePrefix + '.html'
    text_file = open(saveFile, 'w')
    text_file.write(html_string)
    text_file.close()

    # Find the link to the particular book and click that link
    if link_exists(bookname_links[bookNum]):
        link = browser.find_element_by_link_text(bookname_links[bookNum])
        browser.implicitly_wait(clickSpeed)
        link.click()
    else: # Corresponds with first link - Going to particular book
        print('Was not able to find a link with that name.')

    # Stop the while loop when there is no next_chapter_link or next_section_link left in the book

    while True:
        if not (link_exists(next_chapter_link) or link_exists(next_section_link)):
            print('There is no button called "next chapter" or "next section"')
            break
        else:
            if link_exists(next_chapter_link):
                link = browser.find_element_by_partial_link_text(next_chapter_link)
                link.click()
                browser.implicitly_wait(clickSpeed)
            elif link_exists(next_section_link):
                link = browser.find_element_by_partial_link_text(next_section_link)
                link.click()
                browser.implicitly_wait(clickSpeed)
            html = browser.page_source
            soup = bs4.BeautifulSoup(html, features="html.parser")
            html = list(soup.children)[5]
            body = list(html.children)[3]
            ministry_text_tag = (body.select('#ministry-text'))[0]
            ministry_text = str(ministry_text_tag)
            text_file = open(saveFile, 'a')
            text_file.write(ministry_text)
            text_file.close()
            if no_more_sections():
                break
    browser.implicitly_wait(clickSpeed)

    # Add the rest of the html file text to close it off (completes the html file)
    text_file = open(saveFile, 'a')
    text_file.write("</body></html>")

    # Converting html file into pdf file
    convertFile = savePrefix + '.pdf'
    pdfkit.from_file(saveFile, convertFile)

    # Delete the html file, leaving behind only the pdfs
    os.remove(saveFile)


