# pip install torch

import torch

if torch.cuda.is_available():

   print("CUDA is available! PyTorch can use the GPU.")
   print(f"Device count: {torch.cuda.device_count()}")
   print(f"Device name: {torch.cuda.get_device_name(0)}")
else:

   print("CUDA is not available. PyTorch cannot use the GPU.")