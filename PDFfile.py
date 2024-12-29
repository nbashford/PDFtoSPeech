from pdf2image import convert_from_path
from PIL import Image, ImageTk
from tkinter import *

PDF_FOLDER = "./pdf_folder"
current_file = None
current_image = None
tk_image = None
tk_images_list = None



class PdfImage:

    def __init__(self, root, tk_container, tk_canvas, text_box):
        self.root = root
        self.tk_pdf_container = tk_container
        self.pdf_canvas = tk_canvas
        self.text_box = text_box
        self.current_file = None
        self.current_image = None
        self.tk_image = None
        self.tk_images_list = []
        self.resized_height = None
        self.resized_width = None


    def create_tk_images_from_file(self):
        """
        gets images from PDF file, resizes them to the tkinter frame that will be holding the
        tkinter canvas, then converts each img to a tk image and stored as a list.
        """

        # get images from PDF file
        images = convert_from_path(self.current_file, first_page=1)

        # resize the images
        max_width = self.tk_pdf_container.winfo_width()
        max_height = self.tk_pdf_container.winfo_height()

        aspect_ratio = min(max_width / images[0].width, max_height / images[0].height)
        self.resized_width = int(images[0].width * aspect_ratio)
        self.resized_height = int(images[0].height * aspect_ratio)

        for i in range(len(images)):
            images[i] = images[i].resize((self.resized_width, self.resized_height))

        # convert to tk image and store in list
        self.tk_images_list = []
        for img in images:
            tk_img = ImageTk.PhotoImage(img)
            self.tk_images_list.append(tk_img)

    def display_img_page(self, page=0):
        if self.current_image and self.tk_image:
            self.current_image = None
            self.tk_image = None
        self.tk_image = self.tk_images_list[page]
        self.current_image = self.pdf_canvas.create_image(0, 0, image=self.tk_image, anchor="nw")


    def show_pdf_image(self):

        if self.current_file:
            if self.tk_images_list:
                self.tk_images_list.clear()
                self.tk_images_list = []  # This removes references to the images in the list
                self.tk_image = None  # Set the current image to None

            self.create_tk_images_from_file()

            self.display_img_page()  # new_width, new_height)  # show image on canvas

            # self.pdf_canvas.config(width=self.resized_width, height=self.resized_height)
            # self.tk_pdf_container.config(width=self.resized_width, height=self.resized_height)
            # self.root.update_idletasks()


    def get_img_page_num(self):
        current_img_index = self.tk_images_list.index(self.tk_image)
        return current_img_index


    def update_current_file(self, destination_path):
        self.current_file = destination_path


    def view_next_page(self):

        current_page = self.get_img_page_num()  # part of PDF file class
        if current_page + 1 == len(self.tk_images_list):
            next_page_num = 0
        else:
            next_page_num = current_page + 1

        self.display_img_page(next_page_num)
        return next_page_num

    def view_previous_page(self):

        current_page = self.get_img_page_num()  # part of PDF file class
        prev_page_num = current_page - 1

        if prev_page_num < 0:
            prev_page_num = len(self.tk_images_list) - 1

        self.display_img_page(prev_page_num)  # part of PDFfile function
        return prev_page_num
