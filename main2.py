"""
TODO:
be able to select a previously loaded file and load that instead i.e. go back
"""

from tkinter import *
from tkinter import filedialog, messagebox
import os
import shutil
from PDFfile import PdfImage
from PDFtext import TextPDF
from PDFaudio import AudioPDF

# global variables
PDF_FOLDER = "./pdf_folder" # default PDF folder name
AUDIO_FOLDER = "./audio_folder"
check_loaded_event = None  # holds tk root after events
TITLE = ("Georgia", 30, "bold")
BOLD_NORMAL = ("Georgia", 15, "bold")
NORMAL = ("Georgia", 15)
RESIZED_FONT = ["Georgia", 15]


def switch_next_page_state():
    """switches state of next and previous button state"""
    state = 'active' if next_page['state'] == 'disabled' else 'disabled'
    previous_page.config(state=state)
    next_page.config(state=state)


def switch_play_audio_state():
    """switches state of play button state"""
    state = 'active' if audio_button['state'] == 'disabled' else 'disabled'
    audio_button.config(state=state)


def switch_text_size_state():
    """switches state of increase and decrease text buttons states"""
    state = 'active' if decrease_button['state'] == 'disabled' else 'disabled'
    decrease_button.config(state=state)
    increase_button.config(state=state)


def decrease_font_size():
    """calls PDFtext class to decrease text font size"""
    text_pdf.decrease_font_size()


def increase_font_size():
    """calls PDFtext class to increase text font size"""
    text_pdf.increase_font_size()


def update_current_file_label():
    """displays name of current PDF uploaded. Calls PDFaudio class to get current pdf name"""
    current_file.config(text=images_pdf.current_file.split('/')[-1].split('.')[0])


def view_next_page():
    """
    Dislays next pdf page image and text.
    Calls PDFaudio class and PDFtext to get next image and text.
    """
    next_page_num = images_pdf.view_next_page()  # display next page image
    update_page_num_label(next_page_num + 1)  # update page label
    text_pdf.insert_text(next_page_num)  # part of text class # insert that pages text


def view_previous_page():
    """
    Dislays previous pdf page image and text.
    Calls PDFaudio class and PDFtext to get previous image and text.
    """
    prev_page_num = images_pdf.view_previous_page()  # display prev page image
    update_page_num_label(prev_page_num + 1)  # update page label
    text_pdf.insert_text(prev_page_num)  # part of text class # insert that pages text


def update_page_num_label(num=1):
    """Updates current page label to current viewed page """
    page_label.config(text=f"Page: {num}", fg="black")


def force_constant_canvas_width():
    """sets the tk canvas and text frame to be half the width of the containing middle frame"""
    middle_width = middle_frame.winfo_width()
    half_width = middle_width // 2
    pdf_frame.config(width=half_width)
    pdf_main_frame.config(width=half_width)
    text_frame.config(width=half_width)
    root.update_idletasks()  # force layout update


def component_switch(frame1, frame2):
    """switches the initial temp frame to the frame holding the canvas frame"""
    frame1.grid_remove()
    frame2.grid(row=1, column=0, sticky="nsew")
    root.update_idletasks()  # force layout update


def open_pdf_file():
    """
    User selects and loads new PDF file.
    Function passes the current file to PDFAudio, PDFtext, PDFfile to load pdf images, get all text, and
    generate audio.
    """
    # select file
    filepath = filedialog.askopenfile(title="Select PDF file",
                                      defaultextension='pdf',
                                      filetypes=[('PDF files', '*.pdf')])

    if filepath:

        source_path = filepath.name
        filename = source_path.split('/')[-1]
        destination_path = f"{PDF_FOLDER}/{filename}"  # path to default pdf folder

        # new file selected
        if filename not in os.listdir(PDF_FOLDER):
            shutil.copy(source_path, destination_path)  # add copy to pdf folder in project

            if not images_pdf.current_file:  # 1st file loaded in app
                component_switch(pdf_temp_frame, pdf_main_frame) # set up canvas frame
                switch_next_page_state()  # activate user buttons
                switch_play_audio_state()
                switch_text_size_state()

            else:  # file previously loaded
                text_pdf.reset_text_pages()  # removes previous text
                extracted_icon.config(text='□')  # reset label

            # PDFfile class to display the pdf images
            images_pdf.update_current_file(destination_path)  # updates the current file name
            images_pdf.show_pdf_image()  # gets the images from the pdf file

            # PDFtext class to display the pdf text
            text_pdf.get_all_text(destination_path)  # gets all texts
            text_pdf.insert_text()  # display page text

            # PDFaudio class to generate TTS
            audio_pdf.create_audio_files_threaded(text_pdf.text_pages, destination_path)

            # update labels
            update_page_num_label()
            update_current_file_label()

            # cancel any previous tk after event
            if check_loaded_event:
                root.after_cancel(check_loaded_event)

            # updates label identifying if audio is extracted
            update_extracted_text_label()

            # ensures canvas and text frame equal size
            force_constant_canvas_width()

        else:  # filename already loaded
            messagebox.showinfo(title="Loaded",
                                message="File already loaded")
            raise FileExistsError


