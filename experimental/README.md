# Thai Transcript Beautifier

This project is aim to beautify the transcript that transcribe from google api speech to text service
in order to enhance transcript's readability.

This project is based on modified [wannaphongcom/thai-sent_tokenize project](https://github.com/wannaphongcom/thai-sent_tokenize) and 
slight modification of [pythainlp project](https://github.com/PyThaiNLP/pythainlp)

Note:

This project's dataset is based on good, mediocre to bad or utterly nonsense transcript that aren't correctly transcribed such as transcipt from audio with high disturbance, multiple speaker with no diariazation, and problematic speaker. Due to the nature of the transcript need to be processed, this kind of dataset is required.

# Plan

- Anomaly Detection to remove/highlight nonsensical part of speech due to wrong transcription or speaker mistake.