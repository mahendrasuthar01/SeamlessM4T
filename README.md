# Speech Transcriber with Language Selection using SeamlessM4T

This Python script allows you to record audio and transcribe it into text using the Facebook Seamless M4T v2 model. You can choose the target language for transcription from English, German, or French.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3.8 or higher

Install portaudio through the following command(For mac):

```
brew install portaudio
```

You can install the required dependencies using pip and the provided `requirements.txt` file:

```
pip install -r requirements.txt
```


The `requirements.txt` file contains the necessary Python packages and versions required by the script.

## Usage

1. Run the script `app.py` using Python:

```
python app.py
```

2. Follow the on-screen instructions to select the target language (eng, deu, or fra).

3. Start speaking into the microphone. The script will transcribe your speech into text in real-time.

4. Press Ctrl+C to stop recording and exit the script.