import speech_recognition as sr
from pydub import AudioSegment
import os
import nltk
import spacy
import re

# Download required NLP models
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nlp = spacy.load("en_core_web_sm")

def convert_audio_to_wav(input_file):
    """ Converts any audio file to WAV format compatible with SpeechRecognition """
    output_file = input_file.rsplit(".", 1)[0] + ".wav"  # Change extension to .wav
    try:
        audio = AudioSegment.from_file(input_file)  # Auto-detect format
        audio = audio.set_frame_rate(16000).set_channels(1)  # Convert to mono 16kHz
        audio.export(output_file, format="wav")  # Save as WAV
        return output_file, None  # Return file path and no error
    except Exception as e:
        return None, f"Audio conversion failed: {str(e)}"

def transcribe_audio(audio_path):
    """ Transcribes audio to text after ensuring it's in PCM WAV format """
    recognizer = sr.Recognizer()
    
    # Convert file if not already WAV
    if not audio_path.endswith(".wav"):
        audio_path, error = convert_audio_to_wav(audio_path)
        if error:
            return error  # Return conversion error

    try:
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Error: Could not understand the audio."
    except sr.RequestError:
        return "Error: Speech recognition service unavailable."
    except Exception as e:
        return f"Error: {str(e)}"

def extract_key_points(text):
    """ Extracts action items from transcribed text using NLP and returns full transcript """
    sentences = nltk.sent_tokenize(text)
    action_items = []

    # Expanded Task Keywords List
    task_keywords = [
        "should", "must", "need to", "have to", "required", "ensure", "schedule", "assign", "complete",
        "submit", "prepare", "finalize", "review", "implement", "organize", "send", "write", "discuss", "confirm",
        "approve", "plan", "analyze", "meet", "delegate", "provide", "update"
    ]

    # Noise words to ignore (Commonly misrecognized words)
    noise_words = ["eating", "um", "uh", "okay", "so", "alright", "like", "you know", "actually"]

    for sent in sentences:
        # Remove noise words from the start of the sentence
        sent = re.sub(rf"^({'|'.join(noise_words)})\s+", "", sent, flags=re.IGNORECASE).strip()
        doc = nlp(sent)

        # Extract verbs and check for action words
        action_verbs = [token.text for token in doc if token.pos_ == "VERB" or token.dep_ in ["xcomp", "acl"]]
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Identify action-based sentences
        if any(keyword in sent.lower() for keyword in task_keywords) or action_verbs:
            structured_task = f"\n🔹 **Task:** {sent.strip()}"
            action_items.append(structured_task)
            action_items.append("\n")

            # Capture relevant Named Entities
            for entity in entities:
                if entity[1] in ["DATE", "TIME", "PERSON", "ORG", "GPE", "MONEY"]:
                    action_items.append(f"    ➡ **Related to:** {entity[0]} ({entity[1]})")

    # Return both transcript and extracted tasks
    return {
        "transcribed_text": text,
        "extracted_tasks": "\n".join(action_items) if action_items else "**No clear action items found.**"
    }
