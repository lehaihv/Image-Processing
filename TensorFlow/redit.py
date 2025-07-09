import matplotlib.pyplot as plt
import os
import re
import shutil
import string
import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras import losses

url = "https://storage.googleapis.com/download.tensorflow.org/data/stack_overflow_16k.tar.gz"

dataset = tf.keras.utils.get_file("tagofprog", url,
                                    untar=True, cache_dir='.',
                                    cache_subdir='')

dataset_dir = dataset # os.path.join(os.path.dirname(dataset), 'stack_overflow_16k')

print("Dataset directory:",os.listdir(dataset))

