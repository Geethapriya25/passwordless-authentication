import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from io import BytesIO


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def match_spoken_phrase(voice_bytes, stored_phrase_embedding):
    new_embedding = get_voice_embedding(voice_bytes)
    
    if isinstance(stored_phrase_embedding, str):
        stored_embedding = np.array(eval(stored_phrase_embedding))  
    else:
        stored_embedding = np.array(stored_phrase_embedding)

    similarity = cosine_similarity([new_embedding], [stored_embedding])[0][0]
    return similarity > 0.85  

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

def get_voice_embedding(audio_bytes):
    waveform, sample_rate = torchaudio.load(BytesIO(audio_bytes))
    waveform = waveform.squeeze(0)

    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

    inputs = processor(waveform, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().numpy()
    return embedding.tolist()

