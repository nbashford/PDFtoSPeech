import fitz
from tkinter import *


class TextPDF:
    def __init__(self, text_field):
        self.tk_text_field = text_field  # displays the text
        self.text_pages = {}  # hold page number as keys and text from each page as values
        self.current_page = 0
        self.current_text = None
        self.resized_font = ["Georgia", 15]

    def get_all_text(self, current_file):
        """
        extracts the page number and text from the pdf file.
        Stores in a dictionary.
        """
        document = fitz.open(current_file)  # open document
        for page_num, page in enumerate(document):  # iterate document pages
            text = page.get_text()  # get plain text
            if not text:  # cannot extract text - set default text
                pdf_string = "The loaded PDF has no text metadata. It is likely not a true PDF."
            else:
                pdf_string = text

            self.text_pages[page_num] = pdf_string  # store in dictionary

    def reset_text_pages(self):
        """reset text dictionary"""
        self.text_pages = {}

    def insert_text(self, page_num=0):
        """places the current pages text into the text box displayed"""
        self.current_page = page_num
        self.tk_text_field.config(state='normal')
        self.current_text = self.text_pages[page_num]
        self.tk_text_field.delete("1.0", END)  # from first row till end
        self.tk_text_field.insert("1.0", self.current_text)
        self.tk_text_field.tag_add("center", "1.0", "end")
        self.tk_text_field.config(font=tuple(self.resized_font), state=DISABLED)

    def increase_font_size(self):
        """increase the font size"""
        self.resized_font[1] = self.resized_font[1] + 1
        self.insert_text(self.current_page)  # re-adds the page text with larger font

    def decrease_font_size(self):
        """increase the font size"""
        if self.resized_font[1] > 1:
            self.resized_font[1] = self.resized_font[1] - 1
        self.insert_text(self.current_page)  # re-adds the page text with smaller font

