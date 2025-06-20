import numpy as np

# Step 1: Define Queries, Keys, and Values (usually vectors)
# For simplicity, small random vectors for 3 tokens:
Q = np.array([[1, 0], [0, 1], [1, 1]])  # Query vectors (3 tokens, dim=2)
K = np.array([[1, 0], [1, 1], [0, 1]])  # Key vectors (3 tokens, dim=2)
V = np.array([[10, 0], [0, 20], [30, 40]])  # Value vectors (3 tokens, dim=2)

# Step 2: Calculate attention scores (Q dot K^T)
scores = np.dot(Q, K.T)
print("Attention Scores:\n", scores)

# Step 3: Apply softmax to scores to get attention weights
def softmax(x):
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)

weights = softmax(scores)
print("\nAttention Weights (after softmax):\n", weights)

# Step 4: Multiply weights by V to get output
output = np.dot(weights, V)
print("\nAttention Output:\n", output)
