
# FULL APP WITH GEMINI + VOICE

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.clock import Clock
import threading
import os

import vosk
import pyaudio
import json

from google import genai
import gtts
import pygame

Window.clearcolor = (0.35, 0.35, 0.35, 1)

client = genai.Client(
    api_key="sk-M9XQpAX5DdThdJYMoMypH1QCaEOF8nCI", http_options={"base_url": "https://api.proxyapi.ru/google"}
)


def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    os.remove(filename)


class ImageButton(ButtonBehavior, Image):
    pass


class MainLayout(BoxLayout):
    mic_on = BooleanProperty(False)
    status_text = StringProperty("Статус: микрофон не подключен.")
    command_text = StringProperty("")
    recognized_text = StringProperty("")
    ai_response = StringProperty("")

    def toggle_mic(self):
        self.mic_on = not self.mic_on
        self.update_mic_ui()

        if self.mic_on:
            threading.Thread(target=self.start_recognition, daemon=True).start()

    def update_mic_ui(self):
        if self.mic_on:
            self.ids.mic.source = "mic_on.png"
            self.status_text = "Статус: микрофон подключен."
        else:
            self.ids.mic.source = "mic_off.png"
            self.status_text = "Статус: микрофон не подключен."

    def update_command_from_text(self, text):
        for cmd in ["начало", "конец", "добавить", "выход"]:
            if cmd in text.lower():
                self.command_text = cmd
                break

    def start_recognition(self):
        model = vosk.Model("vosk-model-small-ru-0.22")
        rec = vosk.KaldiRecognizer(model, 16000)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True, frames_per_buffer=4000)

        while self.mic_on:
            data = stream.read(4000, exception_on_overflow=False)

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    Clock.schedule_once(lambda dt: self.process_text(text))

        stream.stop_stream()
        stream.close()
        p.terminate()

    def process_text(self, text):
        self.recognized_text = text
        self.update_command_from_text(text)

        threading.Thread(target=self.get_ai_response, args=(text,), daemon=True).start()

    def get_ai_response(self, text):
        try:
            chat = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Отвечай кратко: {text}"
            )

            answer = chat.candidates[0].content.parts[0].text

            Clock.schedule_once(lambda dt: setattr(self, 'ai_response', answer))

            tts = gtts.gTTS(text=answer, lang='ru')
            filename = "voice.mp3"
            tts.save(filename)

            play_audio(filename)

        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self, 'ai_response', f"Ошибка: {e}"))


class MicApp(App):
    def build(self):
        root = MainLayout(orientation='vertical', padding=20, spacing=15)

        mic = ImageButton(source="mic_off.png", size_hint=(1, 0.35))
        mic.bind(on_press=lambda x: root.toggle_mic())
        mic.id = "mic"
        root.ids = {"mic": mic}

        status = Label(text=root.status_text, size_hint=(1, 0.08))
        root.bind(status_text=lambda inst, val: setattr(status, 'text', val))

        command_label = Label(text="Текущая голосовая команда:", size_hint=(1, 0.08))
        command_box = Label(text=root.command_text, size_hint=(1, 0.08))
        root.bind(command_text=lambda inst, val: setattr(command_box, 'text', val))

        hint = Label(text="начало, конец, добавить, выход", size_hint=(1, 0.08))

        recognized_label = Label(text="Распознанный текст:", size_hint=(1, 0.08))
        recognized_output = TextInput(text=root.recognized_text, size_hint=(1, 0.2), readonly=True)
        root.bind(recognized_text=lambda inst, val: setattr(recognized_output, 'text', val))

        ai_label = Label(text="Полученный ответ от AI:", size_hint=(1, 0.08))
        ai_output = TextInput(text=root.ai_response, size_hint=(1, 0.2), readonly=True)
        root.bind(ai_response=lambda inst, val: setattr(ai_output, 'text', val))

        root.add_widget(mic)
        root.add_widget(status)
        root.add_widget(command_label)
        root.add_widget(command_box)
        root.add_widget(hint)
        root.add_widget(recognized_label)
        root.add_widget(recognized_output)
        root.add_widget(ai_label)
        root.add_widget(ai_output)

        return root


if __name__ == "__main__":
    MicApp().run()
