import pymupdf  # imports the pymupdf library
import fitz
from tkinter import *
from tkinter import filedialog, messagebox
import os
import shutil
import PIL
from PIL import Image, ImageTk
import time
from gtts import gTTS
import threading
import pygame
from pdf2image import convert_from_path

from PDFfile import PdfImage
from PDFtext import TextPDF
from PDFaudio import AudioPDF

PDF_FOLDER = "./pdf_folder"
CURRENT_FILE = None  #needed in main
CURRENT_IMAGE = None  # not needed in main
tk_image = None  # somehwat needed - only for page number
tk_images_list = None  # somewhat needed



# ----------------- MAIN FUNCTIONS ---------------------


def switch_next_page_state():
    state = 'active' if next_page['state'] == 'disabled' else 'disabled'

    previous_page.config(state=state)
    next_page.config(state=state)


def switch_play_audio_state():
    state = 'active' if audio_button['state'] == 'disabled' else 'disabled'
    audio_button.config(state=state)


def switch_text_size_state():
    state = 'active' if decrease_button['state'] == 'disabled' else 'disabled'
    decrease_button.config(state=state)
    increase_button.config(state=state)


def decrease_font_size():
    text_pdf.decrease_font_size()


def increase_font_size():
    text_pdf.increase_font_size()


def update_current_file_label():
    """
    MAIN
    NEEDS CURRENT FILE FROM PDFfile
    """
    current_file.config(text=images_pdf.current_file.split('/')[-1].split('.')[0])


def view_next_page():
    """
    """
    next_page_num = images_pdf.view_next_page()  # display next page image
    update_page_num_label(next_page_num + 1)  # update page label
    text_pdf.insert_text(next_page_num)  # part of text class # insert that pages text


def view_previous_page():
    """
    """
    prev_page_num = images_pdf.view_previous_page()  # display prev page image
    update_page_num_label(prev_page_num + 1)  # update page label
    text_pdf.insert_text(prev_page_num)  # part of text class # insert that pages text


def update_page_num_label(num=1):
    """MAIN called when viewing prev and next page - plus when called in PDF file class"""
    page_label.config(text=f"Page: {num}", fg="black")


def force_constant_canvas_width():
    middle_width = middle_frame.winfo_width()
    half_width = middle_width // 2

    pdf_frame.config(width=half_width)
    pdf_main_frame.config(width=half_width)
    root.update_idletasks()


def ensure_equal_frame_sizes(pdf_frame, text_frame, parent_frame):
    """MAIN"""
    middle_width = parent_frame.winfo_width()
    half_width = middle_width // 2

    pdf_frame.config(width=half_width)
    text_frame.config(width=half_width)


def component_switch(frame1, frame2):
    """MAIN"""
    frame1.grid_remove()
    frame2.grid(row=1, column=0, sticky="nsew")
    root.update_idletasks()  # Ensure layout calculations are done
    ensure_equal_frame_sizes(frame2, text_frame, middle_frame)


def open_pdf_file():
    """
    MAIN
    """

    filepath = filedialog.askopenfile(title="Select PDF file",
                                      defaultextension='pdf',
                                      filetypes=[('PDF files', '*.pdf')])

    if filepath:

        source_path = filepath.name
        filename = source_path.split('/')[-1]
        destination_path = f"{PDF_FOLDER}/{filename}"

        # new file selected
        if filename not in os.listdir(PDF_FOLDER):
            shutil.copy(source_path, destination_path)

            # 1st file loaded
            if not images_pdf.current_file: # call from PDFfile - initial load call
                component_switch(pdf_temp_frame, pdf_main_frame) # set up canvas frame
                # activate user buttons
                switch_next_page_state()
                switch_play_audio_state()
                switch_text_size_state()
            # file previously loaded
            else:
                text_pdf.reset_text_pages()  # call to PDFtext
                extracted_icon.config(text='□')
                """option to delete prev audio files?
                possibly a 'reset prev audio function' """

            # DISPLAY THE IMAGE
            images_pdf.update_current_file(destination_path)  # updates the current file name
            images_pdf.show_pdf_image()  # gets the images from the pdf file

            # UPDATE LABELS
            update_page_num_label()  # update page number label
            update_current_file_label()

            """text functions - responsibility of text"""
            text_pdf.get_all_text(images_pdf.current_file)  # retrieve all texts from PDF files
            text_pdf.insert_text()  # display the new pages text

            """AUDIO functionality"""
            audio_pdf.create_audio_files_threaded(text_pdf.text_pages, images_pdf.current_file)

            # ensures canvas remains half the middle frame size
            force_constant_canvas_width()

        # filename already loaded
        else:
            messagebox.showinfo(title="Loaded",
                                message="File already loaded")
            raise FileExistsError


