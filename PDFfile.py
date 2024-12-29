from pdf2image import convert_from_path
from PIL import Image, ImageTk
import os
from tkinter import *

PDF_FOLDER = "./pdf_folder"
current_file = None
current_image = None
tk_image = None
tk_images_list = None
text_pages = {}  # should not be in here


"""
what variables are needed: 
pdf_main_frame
pdf_frame
RESIZED_FONT
NORMAL
text_box

"""

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
        # print(self.tk_image)
        # CURRENT_IMAGE = pdf_frame.create_image(width // 2, height // 2, image=tk_image)
        self.current_image = self.pdf_canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        """
        should the shown image be responsbiloty of main? 
        """

    def show_pdf_image(self):

        if self.current_file:
            if self.tk_images_list:
                self.tk_images_list.clear()
                self.tk_images_list = []  # This removes references to the images in the list
                self.tk_image = None  # Set the current image to None

            self.create_tk_images_from_file()
            """
            Does the job of:
                images = get_images_from_file(current_file)  # gets all PIL images from PDF files
                new_width, new_height = resize_images(images)  # resizes PIL images to fit canvas
                tk_images_list = create_tk_image_list(images)  # holds TK photo images of loaded PDF pages
            """
            self.display_img_page()  # new_width, new_height)  # show image on canvas


            # """text functions - responsibility of audio"""
            # get_all_text()  # retrieve all texts from PDF files
            # insert_text()  # display the new pages text
            # # create_audio_files()  # creates audio files for each page
            # create_audio_files_threaded()
            #
            # """Updating functions - responsibility of main"""
            # update_page_num_label()  # update page number label
            # update_current_file_label()

            self.pdf_canvas.config(width=self.resized_width, height=self.resized_height)
            self.tk_pdf_container.config(width=self.resized_width, height=self.resized_height)
            self.root.update_idletasks()


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


    # def get_images_from_file(self):  # , last_page=10):
    #     """
    #     1. gets the list of images
    #     """
    #     if self.current_file:
    #         return convert_from_path(self.current_file, first_page=1)
    #     else:
    #         print("Error")
    #
    # def resize_images(self, image_list):
    #     """
    #     2. resizes the images
    #     """
    #     pil_image = image_list[0]
    #
    #     # 2. need to get the width and height of the canvas frame
    #     max_width = self.tk_pdf_container.winfo_width()
    #     max_height = self.tk_pdf_container.winfo_height()
    #
    #     aspect_ratio = min(max_width / pil_image.width, max_height / pil_image.height)
    #     new_width = int(pil_image.width * aspect_ratio)
    #     new_height = int(pil_image.height * aspect_ratio)
    #
    #     for i in range(len(image_list)):
    #         image_list[i] = image_list[i].resize((new_width, new_height), Image.LANCZOS)
    #
    #     return new_width, new_height
    #
    #
    # def create_tk_image_list(self, image_list):
    #     """
    #     3. create tk images and store in tk_images_list
    #     """
    #
    #     self.tk_images_list = []
    #     for img in image_list:
    #         tk_img = ImageTk.PhotoImage(img)
    #         self.tk_images_list.append(tk_img)
    #     return tk_images_list  # might not need to return anything





# def get_images_from_file(file):  #, last_page=10):
#     """
#     the self.current_file
#     DONE
#     """
#     return convert_from_path(file, first_page=1)


# def resize_images(image_list):
#     pil_image = image_list[0]
#
#     # 2. need to get the width and height of the canvas frame
#     max_width = pdf_main_frame.winfo_width()
#     max_height = pdf_main_frame.winfo_height()
#
#     aspect_ratio = min(max_width / pil_image.width, max_height / pil_image.height)
#     # 3. change the width and height based on aspect ratio
#     new_width = int(pil_image.width * aspect_ratio)
#     new_height = int(pil_image.height * aspect_ratio)
#
#     for i in range(len(image_list)):
#         image_list[i] = image_list[i].resize((new_width, new_height), Image.LANCZOS)
#
#     return new_width, new_height


# def create_tk_image_list(image_list):
#
#     tk_images = []
#     for img in image_list:
#         tk_img = ImageTk.PhotoImage(img)
#         tk_images.append(tk_img)
#     return tk_images

#
# def display_img_page(page=0): # width, height,
#     global curre, tk_image
#     if curre and tk_image:
#         curre = None
#         tk_image = None
#     tk_image = tk_images_list[page]
#     # CURRENT_IMAGE = pdf_frame.create_image(width // 2, height // 2, image=tk_image)
#     curre = pdf_frame.create_image(0, 0, image=tk_image, anchor="nw")



"""
def increase_font_size():

    #part of audio

    global RESIZED_FONT
    RESIZED_FONT[1] = RESIZED_FONT[1] + 1
    insert_text(alt_size=True)

def decrease_font_size():
    global RESIZED_FONT
    if RESIZED_FONT[1] > 1:
        RESIZED_FONT[1] = RESIZED_FONT[1] - 1
    insert_text(alt_size=True)


def current_page_text():

    #think should not be in this file

    current_page_index = get_img_page_num()
    current_text = text_pages[current_page_index]
    return current_text



def insert_text(alt_size=False):
    if alt_size:
        font = tuple(RESIZED_FONT)
    else:
        font = NORMAL
    text_box.config(state='normal')
    current_text = current_page_text()
    text_box.delete("1.0", END)  # from first row till end
    text_box.insert("1.0", current_text)
    text_box.tag_add("center", "1.0", "end")
    text_box.config(font=font, state=DISABLED)

"""


# def get_img_page_num():
#     current_img_index = tk_images_list.index(tk_image)
#     return current_img_index
#
#


# def show_pdf_image(canvas_frame):
#     global tk_image, tk_images_list
#
#     if current_file:
#         if tk_images_list:
#             tk_images_list.clear()
#             tk_images_list = None# This removes references to the images in the list
#             tk_image = None  # Set the current image to None
#
#
#         images = get_images_from_file(current_file)  # gets all PIL images from PDF files
#         new_width, new_height = resize_images(images)  # resizes PIL images to fit canvas
#         tk_images_list = create_tk_image_list(images)  # holds TK photo images of loaded PDF pages
#         display_img_page() #new_width, new_height)  # show image on canvas
#
#         update_page_num_label()  # update page number label
#         get_all_text()  # retrieve all texts from PDF files
#         insert_text()  # display the new pages text
#
#         # create_audio_files()  # creates audio files for each page
#         create_audio_files_threaded()
#
#         update_current_file_label()
#
#         canvas_frame.config(width=new_width, height=new_height)
#         pdf_main_frame.config(width=new_width, height=new_height)
#         root.update_idletasks()