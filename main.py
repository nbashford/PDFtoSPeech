import pymupdf # imports the pymupdf library
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

import PDFfile

PDF_FOLDER = "./pdf_folder"
CURRENT_FILE = None
CURRENT_IMAGE = None
TK_IMAGE = None
TK_IMAGES_LIST = None
text_pages = {}


"""
possible additions: 

- make into separate classes - organisation 
- make an option for more simple text-to-speech 
- - give option and show warning that it will take longer to generate. 

what classes are there: 
main 
load / sizing pdf 
text
update variables

"""
"""
Processing Image Functions: 

def get_images_from_file(file):  #, last_page=10):
    return convert_from_path(file, first_page=1)
    
    
def resize_images(image_list):
    pil_image = image_list[0]

    # 2. need to get the width and height of the canvas frame
    max_width = pdf_main_frame.winfo_width()
    max_height = pdf_main_frame.winfo_height()

    aspect_ratio = min(max_width / pil_image.width, max_height / pil_image.height)
    # 3. change the width and height based on aspect ratio
    new_width = int(pil_image.width * aspect_ratio)
    new_height = int(pil_image.height * aspect_ratio)

    for i in range(len(image_list)):
        image_list[i] = image_list[i].resize((new_width, new_height), Image.LANCZOS)

    return new_width, new_height


"""

# -----
def get_images_from_file(file):  #, last_page=10):
    """
    IN PDF
    """
    return convert_from_path(file, first_page=1)


def resize_images(image_list):
    pil_image = image_list[0]

    # 2. need to get the width and height of the canvas frame
    max_width = pdf_main_frame.winfo_width()
    max_height = pdf_main_frame.winfo_height()

    aspect_ratio = min(max_width / pil_image.width, max_height / pil_image.height)
    # 3. change the width and height based on aspect ratio
    new_width = int(pil_image.width * aspect_ratio)
    new_height = int(pil_image.height * aspect_ratio)

    for i in range(len(image_list)):
        image_list[i] = image_list[i].resize((new_width, new_height), Image.LANCZOS)

    return new_width, new_height


def create_tk_image_list(image_list):

    tk_images = []
    for img in image_list:
        tk_img = ImageTk.PhotoImage(img)
        tk_images.append(tk_img)
    return tk_images


def display_img_page(page=0): # width, height,
    global CURRENT_IMAGE, TK_IMAGE
    if CURRENT_IMAGE and TK_IMAGE:
        CURRENT_IMAGE = None
        TK_IMAGE = None
    TK_IMAGE = TK_IMAGES_LIST[page]
    # CURRENT_IMAGE = pdf_frame.create_image(width // 2, height // 2, image=tk_image)
    CURRENT_IMAGE = pdf_frame.create_image(0, 0, image=TK_IMAGE, anchor="nw")


def increase_font_size():
    global RESIZED_FONT
    RESIZED_FONT[1] = RESIZED_FONT[1] + 1
    insert_text(alt_size=True)

def decrease_font_size():
    global RESIZED_FONT
    if RESIZED_FONT[1] > 1:
        RESIZED_FONT[1] = RESIZED_FONT[1] - 1
    insert_text(alt_size=True)


def current_page_text():
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



def get_img_page_num():
    current_img_index = TK_IMAGES_LIST.index(TK_IMAGE)
    return current_img_index

# From above here

def view_next_page():

    current_page = get_img_page_num()
    if current_page + 1 == len(TK_IMAGES_LIST):
        next_page = 0
    else:
        next_page = current_page + 1

    display_img_page(next_page)
    update_page_num_label(next_page + 1)
    insert_text()


def view_previous_page():

    current_page = get_img_page_num()
    prev_page = current_page - 1

    if prev_page < 0:
        prev_page = len(TK_IMAGES_LIST) - 1

    display_img_page(prev_page)
    update_page_num_label(prev_page + 1)
    insert_text()


def update_page_num_label(num=1):
    page_label.config(text=f"Page: {num}", fg="black")