def text_to_voice():
    """
    Converts text to speech
    """

    playing = audio_pdf.text_to_voice(current_page=images_pdf.get_img_page_num(),
                            current_file=images_pdf.current_file)
    if playing:
        audio_button.config(state='disabled')
        stop_audio_button.config(state='active')


def stop_audio():
    """AUDIO"""

    audio_pdf.stop_audio()
    audio_button.config(state='active')
    stop_audio_button.config(state='disabled')


# ---------------------------------------------------


audio_folder = "./audio_folder"
if not os.path.isdir(audio_folder):
    os.mkdir(audio_folder)

if not os.path.isdir(PDF_FOLDER):
    os.mkdir(PDF_FOLDER)


TITLE = ("Georgia", 30, "bold")
BOLD_NORMAL = ("Georgia", 15, "bold")
NORMAL = ("Georgia", 15)
RESIZED_FONT = ["Georgia", 15]
SMALL = ("Georgia", 12)

root = Tk()
root.title("PDF to Speech")
root.geometry("1000x850")
root.minsize(width=1000, height=850)
# root.resizable(False, False)
root.config(padx=20, pady=20, bg="grey")

# Top
top_frame = Frame(root)
top_frame.pack(fill="x", pady=10)

top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)

file_frame = Frame(top_frame, bg="white")
file_frame.grid(row=0, column=0, sticky='nsew')

file_frame.grid_rowconfigure(0, weight=1)
file_frame.grid_columnconfigure(0, weight=1)
file_frame.grid_columnconfigure(1, weight=0)
file_frame.grid_columnconfigure(2, weight=0)
file_frame.grid_propagate(False)

# Load Button
load_button_top = Button(file_frame, text="Load PDF", bg='white', fg='black', font=BOLD_NORMAL,
                         command=open_pdf_file)
load_button_top.grid(row=0, column=0, sticky='w')

# labels
file_label = Label(file_frame, text="Current File: ", bg='white', fg='black', font=NORMAL)
file_label.grid(row=0, column=1, sticky='e')

current_file = Label(file_frame, text="", bg='lightgrey', fg='black', font=NORMAL, width=15)
current_file.grid(row=0, column=2, sticky='w')

extracted_frame = Frame(top_frame, bg="white")
extracted_frame.grid(row=0, column=1, sticky='nsew')
extracted_frame.grid_rowconfigure(0, weight=1)
extracted_frame.grid_columnconfigure(0, weight=1)
extracted_frame.grid_columnconfigure(1, weight=1)

text_extracted_label = Label(extracted_frame, text="Audio Extracted: ", bg='white', fg='black', font=NORMAL)
text_extracted_label.grid(row=0, column=0, sticky='e')

# ✓
""" change to the tick when text extracted """
extracted_icon = Label(extracted_frame, text="□", bg='white', fg='black', font=TITLE)
extracted_icon.grid(row=0, column=1, sticky='w')

# middle - frame
middle_frame = Frame(root, bg='lightgrey', borderwidth=5)
middle_frame.pack(fill="both", expand=True)
middle_frame.grid_propagate(False)
middle_frame.rowconfigure(0, weight=1)
middle_frame.rowconfigure(1, weight=10)
middle_frame.grid_columnconfigure(0, weight=1)
middle_frame.grid_columnconfigure(1, weight=1)

