import vosk
import pyaudio
import json
import sys


def check_vosk():
    """Проверка установки Vosk и наличия модели"""
    try:
        # Проверяем наличие модели
        model_path = "vosk-model-small-ru-0.22"
        if not os.path.exists(model_path):
            print("❌ Модель Vosk не найдена!")
            print(f"   Скачайте модель с https://alphacephei.com/vosk/models")
            print(f"   и распакуйте в папку: {model_path}")
            return False

        # Загружаем модель
        model = vosk.Model(model_path)
        print("✅ Vosk: модель успешно загружена")
        return True
    except Exception as e:
        print(f"❌ Ошибка Vosk: {e}")
        return False


def check_pyaudio():
    """Проверка PyAudio и микрофона"""
    try:
        p = pyaudio.PyAudio()

        # Выводим информацию об аудиоустройствах
        print(f"\n✅ PyAudio версия: {pyaudio.__version__}")
        print(f"   Устройств ввода: {p.get_device_count()}")

        # Проверяем доступные устройства ввода
        has_input = False
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                has_input = True
                print(f"   Устройство ввода {i}: {device_info['name']}")

        if not has_input:
            print("❌ Нет доступных устройств ввода!")
            p.terminate()
            return False

        # Пробуем открыть поток
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        print("✅ Микрофон: успешно открыт")

        stream.close()
        p.terminate()
        return True

    except Exception as e:
        print(f"❌ Ошибка PyAudio: {e}")
        return False


def quick_test():
    """Быстрый тест записи и распознавания (3 секунды)"""
    print("\n🎤 Тест записи и распознавания (3 секунды)...")
    print("   Скажите что-нибудь...")

    try:
        model = vosk.Model("vosk-model-small-ru-0.22")
        rec = vosk.KaldiRecognizer(model, 16000)

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )

        # Записываем 3 секунды
        import time
        start_time = time.time()

        while time.time() - start_time < 3:
            data = stream.read(4000)
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())

        stream.stop_stream()
        stream.close()
        p.terminate()

        if result.get('text'):
            print(f"✅ Распознано: '{result['text']}'")
        else:
            print("⚠️ Ничего не распознано")

    except Exception as e:
        print(f"❌ Ошибка при тесте: {e}")


if __name__ == "__main__":
    import os

    print("=" * 50)
    print("ПРОВЕРКА VOSK И PYAUDIO")
    print("=" * 50)

    vosk_ok = check_vosk()
    pyaudio_ok = check_pyaudio()

    if vosk_ok and pyaudio_ok:
        print("\n" + "=" * 50)
        print("✅ ВСЕ КОМПОНЕНТЫ РАБОТАЮТ")
        print("=" * 50)

        # Запрашиваем быстрый тест
        response = input("\nЗапустить быстрый тест распознавания? (y/n): ")
        if response.lower() == 'y':
            quick_test()
    else:
        print("\n❌ Есть проблемы с компонентами")
        print("\nРекомендации:")
        print("1. Установите Vosk: pip install vosk")
        print("2. Установите PyAudio: pkg install portaudio && pip install pyaudio")
        print("3. Скачайте модель: wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
        print("   и распакуйте: unzip vosk-model-small-ru-0.22.zip")