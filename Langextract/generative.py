import torch
from diffusers import StableDiffusionPipeline
from genaibook.core import get_device

device = get_device()
print(f"Using device: {device}")

pipe = StableDiffusionPipeline.from_pretrained(
    "Lykon/dreamshaper-8",
    # torch_dtype=torch.float16,  # Removed for CPU compatibility
    # variant="fp16",  # Removed for CPU compatibility
).to(device)

# Add this to your script to generate an image
prompt = "a cat chasing after a mouse"
image = pipe(prompt).images[0]
image.save("generated_image.png")