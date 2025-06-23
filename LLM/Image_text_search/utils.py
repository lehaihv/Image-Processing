import os
import torch
import clip
import faiss
import numpy as np
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def load_images(image_folder):
    image_paths = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(image_folder, filename))
    return image_paths

def embed_images(image_paths):
    image_embeddings = []
    for path in image_paths:
        image = preprocess(Image.open(path)).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model.encode_image(image).cpu().numpy()[0]
        image_embeddings.append(features)
    return np.array(image_embeddings).astype('float32')

def embed_text(text):
    tokens = clip.tokenize([text]).to(device)
    with torch.no_grad():
        features = model.encode_text(tokens).cpu().numpy()[0]
    return features.astype('float32')

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_index(index, query_vec, k=5):
    distances, indices = index.search(query_vec.reshape(1, -1), k)
    return indices[0]
