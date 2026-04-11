import vosk
import sys
import os
import pyaudio
import json
import pyttsx3
from google import genai
import gtts
import pygame

client = genai.Client(
    api_key="sk-M9XQpAX5DdThdJYMoMypH1QCaEOF8nCI", http_options={"base_url": "https://api.proxyapi.ru/google"}
)

# engine = pyttsx3.init()


def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Ждем пока играет музыка
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    os.remove(filename)  # Удаляем файл после воспроизведения

def recording(result):
    text_index = ""
    commands = ["начал", "добавить", "конец", "выход"]

    for i in commands:
        if i in result["text"]:
            if commands[0] in result["text"]:
                 text_index = result["text"]
            if commands[1] in result["text"]:
                text_index = text_index + result["text"]
            if commands[2] in result["text"]:
                 return text_index
        # elif i not in result["text"]:
        #     return 1
        if i in result["text"]:
            if commands[3] in result["text"]:
                return 0

def filtering_result(ans):
    filtering_words = ["начал", "добавить", "конец", None]
    delete_index = []
    str_1 = ans.split(" ")
    # print(str_1)
    for i in range(len(str_1)):
        if str_1[i] in filtering_words:
            delete_index.append(i)
    delete_index.sort(reverse=True)
    for i in delete_index:
        str_1.pop(i)

        ans = ' '.join(str_1)
    return ans
# Функция для распознавания речи с микрофона
def recognize_speech():
    recorded = []

    # Устанавливаем модель для русского языка
    model = vosk.Model("vosk-model-small-ru-0.22")

    # Создаем объект распознавания речи
    rec = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)

    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            # print(f"result = {result}")

            ans = recording(result)
            # print(ans)
            if ans == None:
                continue
            elif ans == 0:
                break
            else:
                filtered_result = filtering_result(ans)
                recorded.append(filtered_result)


                chat_completion = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents={f"Отвечай кратко но достуточно для раскрытия вопроса: {recorded}"},
                )

                tts = gtts.gTTS(text=chat_completion.candidates[0].content.parts[0].text, lang='ru', slow=False)
                filename = "smart_speech.mp3"
                tts.save(filename)

                play_audio(filename)

                # engine.say(chat_completion.candidates[0].content.parts[0].text)
                # engine.runAndWait()

                recorded.clear()


    stream.stop_stream()
    stream.close()
    p.terminate()


# Запускаем распознавание речи
recognize_speech()