def show_pdf_image(canvas_frame):
    """
    In PDF
    """
    global TK_IMAGE, TK_IMAGES_LIST

    if CURRENT_FILE:
        if TK_IMAGES_LIST:
            TK_IMAGES_LIST.clear()
            TK_IMAGES_LIST = None# This removes references to the images in the list
            TK_IMAGE = None  # Set the current image to None


        images = get_images_from_file(CURRENT_FILE)  # gets all PIL images from PDF files
        new_width, new_height = resize_images(images)  # resizes PIL images to fit canvas
        TK_IMAGES_LIST = create_tk_image_list(images)  # holds TK photo images of loaded PDF pages
        display_img_page() #new_width, new_height)  # show image on canvas

        update_page_num_label()  # update page number label
        get_all_text()  # retrieve all texts from PDF files
        insert_text()  # display the new pages text

        # create_audio_files()  # creates audio files for each page
        create_audio_files_threaded()

        update_current_file_label()

        canvas_frame.config(width=new_width, height=new_height)
        pdf_main_frame.config(width=new_width, height=new_height)
        root.update_idletasks()





def create_pdf_folder():

  if not os.path.isdir(PDF_FOLDER):
    os.mkdir(PDF_FOLDER)

def ensure_equal_frame_sizes(pdf_frame, text_frame, parent_frame):
    middle_width = parent_frame.winfo_width()
    half_width = middle_width // 2

    pdf_frame.config(width=half_width)
    text_frame.config(width=half_width)

def component_switch(frame1, frame2):

    frame1.grid_remove()
    frame2.grid(row=1, column=0, sticky="nsew")
    root.update_idletasks()  # Ensure layout calculations are done
    ensure_equal_frame_sizes(frame2, text_frame, middle_frame)


def open_pdf_file():
    global CURRENT_FILE

    filepath = filedialog.askopenfile(title="Select PDF file",
                                    defaultextension='pdf',
                                    filetypes=[('PDF files', '*.pdf')])

    if filepath:

        source_path = filepath.name
        filename = source_path.split('/')[-1]
        destination_path = f"{PDF_FOLDER}/{filename}"

        if filename not in os.listdir(PDF_FOLDER):
            shutil.copy(source_path, destination_path)
            # if not CURRENT_FILE: # i.e. pdf already showing - don't switch frames
            #     switch_next_page_state()
            #     switch_play_audio_state()
            #     switch_text_size_state()

                #show_pdf_image(pdf_frame)  # show the pdf and everything else
            if not CURRENT_FILE:
                component_switch(pdf_temp_frame, pdf_main_frame)
                switch_next_page_state()
                switch_play_audio_state()
                switch_text_size_state()
            else:
                reset_text_pages()
                extracted_icon.config(text='□')
            CURRENT_FILE = destination_path

            # switch_next_page_state()
            # switch_play_audio_state()
            # switch_text_size_state()
            show_pdf_image(pdf_frame)

        else: #filename already loaded1
            messagebox.showinfo(title="Loaded",
                                message="File already loaded")
            raise FileExistsError

    else:
        print("No file selected")

"""
get all the audio files of each page created before displaying the pdf files 
"""
audio_folder = "./audio_folder"
if not os.path.isdir(audio_folder):
    os.mkdir(audio_folder)


def save_audio(audio, file_name):
    audio.save(f"{audio_folder}/{file_name}.mp3")


def get_audio(text):
    return gTTS(text, lang='en')


'''

issue - the new thread is starting as the old thread is still finishing, making some 
of the variables unsafe - i.e. the page number 

- solution / workaround - limit the number of pages audio can generate initially 
- or simply make a new thread for each single audio page 
- i.e. when user presses 'play audio'
- thread is created that gets only that page numbers text and audio and saves it 
- 

'''


