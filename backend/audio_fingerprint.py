import librosa
import numpy as np

from transformers import Wav2Vec2Processor, Wav2Vec2Model
import torch

import chromadb



TARGET_DURATION = 60  
def preprocess_audio(file_path, target_sr=16000, target_duration=TARGET_DURATION):
   y, sr = librosa.load(file_path, sr=target_sr)


   y = librosa.util.normalize(y)


   target_length = target_sr * target_duration


   if len(y) < target_length:
       padding = target_length - len(y)
       y = np.pad(y, (0, padding), mode='constant')
  
   else:
       y = y[:target_length]
  
   return y, sr




processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")


def get_audio_embedding(file_path):
   audio, sr = preprocess_audio(file_path)
   inputs = processor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
   with torch.no_grad():
       embeddings = model(**inputs).last_hidden_state.mean(dim=1)
   return embeddings.squeeze().numpy()


client = chromadb.Client()


collection = client.get_or_create_collection(name="audio_embeddings")


def add_to_database(embedding, audio_id):
   collection.add(
       embeddings=[embedding],
       metadatas=[{"audio_id": audio_id, "location": audio_id}],
       ids=[audio_id]
   )



def search_audio(query_file, top_k=5):
   query_embedding = get_audio_embedding(query_file)
  
   results = collection.query(
       query_embeddings=[query_embedding],
       n_results=top_k
   )
  
   return results["ids"][0], results["distances"][0]
def print_search_results(query_file):
   documents, distances = search_audio(query_file)
  
   for i, (doc, dist) in enumerate(zip(documents, distances)):
       print(f"Rank {i + 1}: Audio ID = {doc}, distance = {dist}")


embedding1 = get_audio_embedding(
    "D:/audio_copyright_management/sample audio/haunted-danger-60-seconds-356975 (1).mp3"
)
add_to_database(
    embedding1,
    "D:/audio_copyright_management/sample audio/haunted-danger-60-seconds-356975 (1).mp3"
)

embedding2 = get_audio_embedding(
    "D:/audio_copyright_management/sample audio/fairy-lullaby-60-seconds-439269.mp3"
)
add_to_database(
    embedding2,
    "D:/audio_copyright_management/sample audio/fairy-lullaby-60-seconds-439269.mp3"
)
print_search_results(
    "D:/audio_copyright_management/sample audio/fairy-lullaby-60-seconds-439269.mp3"
)