def text_to_voice():
    """
    Calls PDFaudio class to handle playing audio.
    Requires current page displayed, and current filename
    """
    playing = audio_pdf.text_to_voice(current_page=images_pdf.get_img_page_num(),
                                      current_file=images_pdf.current_file)

    if playing:  # switch state if play and stop audio buttons
        audio_button.config(state='disabled')
        stop_audio_button.config(state='active')


def stop_audio():
    """Calls PDFaudio to stop audio playing. Switches state of play and stop buttons."""
    audio_pdf.stop_audio()
    audio_button.config(state='active')
    stop_audio_button.config(state='disabled')


def update_extracted_text_label(time_ms=2000):
    """
    Updates the no. of pages that have had audio generated.
    Gets the current page loaded from the PDFaudio class.
    Calls the containing function again until all audio generated.
    """
    global check_loaded_event
    total_pages = len(text_pdf.text_pages)
    current_page = audio_pdf.current_page_loaded
    page_status = f"{current_page}/{total_pages}"
    text_extracted_label.config(text=f"Audio Pages Extracted: {page_status}")

    if current_page < total_pages:
        # call function again later
        check_loaded_event = root.after(time_ms, update_extracted_text_label)
    else:  # all audio extracted
        extracted_icon.config(text='✓')


# create audio and pdf folder if not created
if not os.path.isdir(AUDIO_FOLDER):
    os.mkdir(AUDIO_FOLDER)

if not os.path.isdir(PDF_FOLDER):
    os.mkdir(PDF_FOLDER)


# Root setup - contains 3 frames - - - - - -
root = Tk()
root.title("PDF to Speech")
root.geometry("1000x850")
root.minsize(width=1000, height=850)
root.config(padx=20, pady=20, bg="grey")

# Top frame (1) setup - - - - - - - - - - - - - - - - - - - - - - -
top_frame = Frame(root)
top_frame.pack(fill="x", pady=10)
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)

# container within top frame
file_frame = Frame(top_frame, bg="white")
file_frame.grid(row=0, column=0, sticky='nsew')
file_frame.grid_rowconfigure(0, weight=1)
file_frame.grid_columnconfigure(0, weight=1)
file_frame.grid_columnconfigure(1, weight=0)
file_frame.grid_columnconfigure(2, weight=0)
file_frame.grid_propagate(False)
# Load Button
load_button_top = Button(file_frame, text="Load PDF", bg='white', fg='black',
                         font=BOLD_NORMAL, command=open_pdf_file)
load_button_top.grid(row=0, column=0, sticky='w')
# current file label
file_label = Label(file_frame, text="Current File: ", bg='white', fg='black', font=NORMAL)
file_label.grid(row=0, column=1, sticky='e')
# current file
current_file = Label(file_frame, text="", bg='lightgrey', fg='black', font=NORMAL, width=15)
current_file.grid(row=0, column=2, sticky='w')

# 2nd container within top frame
extracted_frame = Frame(top_frame, bg="white")
extracted_frame.grid(row=0, column=1, sticky='nsew')
extracted_frame.grid_rowconfigure(0, weight=1)
extracted_frame.grid_columnconfigure(0, weight=1)
extracted_frame.grid_columnconfigure(1, weight=1)
# audio extracted label
text_extracted_label = Label(extracted_frame, text="Audio Pages Extracted: ", bg='white', fg='black', font=NORMAL)
text_extracted_label.grid(row=0, column=0, sticky='e')
# audio extracted yes or no label
extracted_icon = Label(extracted_frame, text="□", bg='white', fg='black', font=TITLE)
extracted_icon.grid(row=0, column=1, sticky='w')

# Middle frame (2) setup - - - - - - - - - - - - - - - - - - - - - - -
middle_frame = Frame(root, bg='lightgrey', borderwidth=5)
middle_frame.pack(fill="both", expand=True)
middle_frame.grid_propagate(False)
middle_frame.rowconfigure(0, weight=1)
middle_frame.rowconfigure(1, weight=10)
middle_frame.grid_columnconfigure(0, weight=1)
middle_frame.grid_columnconfigure(1, weight=1)

