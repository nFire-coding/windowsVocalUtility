import os
import subprocess
import pyttsx3
import vosk
import sounddevice as sd
import json
import queue
import concurrent.futures

def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    model_path = "C:\\Users\\bella\\Desktop\\Sfidona Morro\\vosk-model-small-it-0.22"
    model = vosk.Model(model_path)
	vosk.SetLogLevel(-1)
    q = queue.Queue()
  
    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        q.put(bytes(indata))
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")

def open_app(app_name):
    
    apps = {
        "notepad": "notepad.exe",
        "explorer": "explorer.exe",
        "terminale": "cmd.exe",
        "calcolatrice": "calc.exe",
        "paint": "mspaint.exe"
    }
    if app_name in apps:
        subprocess.run(apps[app_name])
        speak(f"Apro {app_name}")
    else:
        speak("Applicazione non trovata, prova con un altro nome.")

def search_files(keyword, root="C:\\"):
    matches = []
    def search_in_directory(directory):
        try:
            for folder, _, files in os.walk(directory):
                for file in files:
                    if keyword.lower() in file.lower():
                        matches.append((file, os.path.abspath(folder)))
        except PermissionError:
            pass
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.submit(search_in_directory, root)
    return list(set(matches))

def convert_number(text):
    numbers = {"uno": "1", "due": "2", "tre": "3", "quattro": "4", "cinque": "5", 
               "sei": "6", "sette": "7", "otto": "8", "nove": "9", "dieci": "10"}
    return numbers.get(text, text)

def find_file_interactive():
    speak("Cosa vuoi cercare?")
    filename = listen()
    if not filename:
        speak("Non ho capito il nome del file.")
        return
    speak(f"Sto cercando file contenenti {filename}, attendi...")
    results = search_files(filename)
    if not results:
        speak("Nessun file trovato.")
        return
    for i, (file, folder) in enumerate(results, 1):
        print(f"{i}. {folder} ({file})")
    while True:
        speak("Quale cartella vuoi aprire? Dimmi il numero.")
        choice = listen()
        choice = convert_number(choice)
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(results):
                subprocess.run(["explorer", results[choice - 1][1]])
                speak("Apro la cartella.")
                break
            else:
                speak("Numero non valido. Riprova.")
        else:
            speak("Non ho capito il numero. Riprova.")

def process_command(command):
    if "apri" in command:
        app_name = command.replace("apri", "").strip()
        open_app(app_name)
    elif "cerca" in command:
        find_file_interactive()
    elif "esci" in command:
        speak("Arrivederci!")
        exit()
    else:
        speak("Comando non riconosciuto.")

if __name__ == "__main__":
    engine = pyttsx3.init()
    speak("Ciao tesoro, benvenuto nel programma!")
    while True:
        cmd = listen()
        if cmd:
            process_command(cmd)