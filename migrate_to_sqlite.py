import psycopg2
import sqlite3
import json

def migrate_to_sqlite():
    print("Connecting to PostgreSQL...")
    conn_pg = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
    cursor_pg = conn_pg.cursor()

    # Get all messages ONLY from the specified groups
    cursor_pg.execute('''
        SELECT "id", "instanceId", "pushName", "participant", "messageType", "messageTimestamp", "message", "key", "contextInfo", "status" 
        FROM "Message" 
        WHERE "key"->>'remoteJid' IN ('120363409447790752@g.us', '120363042493725288@g.us')
    ''')
    rows = cursor_pg.fetchall()
    
    print(f"Fetched {len(rows)} messages from PostgreSQL. Saving to SQLite...")

    # Connect to SQLite
    conn_sqlite = sqlite3.connect("whatsapp_messages.db")
    cursor_sqlite = conn_sqlite.cursor()

    # Create tables
    cursor_sqlite.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            instance_id TEXT,
            push_name TEXT,
            participant TEXT,
            remote_jid TEXT,
            from_me BOOLEAN,
            message_type TEXT,
            message_timestamp INTEGER,
            text_content TEXT,
            reply_to_id TEXT,
            reply_to_participant TEXT,
            status TEXT,
            raw_message TEXT,
            raw_key TEXT,
            raw_context_info TEXT
        )
    ''')

    insert_data = []
    for row in rows:
        msg_id, instance_id, push_name, participant, message_type, message_timestamp, message_json, key_json, context_json, status = row
        
        if not key_json: continue
        
        remote_jid = key_json.get('remoteJid', '')
        from_me = key_json.get('fromMe', False)
        
        text_content = ""
        if message_json:
            if 'conversation' in message_json:
                text_content = message_json['conversation']
            elif 'extendedTextMessage' in message_json:
                text_content = message_json['extendedTextMessage'].get('text', '')
            elif 'imageMessage' in message_json:
                text_content = message_json['imageMessage'].get('caption', '')
            elif 'videoMessage' in message_json:
                text_content = message_json['videoMessage'].get('caption', '')
            
        reply_to_id = None
        reply_to_participant = None
        if context_json:
            reply_to_id = context_json.get('stanzaId')
            reply_to_participant = context_json.get('participant')
            
        insert_data.append((
            msg_id, instance_id, push_name, participant, remote_jid, from_me,
            message_type, message_timestamp, text_content, reply_to_id, reply_to_participant, status,
            json.dumps(message_json) if message_json else None, 
            json.dumps(key_json), 
            json.dumps(context_json) if context_json else None
        ))

    # Insert into SQLite
    cursor_sqlite.executemany('''
        INSERT OR REPLACE INTO messages (
            id, instance_id, push_name, participant, remote_jid, from_me,
            message_type, message_timestamp, text_content, reply_to_id, reply_to_participant, status,
            raw_message, raw_key, raw_context_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', insert_data)

    conn_sqlite.commit()
    conn_sqlite.close()
    conn_pg.close()

    print("Migration complete! Database saved as whatsapp_messages.db")

if __name__ == "__main__":
    migrate_to_sqlite()
