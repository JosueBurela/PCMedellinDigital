import sqlite3
import json
import base64
import requests
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

def download_and_decrypt_whatsapp_media(url, media_key_b64, media_type="Audio"):
    try:
        # Download the encrypted file
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to download from WhatsApp servers. Status: {response.status_code}")
            return None
            
        encrypted_data = response.content
        
        # Decode base64 media key
        media_key = base64.b64decode(media_key_b64)
        
        # HKDF extraction
        # WhatsApp uses different appInfo strings based on media type
        app_info = f"WhatsApp {media_type} Keys".encode('utf-8')
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=112,
            salt=None,
            info=app_info,
            backend=default_backend()
        )
        expanded_key = hkdf.derive(media_key)
        
        iv = expanded_key[0:16]
        cipher_key = expanded_key[16:48]
        # mac_key = expanded_key[48:80]
        # ref_key = expanded_key[80:112]
        
        # Remove MAC from the end of encrypted data (last 10 bytes)
        encrypted_data_without_mac = encrypted_data[:-10]
        
        # Decrypt using AES-CBC
        cipher = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data_without_mac) + decryptor.finalize()
        
        return decrypted_data
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def test_first_audio():
    conn = sqlite3.connect('whatsapp_messages.db')
    cur = conn.cursor()
    cur.execute('SELECT id, raw_message FROM messages WHERE message_type = "audioMessage" LIMIT 1')
    res = cur.fetchone()
    if res:
        msg_id, raw = res
        msg_data = json.loads(raw)
        audio_info = msg_data.get('audioMessage', {})
        url = audio_info.get('url')
        media_key = audio_info.get('mediaKey')
        
        if url and media_key:
            print(f"Attempting to download and decrypt {msg_id}...")
            decrypted = download_and_decrypt_whatsapp_media(url, media_key, "Audio")
            if decrypted:
                os.makedirs("audios", exist_ok=True)
                file_path = f"audios/{msg_id}.ogg"
                with open(file_path, "wb") as f:
                    f.write(decrypted)
                print(f"Success! Saved to {file_path}")
            else:
                print("Failed to decrypt.")
        else:
            print("Missing URL or mediaKey in DB.")
    else:
        print("No audio messages found.")

if __name__ == "__main__":
    test_first_audio()
