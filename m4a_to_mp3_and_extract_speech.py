# %%

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
from threading import Thread

# Import pydub for audio conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    messagebox.showerror("Error", "Pydub library not found. Please install it using: pip install pydub")

# Import whisper for STT
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    messagebox.showerror("Error", "Whisper library not found. Please install it using: pip install openai-whisper")

class M4AtoMP3ConverterApp:
    def __init__(self, master):
        """
        Initializes the Tkinter application for M4A to MP3 conversion and STT.
        """
        self.master = master
        master.title("M4A to MP3 & Speech Extractor (Whisper)") # Updated title
        master.geometry("600x600") # Increased size to accommodate new widgets
        master.resizable(True, True) # Allow resizing for text area

        # Apply a modern style
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Configure styles for widgets
        self.style.configure('TFrame', background='#e0e0e0')
        self.style.configure('TLabel', background='#e0e0e0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)
        self.style.map('TButton',
                       background=[('active', '#6a5acd')], # Lavender for active
                       foreground=[('active', 'white')])
        self.style.configure('TEntry', padding=5, font=('Arial', 10))
        self.style.configure('TProgressbar', thickness=20, troughcolor='#d3d3d3',
                             background='#8a2be2', bordercolor='#8a2be2') # BlueViolet
        self.style.configure('TScrolledtext', background='white', font=('Arial', 9))

        # Main Frame for padding and background
        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.title_label = ttk.Label(self.main_frame, text="M4A to MP3 & Speech Extractor",
                                     font=('Arial', 18, 'bold'), anchor='center')
        self.title_label.pack(pady=(0, 20))

        # Input File Selection
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.input_frame, text="Input M4A File:").pack(side=tk.LEFT, padx=(0, 10))
        self.input_path = ttk.Entry(self.input_frame, width=40)
        self.input_path.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.browse_input_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_input_file)
        self.browse_input_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Output File Selection (for MP3 conversion)
        self.output_frame = ttk.Frame(self.main_frame)
        self.output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.output_frame, text="Output MP3 File:").pack(side=tk.LEFT, padx=(0, 10))
        self.output_path = ttk.Entry(self.output_frame, width=40)
        self.output_path.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.browse_output_button = ttk.Button(self.output_frame, text="Browse", command=self.browse_output_file)
        self.browse_output_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Action Buttons Frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        # Convert Button
        self.convert_button = ttk.Button(self.button_frame, text="Convert to MP3", command=self.start_conversion_thread)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5)

        # Extract Speech Button
        self.extract_speech_button = ttk.Button(self.button_frame, text="Extract Speech", command=self.start_speech_extraction_thread)
        self.extract_speech_button.pack(side=tk.LEFT, padx=(10, 0), ipadx=10, ipady=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.stop() # Hide it initially

        # Status Label
        self.status_label = ttk.Label(self.main_frame, text="", foreground="blue", font=('Arial', 10, 'italic'))
        self.status_label.pack(pady=(0, 10))

        # Speech Output Label and Text Area
        ttk.Label(self.main_frame, text="Extracted Speech:", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        self.speech_output_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=10, width=60)
        self.speech_output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.speech_output_text.config(state=tk.DISABLED) # Make read-only

        # Load Whisper model once
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.update_status("Loading Whisper model (base)... This may take a moment.", "purple")
                self.whisper_model = whisper.load_model("base")
                self.update_status("Whisper model loaded.", "green")
            except Exception as e:
                self.update_status(f"Error loading Whisper model: {e}", "red")
                self.whisper_model = None


    def browse_input_file(self):
        """Opens a file dialog to select the input M4A file."""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(("Audio files", "*.m4a *.mp3 *.wav"), ("M4A files", "*.m4a"), ("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if file_path:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, file_path)
            # Suggest output file name based on input
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            self.output_path.delete(0, tk.END)
            # Default to saving MP3 in the same directory as input
            self.output_path.insert(0, os.path.join(os.path.dirname(file_path), f"{name_without_ext}.mp3"))
            self.update_status("")
            self.speech_output_text.config(state=tk.NORMAL)
            self.speech_output_text.delete(1.0, tk.END) # Clear previous speech output
            self.speech_output_text.config(state=tk.DISABLED)


    def browse_output_file(self):
        """Opens a file dialog to select/specify the output MP3 file."""
        file_path = filedialog.asksaveasfilename(
            title="Save MP3 File As",
            defaultextension=".mp3",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if file_path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, file_path)
            self.update_status("")

    def update_status(self, message, color="blue"):
        """Updates the status label with a given message and color."""
        self.status_label.config(text=message, foreground=color)
        self.master.update_idletasks() # Force update

    def set_buttons_state(self, state):
        """Helper function to set the state of all action buttons."""
        self.convert_button.config(state=state)
        self.browse_input_button.config(state=state)
        self.browse_output_button.config(state=state)
        self.extract_speech_button.config(state=state)

    def start_conversion_thread(self):
        """Starts the conversion process in a separate thread to keep the GUI responsive."""
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file:
            self.update_status("Please select an input audio file.", "red")
            return
        if not os.path.exists(input_file):
            self.update_status("Input file does not exist.", "red")
            return
        # Allow multiple audio formats for input
        if not (input_file.lower().endswith(".m4a") or input_file.lower().endswith(".mp3") or input_file.lower().endswith(".wav")):
            self.update_status("Input file must be M4A, MP3, or WAV.", "red")
            return

        if not output_file:
            self.update_status("Please specify an output MP3 file.", "red")
            return
        if not output_file.lower().endswith(".mp3"):
            self.update_status("Output file must have a .mp3 extension.", "red")
            return

        # Disable buttons and show progress
        self.set_buttons_state(tk.DISABLED)
        self.progress_bar.start(10) # Start indeterminate animation
        self.update_status("Conversion in progress... Please wait.")

        # Run conversion in a separate thread
        conversion_thread = Thread(target=self.convert_audio, args=(input_file, output_file))
        conversion_thread.start()

    def convert_audio(self, input_file, output_file):
        """
        Performs the audio conversion using pydub.
        This function runs in a separate thread.
        """
        if not PYDUB_AVAILABLE:
            self.update_status("Pydub library not available. Cannot convert.", "red")
            self.reset_ui()
            return

        try:
            # Determine input format from extension
            input_format = os.path.splitext(input_file)[1].lower().lstrip('.')
            if input_format == 'm4a':
                 # Explicitly handle M4A to ensure correct codec usage if necessary
                 audio = AudioSegment.from_file(input_file, format="m4a")
            elif input_format == 'mp3':
                 audio = AudioSegment.from_file(input_file, format="mp3")
            elif input_format == 'wav':
                 audio = AudioSegment.from_file(input_file, format="wav")
            else:
                 raise ValueError("Unsupported input format detected by pydub.")

            audio.export(output_file, format="mp3")
            self.update_status(f"Conversion successful! Output saved to: {output_file}", "green")
        except Exception as e:
            # Catch errors related to FFmpeg not being found/configured correctly
            error_message = str(e)
            if "Could not find ffmpeg or ffprobe" in error_message or "No such file or directory: 'ffprobe'" in error_message:
                self.update_status("Error: FFmpeg is not installed or not in your system's PATH. "
                                   "Please install FFmpeg and ensure it's accessible. For details, check the console.", "red")
                print(f"FFmpeg/FFprobe error: {e}") # Print full error for debugging
            else:
                self.update_status(f"An error occurred during conversion: {e}", "red")
        finally:
            self.reset_ui()

    def start_speech_extraction_thread(self):
        """Starts the speech extraction process in a separate thread."""
        input_file = self.input_path.get()

        if not input_file:
            self.update_status("Please select an input audio file for speech extraction.", "red")
            return
        if not os.path.exists(input_file):
            self.update_status("Input file does not exist.", "red")
            return
        if not (input_file.lower().endswith(".m4a") or input_file.lower().endswith(".mp3") or input_file.lower().endswith(".wav")):
            self.update_status("Speech extraction supports M4A, MP3, or WAV files.", "red")
            return

        if not WHISPER_AVAILABLE or self.whisper_model is None:
            self.update_status("Whisper library not available or model failed to load. Cannot extract speech.", "red")
            return

        # Clear previous speech output
        self.speech_output_text.config(state=tk.NORMAL)
        self.speech_output_text.delete(1.0, tk.END)
        self.speech_output_text.config(state=tk.DISABLED)

        # Disable buttons and show progress
        self.set_buttons_state(tk.DISABLED)
        self.progress_bar.start(10)
        self.update_status("Extracting speech... This might take a while for long audio.", "purple")

        # Run speech extraction in a separate thread
        speech_thread = Thread(target=self.extract_speech, args=(input_file,))
        speech_thread.start()

    def extract_speech(self, input_file):
        """
        Extracts speech from the audio file using Whisper.
        This function runs in a separate thread.
        """
        try:
            # Whisper can often directly handle various audio formats (M4A, MP3, WAV)
            # without explicit pydub conversion to WAV first for transcription.
            # This simplifies the process.

            result = self.whisper_model.transcribe(input_file, language="pt") # Use Portuguese language
            text = result["text"]

            self.speech_output_text.config(state=tk.NORMAL)
            self.speech_output_text.insert(tk.END, text)
            self.speech_output_text.config(state=tk.DISABLED)
            self.update_status("Speech extraction complete.", "green")

        except Exception as e:
            self.update_status(f"An error occurred during speech extraction: {e}", "red")
            self.speech_output_text.config(state=tk.NORMAL)
            self.speech_output_text.insert(tk.END, f"Error: {e}")
            self.speech_output_text.config(state=tk.DISABLED)
        finally:
            self.reset_ui()

    def reset_ui(self):
        """Resets the UI elements after conversion or error."""
        self.set_buttons_state(tk.NORMAL)
        self.progress_bar.stop()


# Main execution block
if __name__ == "__main__":
    root = tk.Tk()
    app = M4AtoMP3ConverterApp(root)
    root.mainloop()

# %%
