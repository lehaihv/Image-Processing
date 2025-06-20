import os
import zipfile
import urllib.request
from tqdm import tqdm
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

# 1. Download and extract dataset
DATA_URL = "https://download.microsoft.com/download/3/E/1/3E1CCCAB-ECBA-4AFA-AF45-9B6B7F6D9C0F/kagglecatsanddogs_3367a.zip"
ZIP_PATH = "cats_vs_dogs.zip"
EXTRACTED_PATH = "PetImages"
DATA_DIR = "cats_vs_dogs_data"

print("Downloading dataset...")
def download_with_progress(url, filename):
    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as t:
        urllib.request.urlretrieve(url, filename, reporthook=t.update_to)

if not os.path.exists(DATA_DIR):
    if not os.path.exists(ZIP_PATH):
        print("Downloading dataset...")
        download_with_progress(DATA_URL, ZIP_PATH)
    print("Extracting dataset...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(".")
    # Organize into cats_vs_dogs_data/cats and cats_vs_dogs_data/dogs
    os.makedirs(f"{DATA_DIR}/cats", exist_ok=True)
    os.makedirs(f"{DATA_DIR}/dogs", exist_ok=True)
    for label in ["Cat", "Dog"]:
        src_folder = os.path.join(EXTRACTED_PATH, label)
        dst_folder = os.path.join(DATA_DIR, label.lower() + "s")
        for fname in os.listdir(src_folder):
            src = os.path.join(src_folder, fname)
            dst = os.path.join(dst_folder, fname)
            try:
                # Some images are corrupted, skip them
                with open(src, "rb") as f:
                    is_jpg = f.read(10).startswith(b'\xff\xd8')
                if is_jpg:
                    shutil.copy(src, dst)
            except Exception:
                continue
    print("Dataset prepared.")

# 2. Data transforms and loaders
IMG_SIZE = 128
BATCH_SIZE = 32

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

dataset = datasets.ImageFolder(
    root=DATA_DIR,
    transform=transform
)

# 3. Split dataset
total_size = len(dataset)
train_size = int(0.7 * total_size)
val_size = int(0.15 * total_size)
test_size = total_size - train_size - val_size
train_ds, val_ds, test_ds = random_split(dataset, [train_size, val_size, test_size])

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

# 4. Define CNN model
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * (IMG_SIZE // 8) * (IMG_SIZE // 8), 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleCNN().to(device)

# 5. Loss and optimizer
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# 6. Training loop
EPOCHS = 10
for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.float().unsqueeze(1).to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
    epoch_loss = running_loss / len(train_loader.dataset)
    print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {epoch_loss:.4f}")

    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.float().unsqueeze(1).to(device)
            outputs = model(images)
            preds = (outputs > 0.5).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    val_acc = correct / total
    print(f"Validation Accuracy: {val_acc:.4f}")

# 7. Test accuracy
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.float().unsqueeze(1).to(device)
        outputs = model(images)
        preds = (outputs > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
test_acc = correct / total
print(f"Test Accuracy: {test_acc:.4f}")

# 8. Save the model
torch.save(model.state_dict(), 'cat_dog_model.pt')