# pdf image label
pdf_frame_label = Label(middle_frame, text="PDF File", bg='white', fg='black',
                        font=NORMAL, width=middle_frame.winfo_width() // 2)
pdf_frame_label.grid(row=0, column=0, sticky='nsew')
# pdf text label
text_frame_label = Label(middle_frame, text="Extract Text", bg='lightgrey', fg='black',
                         font=NORMAL, width=middle_frame.winfo_width() // 2)
text_frame_label.grid(row=0, column=1)

# Temporary frame where pdf image will be displayed
pdf_temp_frame = Frame(middle_frame, bg='white')
pdf_temp_frame.grid(row=1, column=0, sticky='nsew')
pdf_temp_frame.grid_propagate(False)
# load button for PDF:
load_pdf_button = Button(pdf_temp_frame, text="Load PDF", bg='blue', fg='black', font=BOLD_NORMAL,
                         command=open_pdf_file)
load_pdf_button.place(relx=0.5, rely=0.4, anchor='center')

# Main frame holding canvas frame
pdf_main_frame = Frame(middle_frame, bg='white')
pdf_temp_frame.grid_propagate(False)
# Canvas frame holding pdf image
pdf_frame = Canvas(pdf_main_frame, bg='white')
pdf_frame.pack(fill='both', expand=True)
pdf_frame.grid_propagate(False)

# frame to hold the pdf text and setup
text_frame = Frame(middle_frame, bg='lightgrey', width=middle_frame.winfo_width() // 2)
text_frame.grid(row=1, column=1, sticky='nsew', pady=5, padx=5)
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_columnconfigure(0, weight=1)
text_frame.grid_propagate(False)
# text area to hold pdf text + inital helper text
text_box = Text(text_frame, fg="black", bg="white", wrap=WORD, font=NORMAL)
text_box.tag_configure("center", justify='center')
text_box.insert("1.0", "\n\n\nExtract Text from PDF files and voice out load.\n\n\nLoad a PDF file to begin.\n")
text_box.tag_add("center", "1.0", "end")
text_box.grid(row=0, column=0, sticky='nsew')
text_box.config(state=DISABLED)

# Bottom frame (3) setup - - - - - - - - - - - - - - - - - - - - - - -
bottom_frame = Frame(root, height=50, bg='grey')
bottom_frame.pack(fill="x", pady=10)
bottom_frame.grid_rowconfigure(0, weight=0)
bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)
bottom_frame.grid_propagate(True)

# frame for pdf image contol
move_page_frame = Frame(bottom_frame, bg='grey')
move_page_frame.grid(row=0, column=0, sticky="w", padx=100)
move_page_frame.grid_columnconfigure(0, weight=1)
move_page_frame.grid_columnconfigure(1, weight=1)
move_page_frame.grid_columnconfigure(2, weight=1)
move_page_frame.grid_columnconfigure(3, weight=1)
move_page_frame.grid_columnconfigure(4, weight=1)
# Previous page button
previous_page = Button(move_page_frame, text="<", bg="white", fg='black', font=NORMAL,
                       state='disabled', command=view_previous_page)
previous_page.grid(row=0, column=1, padx=10)
# page label
page_label = Label(move_page_frame, text="Page: ", fg='black', bg='grey', font=NORMAL)
page_label.grid(row=0, column=2, padx=10)
# Next page button
next_page = Button(move_page_frame, text=">", bg="white", fg='black', font=NORMAL,
                   state='disabled', command=view_next_page)
next_page.grid(row=0, column=3, padx=10)

# frame for pdf text and audio control
audio_frame = Frame(bottom_frame, bg='grey')
audio_frame.grid(row=0, column=1, sticky="ew")
audio_frame.grid_rowconfigure(0, weight=1)
audio_frame.grid_columnconfigure(0, weight=1)
audio_frame.grid_columnconfigure(1, weight=1)
audio_frame.grid_columnconfigure(2, weight=0)
audio_frame.grid_columnconfigure(3, weight=0)
audio_frame.grid_columnconfigure(4, weight=0)
# play audio button
audio_button = Button(audio_frame, text="Play Audio", bg="white", fg='black', font=NORMAL,
                      border=0, state='disabled', command=text_to_voice)
audio_button.grid(row=0, column=0, sticky='e', padx=10)
# stop audio button
stop_audio_button = Button(audio_frame, text="Stop Audio", bg="white", fg='black', font=NORMAL,
                           border=0, state='disabled', command=stop_audio)
stop_audio_button.grid(row=0, column=1, sticky='w')
# decrease text size button
decrease_button = Button(audio_frame, text="-", bg="white", fg='black', font=NORMAL,
                         border=0, state='disabled', command=decrease_font_size)
decrease_button.grid(row=0, column=2, sticky='e')
# font size label
size_label = Label(audio_frame, text="Text Size", bg='grey', fg='black', font=NORMAL)
size_label.grid(row=0, column=3, padx=0)
# increase text size button
increase_button = Button(audio_frame, text="+", bg="white", fg='black', font=NORMAL,
                         border=0, state='disabled', command=increase_font_size)
increase_button.grid(row=0, column=4, sticky='w')


# initialise helper class objects - - - - - - - - - - - - - - - - - -
images_pdf = PdfImage(pdf_main_frame, pdf_frame, text_box)  # PDFfile
text_pdf = TextPDF(text_box)  # PDFtext
audio_pdf = AudioPDF(AUDIO_FOLDER)  # PDFaudio


if __name__ == "__main__":
    root.mainloop()