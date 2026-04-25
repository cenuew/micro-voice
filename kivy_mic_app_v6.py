
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.35, 0.35, 0.35, 1)


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

    def update_mic_ui(self):
        if self.mic_on:
            self.ids.mic.source = "mic_on.png"
            self.status_text = "Статус: микрофон подключен."
        else:
            self.ids.mic.source = "mic_off.png"
            self.status_text = "Статус: микрофон не подключен."

    def update_command_from_text(self, text):
        commands = ["начало", "конец", "добавить", "выход"]
        for cmd in commands:
            if cmd in text.lower():
                self.command_text = cmd
                break

    def simulate_recognition(self, dt):
        if self.mic_on:
            sample = "пример текст начало"
            self.recognized_text = sample
            self.update_command_from_text(sample)
            self.ai_response = f"Ответ AI: {sample}"


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
        command_box = Label(text=root.command_text, size_hint=(1, 0.08), color=(0,0,0,1))
        root.bind(command_text=lambda inst, val: setattr(command_box, 'text', val))

        # SAME SIZE as headers now
        hint = Label(
            text="начало, конец, добавить, выход",
            size_hint=(1, 0.08),
            font_size=18
        )

        recognized_label = Label(text="Распознанный текст:", size_hint=(1, 0.08))
        recognized_output = TextInput(
            text=root.recognized_text,
            size_hint=(1, 0.2),
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            readonly=True
        )
        root.bind(recognized_text=lambda inst, val: setattr(recognized_output, 'text', val))

        ai_label = Label(text="Полученный ответ от AI:", size_hint=(1, 0.08))
        ai_output = TextInput(
            text=root.ai_response,
            size_hint=(1, 0.2),
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            readonly=True
        )
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

        Clock.schedule_interval(root.simulate_recognition, 3)

        return root


if __name__ == "__main__":
    MicApp().run()
