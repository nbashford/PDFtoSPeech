from pdf2image import convert_from_path
from PIL import Image, ImageTk

PDF_FOLDER = "./pdf_folder"


class PdfImage:
    def __init__(self, tk_container, tk_canvas, text_box):
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
        max_width = self.tk_pdf_container.winfo_width()
        max_height = self.tk_pdf_container.winfo_height()
        # gets aspect ratio for resizing image
        aspect_ratio = min(max_width / images[0].width, max_height / images[0].height)
        self.resized_width = int(images[0].width * aspect_ratio)
        self.resized_height = int(images[0].height * aspect_ratio)
        # resize each image
        for i in range(len(images)):
            images[i] = images[i].resize((self.resized_width, self.resized_height))

        # convert to tk image and store in list
        self.tk_images_list = []
        for img in images:
            tk_img = ImageTk.PhotoImage(img)
            self.tk_images_list.append(tk_img)

    def display_img_page(self, page=0):
        """displays the image selected. Removes any previous image displayed."""
        if self.current_image and self.tk_image:
            self.current_image = None
            self.tk_image = None
        self.tk_image = self.tk_images_list[page]  # get the image based on current page dictionary key
        self.current_image = self.pdf_canvas.create_image(0, 0, image=self.tk_image, anchor="nw")  # add image

    def show_pdf_image(self):
        """
        Creates all pdf images. Resets/clears any previous tk images, then called above functions to open and
        resize images, make into tk images, then displays the image.
        """
        if self.current_file:
            if self.tk_images_list:
                self.tk_images_list.clear()
                self.tk_images_list = []  # removes images
                self.tk_image = None

            self.create_tk_images_from_file()  # create resized images from pdf file
            self.display_img_page()  # show image on canvas

    def get_img_page_num(self):
        """get page number of current displayed image"""
        current_img_index = self.tk_images_list.index(self.tk_image)
        return current_img_index

    def update_current_file(self, destination_path):
        """set the current file filename"""
        self.current_file = destination_path

    def view_next_page(self):
        """view the next pdf page image. Returns next page number"""
        current_page = self.get_img_page_num()
        # calc next page number
        if current_page + 1 == len(self.tk_images_list):
            next_page_num = 0
        else:
            next_page_num = current_page + 1

        self.display_img_page(next_page_num)  # display next page
        return next_page_num

    def view_previous_page(self):
        """view the previous pdf page image. Returns previous page number"""
        current_page = self.get_img_page_num()  # part of PDF file class
        # calc prev page number
        prev_page_num = current_page - 1
        if prev_page_num < 0:
            prev_page_num = len(self.tk_images_list) - 1

        self.display_img_page(prev_page_num)  # display prev page
        return prev_page_num