# top labels
pdf_frame_label = Label(middle_frame, text="PDF File", bg='white', fg='black',
                        font=NORMAL, width=middle_frame.winfo_width() // 2)
pdf_frame_label.grid(row=0, column=0, sticky='nsew')

text_frame_label = Label(middle_frame, text="Extract Text", bg='lightgrey', fg='black',
                         font=NORMAL, width=middle_frame.winfo_width() // 2)
text_frame_label.grid(row=0, column=1)

# Main frames
pdf_temp_frame = Frame(middle_frame, bg='white')  # -----initial placeholder frame for pdf -------
pdf_temp_frame.grid(row=1, column=0, sticky='nsew')
pdf_temp_frame.grid_propagate(False)
# load button for PDF:
load_pdf_button = Button(pdf_temp_frame, text="Load PDF", bg='blue', fg='black', font=BOLD_NORMAL,
                         command=open_pdf_file)
load_pdf_button.place(relx=0.5, rely=0.4, anchor='center')

pdf_main_frame = Frame(middle_frame, bg='white')  # ------ MAIN PDF Frame (LEFT) ----------------
# pdf_temp_frame.grid(row=1, column=0, sticky='nsew')
pdf_temp_frame.grid_propagate(False)

pdf_frame = Canvas(pdf_main_frame, bg='white')  # -- MAIN PDF CANVAS ------
pdf_frame.pack(fill='both', expand=True)
pdf_frame.grid_propagate(False)


text_frame = Frame(middle_frame, bg='lightgrey', width=middle_frame.winfo_width() // 2)  # ---- TEXT FRAME (Right) ---
text_frame.grid(row=1, column=1, sticky='nsew', pady=5, padx=5)
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_columnconfigure(0, weight=1)
text_frame.grid_propagate(False)
# - - - - Might not need this button - - -
# load_text_button = Button(text_frame, text="Extract Text", bg='white', fg='black', font=NORMAL, state='disabled',
#                           command=get_all_text)
# load_text_button.place(relx=0.5, rely=0.4, anchor='center')
text_box = Text(text_frame,
                fg="black", bg="white", wrap=WORD, font=NORMAL)
text_box.tag_configure("center", justify='center')
text_box.insert("1.0", "\n\n\nExtract Text from PDF files and voice out load.\n\n\nLoad a PDF file to begin.\n")
text_box.tag_add("center", "1.0", "end")
# text_box.insert(END, "\n\n\nExtract Text from PDF files and voice out load.\n\n\nLoad a PDF file to begin.\n") # placeholder text

# text_box.pack(fill="both", expand=True)
text_box.grid(row=0, column=0, sticky='nsew')
text_box.config(state=DISABLED)

# Bottom of the page

# Bottom of the page
bottom_frame = Frame(root, height=50, bg='grey')  # Set a fixed height (adjust as needed)
bottom_frame.pack(fill="x", pady=10)  # Remove expand=True and set only fill="x"

bottom_frame.grid_rowconfigure(0, weight=0)  # Prevent row from expanding
bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)
bottom_frame.grid_propagate(True)  # Let the frame adjust naturally to its content

move_page_frame = Frame(bottom_frame, bg='grey')  # Buttons inside bottom frame
move_page_frame.grid(row=0, column=0, sticky="w", padx=100)  # Adjust padding as needed
move_page_frame.grid_columnconfigure(0, weight=1)
move_page_frame.grid_columnconfigure(1, weight=1)
move_page_frame.grid_columnconfigure(2, weight=1)
move_page_frame.grid_columnconfigure(3, weight=1)
move_page_frame.grid_columnconfigure(4, weight=1)
# move_page_frame.grid_columnconfigure(2, weight=1)

# Previous page button
previous_page = Button(move_page_frame, text="<", bg="white", fg='black', font=NORMAL,
                       state='disabled', command=view_previous_page)
previous_page.grid(row=0, column=1, padx=10)

# Next page button
next_page = Button(move_page_frame, text=">", bg="white", fg='black', font=NORMAL,
                   state='disabled', command=view_next_page)
next_page.grid(row=0, column=3, padx=10)

page_label = Label(move_page_frame, text="Page: ", fg='black', bg='grey', font=NORMAL)
page_label.grid(row=0, column=2, padx=10)

audio_frame = Frame(bottom_frame, bg='grey')  # Buttons inside bottom frame
audio_frame.grid(row=0, column=1, sticky="ew")  # Adjust padding as needed
# audio_frame.grid_propagate(False)
audio_frame.grid_rowconfigure(0, weight=1)
audio_frame.grid_columnconfigure(0, weight=1)
audio_frame.grid_columnconfigure(1, weight=1)
audio_frame.grid_columnconfigure(2, weight=0)
audio_frame.grid_columnconfigure(3, weight=0)
audio_frame.grid_columnconfigure(4, weight=0)

audio_button = Button(audio_frame, text="Play Audio", bg="white", fg='black', font=NORMAL,
                      border=0,
                      state='disabled', command=text_to_voice)
audio_button.grid(row=0, column=0, sticky='e', padx=10)

stop_audio_button = Button(audio_frame, text="Stop Audio", bg="white", fg='black', font=NORMAL,
                           border=0,
                           state='disabled', command=stop_audio)
stop_audio_button.grid(row=0, column=1, sticky='w')

decrease_button = Button(audio_frame, text="-", bg="white", fg='black', font=NORMAL,
                         border=0,
                         state='disabled', command=decrease_font_size)
decrease_button.grid(row=0, column=2, sticky='e')

size_label = Label(audio_frame, text="Text Size", bg='grey', fg='black', font=NORMAL)
size_label.grid(row=0, column=3, padx=0)

increase_button = Button(audio_frame, text="+", bg="white", fg='black', font=NORMAL,
                         border=0,
                         state='disabled', command=increase_font_size)
increase_button.grid(row=0, column=4, sticky='w')


# initialise helper class objects
images_pdf = PdfImage(root, pdf_main_frame, pdf_frame, text_box)

text_pdf = TextPDF(text_box)

audio_pdf = AudioPDF(audio_folder, text_extracted_label, extracted_icon)


if __name__ == "__main__":
    # images_pdf = PdfImage(root, pdf_main_frame, pdf_frame, text_box)
    # text_pdf = TextPDF(text_box)
    # audio_pdf = AudioPDF(audio_folder, text_extracted_label, extracted_icon)
    root.mainloop()