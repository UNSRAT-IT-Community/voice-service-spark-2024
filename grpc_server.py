import grpc
from concurrent import futures
import speech_pb2, speech_pb2_grpc
import speech_recognition as sr
import keyboard
import tempfile
import os
import time
import edge_tts
import asyncio

# Konfigurasi suara untuk TTS
VOICES = ['id-ID-ArdiNeural', 'id-ID-GadisNeural']
VOICE = VOICES[0]

# gRPC service untuk STT dan TTS
class SpeechService(speech_pb2_grpc.SpeechServiceServicer):
    # STT (Speech to Text)
    def Listen(self, request, context):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Tekan dan tahan 'Space' untuk mulai berbicara...")
            keyboard.wait('space')
            print("Merekam...")

            audio = recognizer.listen(source)
            print("Selesai merekam.")

            # Simpan input audio ke folder source-input
            audio_data = audio.get_wav_data()
            input_wav_path = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/source-input/input_audio.wav'
            with open(input_wav_path, 'wb') as f:
                f.write(audio_data)

            try:
                text = recognizer.recognize_google(audio, language="id-ID")
                print(f"Anda mengatakan: {text}")
                return speech_pb2.STTResponse(text=text)
            except sr.UnknownValueError:
                return speech_pb2.STTResponse(text="Audio tidak bisa dikenali")
            except sr.RequestError:
                return speech_pb2.STTResponse(text="Terjadi kesalahan pada request")

    # TTS (Text to Speech)
    async def synthesize_speech(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        temp_wav_path = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/output/output_audio.wav'
        await communicate.save(temp_wav_path)
        return temp_wav_path

    def ConvertToWav(self, request, context):
        text = request.text

        # Konversi teks ke audio (TTS)
        temp_wav_path = asyncio.run(self.synthesize_speech(text, VOICE))

        # Print file type (extension)
        file_extension = os.path.splitext(temp_wav_path)[1]
        print(f"Tipe file audio: {file_extension}")

        # Kembalikan file WAV sebagai bytes
        with open(temp_wav_path, 'rb') as f:
            wav_data = f.read()

        return speech_pb2.TTSResponse(audio_data=wav_data)

# Menjalankan server gRPC
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    speech_pb2_grpc.add_SpeechServiceServicer_to_server(SpeechService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Server berjalan pada port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
