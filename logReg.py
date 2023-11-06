from sklearn.linear_model import LogisticRegression
import numpy as np

#seq
sequence = [
    0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0, 2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 
    2, 0, 2, 1, 0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1,
    0, 1, 2, 1, 1, 2, 0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0, 2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2,
    0, 2, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 1, 2, 0, 1, 2,
    1, 0, 1, 0, 2, 1, 0, 1
]

def create_dataset(sequence, n_features):
    X, y = [], []
    for i in range(len(sequence) - n_features):
        X.append(sequence[i:i + n_features])
        y.append(sequence[i + n_features])
    return np.array(X), np.array(y)



removeNWeeks = 4

targetVal = None
#remove last n items for testing
for i in range(removeNWeeks):
    targetVal = sequence.pop()

print("Last item: ", sequence[-1])


# Choose a window size (number of previous items to consider)
window_size = 14

# Create dataset
X, y = create_dataset(sequence, window_size)

# Split the data (last 'window_size' entries are left for prediction)
X_train, y_train = X[:-window_size], y[:-window_size]

# Initialize model and fit to the data
model = LogisticRegression(max_iter=200)  # Increased max_iter to ensure convergence
model.fit(X_train, y_train)

# Use the last 'window_size' entries to predict the next item
X_predict = [sequence[-window_size:]]
predicted_proba = model.predict_proba(X_predict)

# Output the prediction probabilities
probabilities = predicted_proba[0]
print(f"Prediction probabilities:")
print(f"Probability of 0: {probabilities[0]*100}%")
print(f"Probability of 1: {probabilities[1]*100}%")
print(f"Probability of 2: {probabilities[2]*100}%")

# You may also want to show the most likely next item
predicted = model.predict(X_predict)
print("TARGET: ",targetVal)
print(f"The most likely next item in the sequence is: {predicted[0]}")