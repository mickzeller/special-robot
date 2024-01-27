import random
from calendar import day_name
from datetime import datetime
from typing import Dict, Tuple

import pyttsx3
import platform

import speech_recognition as sr
from gtts import gTTS


def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        response = recognize_speech_from_mic(recognizer, microphone)
        if response["success"]:
            speech = response["transcription"]
            if wake_word_is_present_in(speech):
                assistant_response(greeting(response))
                if "date" in speech:
                    assistant_response(get_date_today())
                if is_who_is_phrase(speech, 0):
                    person = get_person_after_who_is(speech)
                    assistant_response("I don't know who {} is.".format(person))
            else:
                assistant_response("Sorry, I didn't catch that. Can you please repeat?")
        else:
            assistant_response(response["error"])


def handle_recognition_errors(error: Exception) -> Tuple[bool, str]:
    if isinstance(error, sr.RequestError):
        return False, "API unavailable"
    if isinstance(error, sr.UnknownValueError):
        return None, "Unable to recognize speech"
    raise error


def recognize_speech_from_mic(
    recognizer: sr.Recognizer, mic: sr.Microphone
) -> Dict[str, str or bool]:
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`speech_identifier` must be a `Recognizer` instance")
    if not isinstance(mic, sr.Microphone):
        raise TypeError("`microphone` must be a `Microphone` instance")

    with mic as source:
        audio = recognizer.listen(source)
        response = {"success": True, "error": None, "transcription": None}
        try:
            response["transcription"] = recognizer.recognize_google(audio)
        except (sr.RequestError, sr.UnknownValueError) as e:
            response["success"], response["error"] = handle_recognition_errors(e)
        return response


def init_engine():
    engine_name = (
        "sapi5"
        if platform.system() == "Windows"
        else "nsss" if platform.system() == "Darwin" else "espeak"
    )
    return pyttsx3.init(driverName=engine_name)


def assistant_response(input_text: str) -> None:
    text_2_speech = gTTS(text=input_text, lang="en", slow=False)
    engine = init_engine()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[33].id)
    engine.say(text_2_speech.text)
    engine.runAndWait()


def wake_word_is_present_in(speech: str) -> bool:
    WAKE_WORDS = ["hey computer", "okay computer"]
    speech = speech.lower()
    for phrase in WAKE_WORDS:
        if phrase in speech:
            return True
    return False


def get_date_today() -> str:
    now = datetime.now()
    today = datetime.today()
    weekday = day_name[today.weekday()]
    return "Today is {} {}.".format(
        weekday, formatted_ordinal_response("%B the {S}, %Y", now)
    )


def get_ordinal_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return "th"
    else:
        # Calculate the last digit of the day.
        last_digit = day % 10

        # Assign suffix based on the last digit of the day.
        ordinal_suffixes = {1: "st", 2: "nd", 3: "rd"}
        suffix = ordinal_suffixes.get(last_digit, "th")

        return suffix


def formatted_ordinal_response(format_date: str, current_time: datetime) -> str:
    return current_time.strftime(format_date).replace(
        "{S}", str(current_time.day) + get_ordinal_suffix(current_time.day)
    )


def greeting(speech: Dict[str, str or bool]) -> str:
    if not speech["error"]:
        GREETINGS = ["hi", "hey", "hello"]
        GREETINGS_RESPONSES = [
            "Hi {}! What's up?".format("Mick"),
            "{}, you're awesome! What's going on?".format("Mick"),
            "What's good {}?".format("Mick"),
        ]
        for greeting_response in speech["transcription"].split():
            if greeting_response.lower() in GREETINGS:
                return random.choice(GREETINGS_RESPONSES)
        return ""


def opening_greeting() -> None:
    hour = int(datetime.now().hour)
    if 0 <= hour < 12:
        assistant_response("Good Morning! How may I help you ?")
    elif 12 <= hour < 18:
        assistant_response("Good Afternoon! How may I help you ?")
    else:
        assistant_response("Good Evening! How may I help you ?")


WHO_IS_PHRASE = ["who", "is"]


def is_who_is_phrase(word_list: list[str], index: int) -> bool:
    return word_list[index : index + 2] == WHO_IS_PHRASE


def get_person_after_who_is(speech: str) -> str:
    word_list = speech.lower().split()
    for i, _ in enumerate(word_list):
        if is_who_is_phrase(word_list, i) and i + 3 < len(word_list):
            return word_list[i + 2] + " " + word_list[i + 3]


print("Say Hi computer! 👋")
opening_greeting()
assistant_response("Hi " + "Mick" + "! " + get_date_today())


if __name__ == "__main__":
    main()