stop_event = threading.Event()
audio_thread = None
def generate_audio_files_with_feedback():
    # status_label.config(text="Creating audio files, please wait...")
    saved_audio = None
    for page in text_pages:
        if stop_event.is_set():
            print("previous thread stopped")
            return
        text = text_pages[page]
        text_audio = get_audio(text)
        update_extracted_text_label(page + 1)
        filename = CURRENT_FILE.split('/')[-1].split('.')[0]
        audio_filename = f"{filename}_{page}"
        save_audio(text_audio, audio_filename)
    # update_extracted_text_label(page+1)
    extracted_icon.config(text='✓')

    # status_label.config(text="Audio files created successfully!")

def create_audio_files_threaded():
    """
    1st called
    """
    global audio_thread, stop_event
    if audio_thread and audio_thread.is_alive():
        print("Stopping previous thread...")
        stop_event.set()  # Signal the previous thread to stop
        audio_thread.join()  # Wait for the thread to stop

    stop_event.clear()
    audio_thread = threading.Thread(target=generate_audio_files_with_feedback)
    audio_thread.daemon = True
    audio_thread.start()

def get_page_mp3():
    current_page = get_img_page_num()
    # now need to get the file name
    current_filename = CURRENT_FILE.split('/')[-1].split('.')[0]
    audio_file_path = f"{audio_folder}/{current_filename}_{current_page}.mp3"
    return audio_file_path


def delete_all_mp3_file():
    for audio in os.listdir(audio_folder):
        os.remove(audio)


pygame.mixer.init()
current_playing_file = None


def text_to_voice():
    """
    Converts text to speech and plays the audio in a separate thread.
    """
    try:
        audio = get_page_mp3()
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        audio_button.config(state='disabled')
        stop_audio_button.config(state='active')
    except pygame.error:
        messagebox.showinfo(title="Still Loading",
                            message="Audio data still loading. Please wait")


def stop_audio():
    pygame.mixer.music.stop()
    audio_button.config(state='active')
    stop_audio_button.config(state='disabled')


def update_current_file_label():
    current_file.config(text=CURRENT_FILE.split('/')[-1].split('.')[0])


def update_extracted_text_label(current_page=0):
    print("In here")
    total_pages = len(TK_IMAGES_LIST)
    page_status = f"{current_page}/{total_pages}"
    text_extracted_label.config(text=f"Audio Extracted: {page_status}")
    print(page_status)


def reset_text_pages():
    global text_pages
    text_pages = {}

def get_all_text():

    global text_pages
    """
    Now need some function to call to pass the page of text to
    - pass the text for each page
    
    - this gets ALL texts - could maybe call this when the pdf image is loaded 
    """
    doc = fitz.open(CURRENT_FILE) # open a document
    for page_num, page in enumerate(doc): # iterate the document pages
        pdf_string = None
        text = page.get_text() # get plain text encoded as UTF-8
        if not text:
            pdf_string = "The loaded PDF has no text metadata. It is likely not a true PDF."
        else:
            pdf_string = text

        text_pages[page_num] = pdf_string
        # pages.append(pdf_string)

        # text_to_voice(pdf_string)
        print(text)
        # break


TITLE = ("Georgia", 30, "bold")
NORMAL = ("Georgia", 15)
RESIZED_FONT = ["Georgia", 15]
SMALL = ("Georgia", 12)

