# elderly-companion
An elderly companion that can be spoken to, share facts, play music, etc.

## How To Use
1. Download and run __main__.exe to start and run the pipeline
2. Start by saying "hello", "hi", or "hey" into the microphone. 
If your voice is detected, you should hear a greeting from the LLM in response. 
3. Ask a question or begin your conversation!

## Code Files Breakdown
### input.py
- Uses the Vosk API and a Kaldi Recognizer to detect speech. 
- Once a wake word is detected, another recognizer will begin to detect for subsequent sentences.

### llm.js
- Uses Hack Club AI's Open AI model to prompt and receive a response.

### output.py
- Uses the PyTTSx API to output the LLM's response.