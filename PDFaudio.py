from gtts import gTTS
import threading
import pygame
import io
from tkinter import filedialog, messagebox
import os


class AudioPDF:
    def __init__(self, audio_folder):
        self.audio_folder = audio_folder
        self.text_pages = None  # dictionary of text
        self.current_file = None
        self.current_page = None  # current page being displayed
        self.audio_thread = None  # current running thread loading audio
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.audio_data = {}  # holds generated audio io.Bytes files
        self.current_page_loaded = 0  # counter for no. of pages of audio generated
        pygame.mixer.init()  # initialise the audio player

    def create_audio_files_threaded(self, text_pages, current_file):
        """
        Sets up a thread to generate all the TTS audio from the pdf texts.
        If called again whilst thread running - new thread waits for previous thread to finish.
        """

        if self.audio_thread and self.audio_thread.is_alive():  # if prev thread and running
            self.stop_event.set()  # stop signal
            self.audio_thread.join()  # Wait until thread stopped
            self.stop_event.clear()  # remove signal

        # setup for initialising thread
        self.text_pages = text_pages
        self.current_file = current_file
        self.reset_audio_bytes()

        self.stop_event.clear()
        # create the thread to generate TTS files
        self.audio_thread = threading.Thread(target=self.generate_audio_files_with_feedback_bytes)
        self.audio_thread.daemon = True
        self.audio_thread.start()


    def generate_audio_files_with_feedback_bytes(self):
        """
        called by thread. iterates over all pdf text, and Chunks each pdf text page,
        then generates TTS for each chunk and saves to an io.Bytes file (RAM).
        Multiple thread stop event flags to reduce thread.join() from blocking main app.
        """
        with self.lock:
            for page, text in self.text_pages.items():  # for each page of pdf
                audio_data = io.BytesIO()  # full page temp bytes file
                text_chunks = self.create_text_chunks(text)  # chunk text
                if self.stop_event.is_set():
                    return
                for chunk in text_chunks:   # for each chunk in page
                    tts = gTTS(chunk, lang='en')  # get TTS
                    if self.stop_event.is_set():
                        return
                    temp_audio = io.BytesIO()
                    tts.write_to_fp(temp_audio)  # write to intermediate bytes file
                    if self.stop_event.is_set():
                        return
                    temp_audio.seek(0)
                    audio_data.write(temp_audio.getvalue())  # write to full page temp bytes file
                    if self.stop_event.is_set():
                        return

                audio_data.seek(0)
                self.audio_data[page] = audio_data  # store the audio byte file to dictionary
                self.current_page_loaded += 1
                if self.stop_event.is_set():
                    return

    def create_text_chunks(self, text, chunk_size=100):
        """
        chunks text into chunks of 100 words.
        Returns list of text chunks.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        for word in words:
            # if over the chunk size - switch to new chunk and add next word
            if len(' '.join(current_chunk + [word])) > chunk_size:
                chunks.append(' '.join(current_chunk))  # concatenate words
                current_chunk = [word]
            else:  # add word to current chunk
                current_chunk.append(word)
        if current_chunk:
            chunks.append(' '.join(current_chunk))  # concatenate words

        return chunks



    def generate_audio_files_with_feedback_disk(self):
        """
        older function - not used currently - keep in case of use.
        Wrote TTS to disk - slower.
        Caution - errors in this.
        """
        for page, text in self.text_pages.items():
            if self.stop_event.is_set():
                print("previous thread stopped")
                return

            with self.lock:

                text_audio = self.get_audio(text)
                self.update_extracted_text_label(page + 1)

                filename = self.current_file.split('/')[-1].split('.')[0]
                audio_filename = f"{filename}_{page}"
                self.save_audio(text_audio, audio_filename)

        self.extracted_icon.config(text='✓')

    def save_audio(self, audio, file_name):
        """
        saves audio as mp3 file
        """
        audio.save(f"{self.audio_folder}/{file_name}.mp3")

    def get_audio(self, text):
        """returns TTS of passed text"""
        return gTTS(text, lang='en')

    def get_audio_bytes_file(self, text):
        """
        returns an io.Bytes file holding the TTS audio
        """
        audio_bytes = io.BytesIO()
        tts = gTTS(text, lang='en')
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes

    def reset_audio_bytes(self):
        """
        Resets dictionary holding previous audio byte files and current page tracker
        """
        if self.audio_data:
            for page in self.audio_data:
                self.audio_data[page].close()  # Close each BytesIO
            self.audio_data.clear()

        self.current_page_loaded = 0

    def text_to_voice(self, current_page, current_file):  # PLAY
        """
        gets the current pages audio file and plays the audio.
        If audio is not generated yet a warning is displayed.
        """
        try:
            self.current_page = current_page
            self.current_file = current_file

            audio = self.audio_data[current_page]  # get current page audio
            audio_copy = io.BytesIO(audio.getvalue())  # Create copy of audio
            audio_copy.seek(0)  # set pointer to beginning
            pygame.mixer.music.load(audio_copy, 'mp3')
            pygame.mixer.music.play()  # play the audio copy
            return True

        except (pygame.error, KeyError):
            messagebox.showinfo(title="Still Loading",
                                message="Audio data still loading. Please wait. "
                                        "\nCheck above at label 'Audio Pages Extracted' "
                                        "to identify if a page is ready to play.")
            return False

    def get_page_mp3(self):
        """gets the current mp3 file name based on current file name and page number"""
        filename = self.current_file.split('/')[-1].split('.')[0]
        audio_file_path = f"{self.audio_folder}/{filename}_{self.current_page}.mp3"
        return audio_file_path

    def stop_audio(self):
        """Stops the audio playing"""
        pygame.mixer.music.stop()

    def delete_all_mp3_file(self):
        """Deletes all audio mp3 stored in audio folder"""
        for audio in os.listdir(self.audio_folder):
            os.remove(audio)

    # def text_to_voice(self, text):  # PLAY
    #     """
    #     for passing the text directly to generate the audio and play
    #     """
    #     try:
    #
    #         tts = gTTS(text, lang='en')
    #         audio_data = io.BytesIO()
    #
    #         tts.write_to_fp(audio_data) # NEW
    #         # tts.save(audio_data)
    #         audio_data.seek(0)  # Go to the start of the BytesIO buffer
    #         pygame.mixer.music.load(audio_data, 'mp3')
    #         pygame.mixer.music.play()
    #         return True
    #     except pygame.error:
    #         messagebox.showinfo(title="Still Loading",
    #                             message="Audio data still loading. Please wait")
    #         return False