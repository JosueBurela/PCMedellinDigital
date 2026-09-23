import sqlite3
import json
import base64
import requests
import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Advertencia: faster-whisper no está instalado aún.")

def decrypt_media(url, media_key_b64):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        encrypted_data = response.content
        media_key = base64.b64decode(media_key_b64)
        hkdf = HKDF(algorithm=hashes.SHA256(), length=112, salt=None, info=b"WhatsApp Audio Keys", backend=default_backend())
        expanded_key = hkdf.derive(media_key)
        iv = expanded_key[0:16]
        cipher_key = expanded_key[16:48]
        encrypted_data_without_mac = encrypted_data[:-10]
        cipher = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data_without_mac) + decryptor.finalize()
    except Exception as e:
        print(f"Error descifrando audio: {e}")
        return None

def process_audios():
    os.makedirs("audios", exist_ok=True)

    # Fetch all missing ones first, then close DB to avoid locks
    conn = sqlite3.connect('whatsapp_messages.db', timeout=20)
    cur = conn.cursor()
    try:
        cur.execute('ALTER TABLE messages ADD COLUMN audio_transcribed BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    cur.execute('SELECT id, raw_message FROM messages WHERE message_type = "audioMessage" AND (audio_transcribed = 0 OR audio_transcribed IS NULL)')
    rows = cur.fetchall()
    conn.close()
    
    print(f"Se encontraron {len(rows)} audios para procesar.")

    model = None
    if WHISPER_AVAILABLE:
        print("Cargando modelo Whisper usando CPU optimizada...")
        model = WhisperModel("base", device="cpu", compute_type="int8")

    # Reabrir DB para updates
    conn = sqlite3.connect('whatsapp_messages.db', timeout=20)
    cur = conn.cursor()

    for msg_id, raw_msg in rows:
        audio_path = f"audios/{msg_id}.ogg"
        
        if not os.path.exists(audio_path):
            try:
                msg_data = json.loads(raw_msg)
                audio_info = msg_data.get('audioMessage', {})
                url = audio_info.get('url')
                media_key = audio_info.get('mediaKey')
                
                if url and media_key:
                    decrypted = decrypt_media(url, media_key)
                    if decrypted:
                        with open(audio_path, "wb") as f:
                            f.write(decrypted)
                    else:
                        cur.execute('UPDATE messages SET audio_transcribed = 1 WHERE id = ?', (msg_id,))
                        conn.commit()
                        continue
                else:
                    cur.execute('UPDATE messages SET audio_transcribed = 1 WHERE id = ?', (msg_id,))
                    conn.commit()
                    continue
            except Exception as e:
                print(f"Error parseando json {msg_id}: {e}")
                cur.execute('UPDATE messages SET audio_transcribed = 1 WHERE id = ?', (msg_id,))
                conn.commit()
                continue

        # Transcribir
        if model and os.path.exists(audio_path):
            print(f"Transcribiendo {msg_id}...", end=" ")
            try:
                segments, info = model.transcribe(audio_path, beam_size=5, language="es")
                transcription = " ".join([segment.text for segment in segments]).strip()
                
                if transcription:
                    print(f"-> {transcription[:50]}...")
                    final_text = f"[AUDIO] {transcription}"
                    cur.execute('UPDATE messages SET text_content = ?, audio_transcribed = 1 WHERE id = ?', (final_text, msg_id))
                    conn.commit()
                else:
                    print("-> (Silencio/Vacio)")
                    cur.execute('UPDATE messages SET audio_transcribed = 1 WHERE id = ?', (msg_id,))
                    conn.commit()
            except Exception as e:
                print(f"Error {e}")
                cur.execute('UPDATE messages SET audio_transcribed = 1 WHERE id = ?', (msg_id,))
                conn.commit()

    conn.close()
    print("Procesamiento de audios finalizado.")

if __name__ == "__main__":
    process_audios()
