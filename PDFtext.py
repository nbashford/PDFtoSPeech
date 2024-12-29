import fitz
from tkinter import *
import pymupdf  # imports the pymupdf library
"""
issue - how do i get the current image page number from PDFfile
- need to be passed it from main

- maybe can store the current page number
- when
"""

RESIZED_FONT = ["Georgia", 15]
text_pages = {}

class TextPDF:

    def __init__(self, text_field):
        self.tk_text_field = text_field
        self.text_pages = {}
        self.current_page = 0
        self.current_text = None
        self.resized_font = ["Georgia", 15]

    def get_all_text(self, current_file):
        """
        Now need some function to call to pass the page of text to
        - pass the text for each page

        - this gets ALL texts - could maybe call this when the pdf image is loaded
        """
        document = fitz.open(current_file)  # open a document
        for page_num, page in enumerate(document):  # iterate the document pages
            text = page.get_text()  # get plain text encoded as UTF-8
            if not text:
                pdf_string = "The loaded PDF has no text metadata. It is likely not a true PDF."
            else:
                pdf_string = text

            self.text_pages[page_num] = pdf_string

    def reset_text_pages(self):
        self.text_pages = {}

    def insert_text(self, page_num=0):
        """
        """
        self.current_page = page_num
        self.tk_text_field.config(state='normal')
        self.current_text = self.text_pages[page_num]
        self.tk_text_field.delete("1.0", END)  # from first row till end
        self.tk_text_field.insert("1.0", self.current_text)
        self.tk_text_field.tag_add("center", "1.0", "end")
        self.tk_text_field.config(font=tuple(self.resized_font), state=DISABLED)

    def increase_font_size(self):
        """
        """
        self.resized_font[1] = self.resized_font[1] + 1
        self.insert_text(self.current_page)

    def decrease_font_size(self):
        """
        """
        if self.resized_font[1] > 1:
            self.resized_font[1] = self.resized_font[1] - 1
        self.insert_text(self.current_page)

