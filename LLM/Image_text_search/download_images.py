# download_images.py
import requests
from pathlib import Path

image_urls = [
    "https://images.unsplash.com/photo-1518717758536-85ae29035b6d",  # dog
    "https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d",  # beach
    "https://images.unsplash.com/photo-1584395630827-860eee694d7b",  # mountain
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",  # forest
    "https://images.unsplash.com/photo-1579546929518-9e396f3cc809",  # people
    "https://images.unsplash.com/photo-1493244040629-496f6d136cc3",  # birds
    "https://images.unsplash.com/photo-1531177076127-b6f1f0060902",  # cat
    "https://images.unsplash.com/photo-1547721064-da6cfb341d50",     # cityscape
    "https://images.unsplash.com/photo-1602526218452-0aee0f5c9f3d",  # desert
    "https://images.unsplash.com/photo-1516979187457-637abb4f9353",  # food
]

Path("data").mkdir(exist_ok=True)

for i, url in enumerate(image_urls):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    with open(f"data/sample_{i+1}.jpg", "wb") as f:
        f.write(response.content)

print("Images downloaded to ./data/")

