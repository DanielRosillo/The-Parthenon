#!/usr/bin/env python
import signal
from pynput.keyboard import Listener, Key
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from deep_translator import GoogleTranslator
from gtts import gTTS
import playsound
import os
import pyaudio
import wave
from pynput import keyboard
import keyboard as k
import pyperclip as clipboard

# create a speech recognition object
r = sr.Recognizer()

# a function that splits the audio file into chunks
# and applies speech recognition
def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 700,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=700,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, "chunk"+str(i)+".wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = text
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

filename = "key_log.txt"  # The file to write characters to

def on_press(key):
    f = open(filename, 'a')  # Open the file

    if hasattr(key, 'char'):  # Write the character pressed if available
        f.write(key.char)
        
        if(key.char == 'r' or key.char == 'R'):
            print("RECORD")
            record()

        elif(key.char == 'm' or key.char == 'M'):
            print("MAGIC")
            magic()

        elif(key.char == 'n' or key.char == 'N'):
            # Reproducimos la traduccion
            print("Reproduciendo traduccion")
            playsound.playsound('input.mp3')
        
        elif(key.char == 'b' or key.char == 'B'):
            # Reproducimos la traduccion
            copy()

    elif key == Key.space:  # If space was pressed, write a space
        f.write(' ')
    elif key == Key.enter:  # If enter was pressed, write a new line
        f.write('\n')
    elif key == Key.tab:  # If tab was pressed, write a tab
        f.write('\t')
    else:  # If anything else was pressed, write [<key_name>]
        f.write('[' + key.name + ']')

    f.close()  # Close the file


def magic():
    path = "output.wav"
    # Sacamos el texto del audio
    text = get_large_audio_transcription(path)
    print("\nFull text:" + text)
    # Traducimos el texto
    translated = GoogleTranslator(source='auto', target='es').translate(text)
    print(translated)
    # Creamos una lectura del texto traducido con voz femenina
    isExist = os.path.exists("input.mp3")
    if isExist:
        os.remove("input.mp3")
    tts = gTTS(translated, lang='es-us')
    tts.save("input.mp3")
    # Reproducimos la traduccion
    print("Reproduciendo traduccion")
    playsound.playsound('input.mp3')

def record():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 50
    filename = "output.wav"
    playsound.playsound('flag.wav')
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    playsound.playsound('flag.wav')

def copy():
    print('copy')
    # Obtener contenido del portapapeles
    content = clipboard.paste()
    print(content)
    # Traducimos el texto
    translated = GoogleTranslator(source='auto', target='es').translate(content)
    print(translated)
    # Si existe el archivo lo borramos
    isExist = os.path.exists("text.mp3")
    if isExist:
        os.remove("text.mp3")
    
    # Creamos la lectura del texto con voz femenina
    tts = gTTS(translated, lang='es-us')
    tts.save("text.mp3")
    # Reproducimos la traduccion
    print("Reproduciendo traduccion")
    playsound.playsound("text.mp3")

if __name__ == '__main__':

    with Listener(on_press=on_press) as listener:  # Setup the listener
        listener.join()  # Join the thread to the main thread