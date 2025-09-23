import asyncio
import json
import logging
from argparse import ArgumentParser

import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='input.log')

DEBOUNCE = 100
TARGET_RATE = 48000
IN_RATE = 48000

WAKE_WORDS = ["hey", "hi", "hello"]

class Wake:
    def __init__(self, path):
        self.model = Model(lang="en-us", model_path=path)
        self.rec = KaldiRecognizer(self.model, TARGET_RATE, '["hey", "hi", "hello", "[unk]"]')
        self.wake_event = asyncio.Event()
        self.sleep_event = asyncio.Event()
        self.sleep_event.set()

    async def woke(self):
        await self.wake_event.wait()
        self.sleep_event.clear()

    def asleep(self):
        self.sleep_event.set()
        self.wake_event.clear()

    async def recognize(self, data):
        if await self.sleep_event.wait() and self.rec.AcceptWaveform(data):
            result = self.rec.Result()
            text = json.loads(result)["text"]
            if any(wake_word in text.lower() for wake_word in WAKE_WORDS):
                print(text)
                self.wake_event.set()
            await asyncio.sleep(0)

class Input:
    def __init__(self, path, pyaudio):
        self.pa = pyaudio
        self.model = Model(lang="en-us", model_path=path)
        self.rec = KaldiRecognizer(self.model, TARGET_RATE)
        self.debouncer = 0

    async def recognize(self, data):
        if self.rec.AcceptWaveform(data):
            result = self.rec.Result()
            text = json.loads(result)["text"]
            print(text)
            logging.info(f"Text: {text}")
            self.debouncer = 0
            if "thank you" in text.lower():
                self.debouncer = DEBOUNCE
        else:
            self.debouncer += 1

async def producer(in_stream, wake):
    while True:
        data = in_stream.read(num_frames=4000, exception_on_overflow=False)
        await wake.recognize(data)

async def consumer(in_stream, wake, input):
    global DEBOUNCE
    while True:
        await wake.woke()
        logging.info("Wake word activated")
        while input.debouncer < DEBOUNCE:
            data = in_stream.read(num_frames=4000, exception_on_overflow=False)
            await input.recognize(data)
        input.debouncer = 0
        wake.asleep()
        logging.info("Back asleep")

async def main(args):
    pa = pyaudio.PyAudio()

    path = args.model
    if args.device is not None:
        input_device = args.device
    else:
        input_device = 0

    in_stream = pa.open(rate=IN_RATE, format=pyaudio.paInt16, channels=1, input=True, input_device_index=input_device)
    wake = Wake(path)
    input = Input(path, pa)

    tasks = []
    tasks.append(asyncio.create_task(producer(in_stream, wake)))
    tasks.append(asyncio.create_task(consumer(in_stream, wake, input)))

    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", default="./assets/models/vosk-model-small-en-us-0.15")
    parser.add_argument("-d", "--device", action="store", default=0)
    args = parser.parse_args()
    logging.info(f"Starting input with: {args}")
    asyncio.run(main(args))