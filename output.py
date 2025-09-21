from argparse import ArgumentParser

import pyttsx3
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='output.log')

female_voice_path = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
male_voice_path = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"

class PyTTSXOutput():
    def __init__(self, voice):
        self.engine = pyttsx3.init()
        if "f" in voice:
            self.engine.setProperty("voice", female_voice_path)
        else:
            self.engine.setProperty("voice", male_voice_path)

    def output(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

def main(args):
    pyttsx3_output = PyTTSXOutput(args.voice.lower())
    while True:
        runtime_input = input()
        print(runtime_input)
        logging.info(f"PyTTS Text: {runtime_input}")
        pyttsx3_output.output(runtime_input)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-v", "--voice", default="male")
    args = parser.parse_args()
    logging.info(f"Starting output with: {args}")
    main(args)