root = Tk()
root.title("PDF to Speech")
root.geometry("1000x850")
root.minsize(width=1000, height=850)
# root.resizable(False, False)
root.config(padx=20, pady=20, bg="white")



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
load_button_top = Button(file_frame, text="Load PDF", bg='white', fg='black', font=NORMAL,
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
pdf_temp_frame = Frame(middle_frame, bg='white') # -----initial placeholder frame for pdf -------
pdf_temp_frame.grid(row=1, column=0, sticky='nsew')
pdf_temp_frame.grid_propagate(False)
# load button for PDF:
load_pdf_button = Button(pdf_temp_frame, text="Load PDF", bg='blue', fg='black', font=NORMAL,
                         command=open_pdf_file)
load_pdf_button.place(relx=0.5, rely=0.4, anchor='center')

pdf_main_frame = Frame(middle_frame, bg='white')  # ------ MAIN PDF Frame (LEFT) ----------------
# pdf_temp_frame.grid(row=1, column=0, sticky='nsew')
pdf_temp_frame.grid_propagate(False)

pdf_frame = Canvas(pdf_main_frame, bg='white')   # -- MAIN PDF CANVAS ------
pdf_frame.pack(fill='both', expand=True)
pdf_frame.grid_propagate(False)

"""
want message box saying to please wait 

- if pdf file > 5 pages - do not load the entire mp3 audio 
- instead do a page at a time when requested 

- maybe i can run the gTTs as a thread - so it doesn't block 
"""




text_frame = Frame(middle_frame, bg='lightgrey', width=middle_frame.winfo_width()//2)    # ---- TEXT FRAME (Right) ---
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
bottom_frame = Frame(root, height=50, bg='white')  # Set a fixed height (adjust as needed)
bottom_frame.pack(fill="x", pady=10)  # Remove expand=True and set only fill="x"

bottom_frame.grid_rowconfigure(0, weight=0)  # Prevent row from expanding
bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)
bottom_frame.grid_propagate(True)  # Let the frame adjust naturally to its content

move_page_frame = Frame(bottom_frame, bg='white')  # Buttons inside bottom frame
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

page_label = Label(move_page_frame, text="Page: ", fg='grey', bg='white', font=NORMAL)
page_label.grid(row=0, column=2, padx=10)


audio_frame = Frame(bottom_frame, bg='white')  # Buttons inside bottom frame
audio_frame.grid(row=0, column=1, sticky="ew")  # Adjust padding as needed
# audio_frame.grid_propagate(False)
audio_frame.grid_rowconfigure(0, weight=1)
audio_frame.grid_columnconfigure(0, weight=1)
audio_frame.grid_columnconfigure(1, weight=1)
audio_frame.grid_columnconfigure(2, weight=0)
audio_frame.grid_columnconfigure(3, weight=0)
audio_frame.grid_columnconfigure(4, weight=0)

audio_button = Button(audio_frame, text="Play Audio", bg="white", fg='black', font=NORMAL,
                      state='disabled', command=text_to_voice)
audio_button.grid(row=0, column=0, sticky='e')

stop_audio_button = Button(audio_frame, text="Stop Audio", bg="white", fg='black', font=NORMAL,
                      state='disabled', command=stop_audio)
stop_audio_button.grid(row=0, column=1, sticky='w')

decrease_button = Button(audio_frame, text="-", bg="white", fg='black', font=NORMAL,
                      state='disabled', command=decrease_font_size)
decrease_button.grid(row=0, column=2, sticky='e')

size_label = Label(audio_frame, text="Text Size", bg='white', fg='black', font=NORMAL)
size_label.grid(row=0, column=3, padx=0)

increase_button = Button(audio_frame, text="+", bg="white", fg='black', font=NORMAL,
                      state='disabled', command=increase_font_size)
increase_button.grid(row=0, column=4, sticky='w')



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



if __name__=="__main__":
    create_pdf_folder()
    root.mainloop()

# text_to_voice("Just go you pussy")

# middle bit to upload files

# option to save just the text or the file?

# want to be able to see the PDF displayed - PIL to be used
# want the first button to extract the text from the pdf file
# want to be able to have the text shown on the screen for the user to view
# want a button for the user to press to convert text to Speech


#
"""
def text_to_voice(text=None):

    #Converts text to speech and plays the audio in a separate thread.
    
    if not text:
        text = current_page_text()

    def play_audio():
        # global cancel_audio
        # Initialize gTTS with the text to convert
        speech = gTTS(text, lang='en')  # Adjust parameters as needed
        speech_file = 'speech.mp3'
        speech.save(speech_file)

        # Play the audio file
        os.system(f'afplay "{speech_file}"')

        # Optionally delete the audio file after playing
        os.remove(speech_file)

        # if cancel_audio:
        #     print("audio stopped")
        #     return

    # Start the audio playback in a separate thread
    playback_thread = threading.Thread(target=play_audio)
    playback_thread.daemon = True  # Ensures thread exits when the app closes
    playback_thread.start()

"""