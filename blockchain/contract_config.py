# blockchain/contract_config.py

from web3 import Web3
import json
import os
import hashlib

# ==========================
# CONFIG
# ==========================
GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0xd04524dF5fd19c066215b966A766Cbe7cC69baa9"  # 👈 Replace with your deployed contract

# ==========================
# CONNECT TO BLOCKCHAIN
# ==========================
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    raise Exception("❌ Could not connect to blockchain")

# ==========================
# LOAD CONTRACT ABI
# ==========================
abi_path = os.path.join(os.path.dirname(__file__), "contract_abi.json")
with open(abi_path, "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

# Use the first Ganache account
ACCOUNT = w3.eth.accounts[0]

print("✅ Blockchain connected successfully")

# ==========================
# FUNCTIONS
# ==========================

def register_audio_blockchain(audio_path, audio_id):
    """
    Registers an audio file on the blockchain using its SHA256 master hash.
    """
    # Read audio bytes
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    # Generate master hash
    master_hash = hashlib.sha256(audio_bytes).hexdigest()

    # Send transaction to blockchain
    tx = contract.functions.registerAudio(
        audio_id,
        master_hash
    ).transact({"from": ACCOUNT})

    receipt = w3.eth.wait_for_transaction_receipt(tx)

    print("✅ Audio registered on blockchain")
    print("🎵 Audio ID:", audio_id)
    print("🔑 Master Hash:", master_hash)
    print("⛓ Tx Hash:", receipt.transactionHash.hex())

    return master_hash


def verify_audio_blockchain(audio_id):
    """
    Verifies an audio on the blockchain by audio_id.
    Returns a dictionary with master_hash, owner, and timestamp.
    """
    master_hash, owner, timestamp = contract.functions.verifyAudio(audio_id).call()

    if master_hash == "":
        print("🆓 Audio not registered on blockchain")
        return None

    print("🔒 Copyright verified")
    print("🎵 Audio ID:", audio_id)
    print("👤 Owner Address:", owner)
    print("⏰ Registered Time:", timestamp)

    return {
        "audio_id": audio_id,
        "master_hash": master_hash,
        "owner": owner,
        "timestamp": timestamp
    }
