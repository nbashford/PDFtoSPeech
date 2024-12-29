from gtts import gTTS
import threading
import pygame

from tkinter import filedialog, messagebox
import os


"""
- make a function that can simply get the gTTs audio for the individual page text
- and play that instead - no need to save
# def generate_audio_files_with_feedback(text_pages, current_file):
#     make another function like above
#     but instead makes a single mp3 for that page and does NOT save it

- make a setting/functionality so that the user can select the local text speech generation 
- instead of gTTs

"""


class AudioPDF:

    def __init__(self, audio_folder, extracted_label, extracted_icon):
        self.audio_folder = audio_folder
        self.text_pages = None
        self.current_file = None
        self.current_page = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        self.extracted_label = extracted_label
        self.extracted_icon = extracted_icon
        pygame.mixer.init()

    # ---- below 4 functions gets the audio files from the texts


    def create_audio_files_threaded(self, text_pages, current_file):
        """
        ENTRY
        """
        self.text_pages = text_pages
        self.current_file = current_file

        if self.audio_thread and self.audio_thread.is_alive():  #
            print("Stopping previous thread...")
            self.stop_event.set()  # Signal the previous thread to stop
            self.audio_thread.join()  # Wait for the thread to stop

        self.stop_event.clear()
        self.audio_thread = threading.Thread(target=self.generate_audio_files_with_feedback)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def generate_audio_files_with_feedback(self):
        """
        AUDIO
        NEEDS CURRENT_FILE and TEXT PAGES dict
        """
        for page, text in self.text_pages.items():
            if self.stop_event.is_set():
                print("previous thread stopped")
                return

            text_audio = self.get_audio(text)
            self.update_extracted_text_label(page + 1)

            filename = self.current_file.split('/')[-1].split('.')[0]
            audio_filename = f"{filename}_{page}"
            self.save_audio(text_audio, audio_filename)

        self.extracted_icon.config(text='✓')

    def save_audio(self, audio, file_name):
        audio.save(f"{self.audio_folder}/{file_name}.mp3")

    def get_audio(self, text):
        return gTTS(text, lang='en')

    def update_extracted_text_label(self, current_page=0):
        """
        MAIN
        Needs TK_IMAGES from PDFfile

        """
        total_pages = len(self.text_pages)
        page_status = f"{current_page}/{total_pages}"
        self.extracted_label.config(text=f"Audio Extracted: {page_status}")
        # print(page_status)



    # --------- Below functions control the playing and stopping of the audio

    def text_to_voice(self, current_page, current_file):  # PLAY
        """
        ENTRY
        Converts text to speech and plays the audio in a separate thread.
        """
        try:
            self.current_page = current_page
            self.current_file = current_file
            audio = self.get_page_mp3()
            pygame.mixer.music.load(audio)
            pygame.mixer.music.play()
            return True
        except pygame.error:
            messagebox.showinfo(title="Still Loading",
                                message="Audio data still loading. Please wait")
            return False

    def get_page_mp3(self):
        """
        """
        filename = self.current_file.split('/')[-1].split('.')[0]
        audio_file_path = f"{self.audio_folder}/{filename}_{self.current_page}.mp3"
        return audio_file_path

    def stop_audio(self):
        """ENTRY"""
        pygame.mixer.music.stop()

    def delete_all_mp3_file(self):
        """AUDIO"""
        for audio in os.listdir(self.audio_folder):
            os.remove(audio)

