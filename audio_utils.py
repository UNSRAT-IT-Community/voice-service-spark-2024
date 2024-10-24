import os
import edge_tts
import asyncio
from pydub import AudioSegment

# Fungsi untuk menyimpan TTS dari Edge-TTS sebagai WAV
async def get_voice_from_edge_tts(text, output_path, voice="id-ID-ArdiNeural"):
    communicate = edge_tts.Communicate(text, voice)
    
    # Buat file sementara untuk menyimpan hasil TTS
    temp_audio_path = output_path.replace('.wav', '.mp3')  # Simpan sementara sebagai MP3 dulu
    
    await communicate.save(temp_audio_path)
    print(f"Suara berhasil disimpan sementara sebagai MP3 di {temp_audio_path}")

    # Konversi MP3 ke WAV
    try:
        sound = AudioSegment.from_file(temp_audio_path, format="mp3")
        sound.export(output_path, format="wav")
        print(f"Suara berhasil dikonversi dan disimpan sebagai WAV di {output_path}")
    except Exception as e:
        print(f"Error saat mengonversi MP3 ke WAV: {e}")

    # Hapus file MP3 sementara
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
        print(f"File sementara MP3 telah dihapus: {temp_audio_path}")

# Contoh penggunaan
text_to_convert = "Halo, ini adalah contoh konversi teks ke suara menggunakan edge-tts."
wav_file_path = './input-source/input_audio.wav'

# Jalankan fungsi secara async
asyncio.run(get_voice_from_edge_tts(text_to_convert, wav_file_path))
