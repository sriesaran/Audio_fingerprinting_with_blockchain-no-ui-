from blockchain.contract_config import contract, ACCOUNT,w3
import librosa
import numpy as np
import hashlib
import sqlite3
from scipy.ndimage import maximum_filter
from blockchain.contract_config import contract, ACCOUNT
import time
from blockchain.contract_config import register_audio_blockchain
from blockchain.contract_config import verify_audio_blockchain
# ==========================
# CONFIG
# ==========================
DB_NAME = "audio_fingerprints.db"
SR = 22050
N_FFT = 2048
HOP_LENGTH = 512
PEAK_NEIGHBORHOOD_SIZE = 20
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200
FAN_VALUE = 10
MIN_MATCH_SCORE = 30

# ==========================
# DATABASE SETUP
# ==========================
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS fingerprints (
    hash TEXT,
    audio_id TEXT,
    time_offset INTEGER
)
""")
conn.commit()

# ==========================
# AUDIO → SPECTROGRAM
# ==========================
def audio_to_spectrogram(file_path):
    y, sr = librosa.load(file_path, sr=SR, mono=True)
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
    return librosa.amplitude_to_db(S)

# ==========================
# PEAK DETECTION
# ==========================
def extract_peaks(S_db):
    threshold = np.mean(S_db) + 10
    local_max = maximum_filter(S_db, size=PEAK_NEIGHBORHOOD_SIZE) == S_db
    peaks = np.where(local_max & (S_db > threshold))
    return list(zip(peaks[0], peaks[1]))

# ==========================
# FINGERPRINT GENERATION
# ==========================
def generate_hashes(peaks):
    fingerprints = []

    for i in range(len(peaks)):
        for j in range(1, FAN_VALUE):
            if i + j < len(peaks):
                f1, t1 = peaks[i]
                f2, t2 = peaks[i + j]

                delta_t = t2 - t1
                if MIN_HASH_TIME_DELTA <= delta_t <= MAX_HASH_TIME_DELTA:
                    raw = f"{f1}|{f2}|{delta_t}"
                    h = hashlib.sha1(raw.encode()).hexdigest()
                    fingerprints.append((h, t1))

    return fingerprints

# ==========================
# MASTER FINGERPRINT HASH (BLOCKCHAIN)
# ==========================
def generate_master_hash(hashes):
    combined = "".join([h for h, _ in hashes])
    return hashlib.sha256(combined.encode()).hexdigest()

# ==========================
# REGISTER AUDIO (SQL + BLOCKCHAIN)
# ==========================
def register_audio(file_path, audio_id):

    # 1️⃣ Check fingerprint DB
    cursor.execute(
        "SELECT 1 FROM fingerprints WHERE audio_id=? LIMIT 1",
        (audio_id,)
    )
    exists = cursor.fetchone() is not None

    if not exists:
        S_db = audio_to_spectrogram(file_path)
        peaks = extract_peaks(S_db)
        hashes = generate_hashes(peaks)

        for h, t in hashes:
            cursor.execute(
                "INSERT INTO fingerprints VALUES (?, ?, ?)",
                (h, audio_id, t)
            )
        conn.commit()
        print(f"✅ Fingerprints stored for {audio_id}")
    else:
        print(f"⚠ Fingerprints already exist for {audio_id}")

    # 2️⃣ Always ensure blockchain registration
    bc_data = verify_audio_blockchain(audio_id)

    if bc_data is None:
        print("🔗 Registering on blockchain...")
        register_audio_blockchain(file_path, audio_id)
    else:
        print("⛓ Already registered on blockchain")

# ==========================
# SEARCH / COPYRIGHT CHECK
# ==========================
def recognize_audio(query_file):
    S_db = audio_to_spectrogram(query_file)
    peaks = extract_peaks(S_db)
    hashes = generate_hashes(peaks)

    matches = {}

    for h, t in hashes:
        cursor.execute(
            "SELECT audio_id, time_offset FROM fingerprints WHERE hash=?",
            (h,)
        )
        results = cursor.fetchall()

        for audio_id, db_time in results:
            if isinstance(db_time, bytes):
                db_time = int.from_bytes(db_time, byteorder="little")

            offset = int(db_time) - int(t)
            matches.setdefault(audio_id, {})
            matches[audio_id][offset] = matches[audio_id].get(offset, 0) + 1

    best_match = None
    best_score = 0

    for audio_id in matches:
        score = max(matches[audio_id].values())
        if score > best_score:
            best_score = score
            best_match = audio_id

    return best_match, best_score


# ==========================
# BLOCKCHAIN VERIFICATION
# ==========================
def verify_from_blockchain(audio_id):
    return verify_audio_blockchain(audio_id)


# ==========================
# CONFIDENCE LEVEL
# ==========================
def confidence_level(score):
    if score >= 500:
        return "HIGH – Confirmed Copyright Match"
    elif score >= 50:
        return "MEDIUM – Likely Match"
    elif score >= 10:
        return "LOW – Weak Similarity"
    else:
        return "NO SIGNIFICANT MATCH"

# ==========================
# MAIN DEMO
# ==========================
if __name__ == "__main__":

    # Register audios (run once)
    
    register_audio(
        "D:/audio_copyright_management/sample audio/haunted-danger-60-seconds-356975 (1).mp3",
        "haunted-danger"
    )

    register_audio(
        "D:/audio_copyright_management/sample audio/fairy-lullaby-60-seconds-439269.mp3",
        "fairy-lullaby"
    )
            


    # Query audio
    match, score = recognize_audio(
        "D:/audio_copyright_management/sample audio/haunted-danger-60-seconds-356975 (1).mp3"
    )

    if match and score >= MIN_MATCH_SCORE:
       bc_data = verify_audio_blockchain(match)
       if bc_data is None:
           print("\n⚠ Match found in fingerprints")
           print("❌ But NOT registered on blockchain")
           print("👉 Ownership proof unavailable")
       else:
           print("\n⛓ BLOCKCHAIN PROOF")
           print("👤 Owner:", bc_data["owner"])
           print("⏱ Registered:", time.ctime(bc_data["timestamp"]))

    else:
        print("\n❌ No copyright match found")
        print("🔒 Score:", score)



