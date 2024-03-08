import asyncio
import pyaudio
import wave
import os
from transformers import AutoProcessor, SeamlessM4TForSpeechToText
import torchaudio
import concurrent.futures

class SpeechTranscriber:
    def __init__(self):
        # Initialize the transcriber with pretrained processor and model
        self.processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
        self.model = SeamlessM4TForSpeechToText.from_pretrained("facebook/hf-seamless-m4t-medium")

        # Audio parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK_DURATION_MS = 2048 
        self.CHUNK_SIZE = int(self.RATE * self.CHUNK_DURATION_MS / 1000)
        self.WAVE_OUTPUT_FILENAME = "temp_chunk.wav"
        self.audio = pyaudio.PyAudio()  # PyAudio instance for audio operations
        self.loop = asyncio.get_event_loop()

    async def record_and_transcribe(self, tgt_lang="eng"):
        # Open audio stream for recording
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK_SIZE,
                                      stream_callback=self.process_audio_chunk_callback(tgt_lang))  # Pass tgt_lang here
        print("Recording... Press Ctrl+C to stop.")

        try:
            while True:  # Continue recording indefinitely until interrupted
                await asyncio.sleep(0.1)   
        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
        finally:
            self.cleanup()

    def process_audio_chunk_callback(self, tgt_lang):  # Include tgt_lang parameter
        # Callback function to process audio chunks
        def callback(in_data, frame_count, time_info, status):
            frames = [in_data]

            # Write audio data to a temporary WAV file
            wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            # Load audio data from the WAV file and resample if necessary
            audio_chunk, orig_freq = torchaudio.load(self.WAVE_OUTPUT_FILENAME)
            audio_chunk = torchaudio.functional.resample(audio_chunk, orig_freq=orig_freq, new_freq=16000)

            # Check if audio power is above a threshold for meaningful speech
            if audio_chunk.pow(2).mean().item() > 0.0001:  
                # Tokenize and transcribe audio using the model
                inputs = self.processor(audios=audio_chunk, sampling_rate=16000, return_tensors="pt")
                
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    output_tokens = self.model.generate(**inputs, tgt_lang=tgt_lang)

                # Decode transcribed text
                translated_text = self.processor.decode(output_tokens[0].tolist(), skip_special_tokens=True)
                print(f"Translated Text ({tgt_lang}): {translated_text}")
            else:
                pass  # Audio is below threshold, skip transcription

            return (in_data, pyaudio.paContinue)  # Continue audio stream
        return callback  # Return the callback function

    def cleanup(self):
        # Clean up audio resources and temporary files
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        os.remove(self.WAVE_OUTPUT_FILENAME)
        print("Cleanup done.")

async def main():
    # Main function to initialize and start transcriber
    transcriber = SpeechTranscriber()
    try:
        lang = input("Enter target language (eng, deu, fra): ").strip().lower()
        await transcriber.record_and_transcribe(tgt_lang=lang)
    except KeyboardInterrupt:
        print("\nFinished.")
if __name__ == "__main__":
    asyncio.run(main())  # Run the main coroutine