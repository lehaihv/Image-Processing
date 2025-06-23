import os
import streamlit as st
from utils import load_images, embed_images, embed_text, build_faiss_index, search_index
from PIL import Image

st.set_page_config(page_title="Image-Text Similarity Search", layout="wide")

st.title("🔍 Image-Text Similarity Search with CLIP")

# Load and embed images
image_folder = "data/"
st.sidebar.header("Settings")
top_k = st.sidebar.slider("Top K results", 1, 10, 5)

st.sidebar.markdown("---")
st.sidebar.info("Drop .jpg/.png images into the `data/` folder to update the gallery.")

@st.cache_data
def prepare_index():
    image_paths = load_images(image_folder)
    image_embeddings = embed_images(image_paths)
    index = build_faiss_index(image_embeddings)
    return image_paths, image_embeddings, index

image_paths, embeddings, faiss_index = prepare_index()

# Query interface
query = st.text_input("🔎 Describe an image (e.g., 'a dog on a beach'):")

if query:
    query_embedding = embed_text(query)
    results_idx = search_index(faiss_index, query_embedding, k=top_k)

    st.subheader("🖼️ Top Results:")
    cols = st.columns(min(5, top_k))
    for i, idx in enumerate(results_idx):
        with cols[i % len(cols)]:
            st.image(Image.open(image_paths[idx]), caption=os.path.basename(image_paths[idx]), use_column_width=True)
