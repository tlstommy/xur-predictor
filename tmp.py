import numpy as np
from collections import defaultdict

# Given sequence
sequence = [
    0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0,
    2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 2, 1,
    0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1,
    0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2,
    0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0,
    2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 1, 2, 0, 2,
    1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1,
    0, 1, 2, 1, 2, 0, 1, 2, 1, 0, 1, 0, 2
]

#testing
removeNWeeks = 0
targetVal = None

#remove last n items for testing
for i in range(removeNWeeks):
    targetVal = sequence.pop()

# Build the Markov Chain
transition_matrix = defaultdict(lambda: defaultdict(int))
for i in range(len(sequence) - 1):
    curr_state, next_state = sequence[i], sequence[i+1]
    transition_matrix[curr_state][next_state] += 1

# Convert counts to probabilities with smoothing
V = len(set(sequence))  # Number of unique states
for curr_state, transitions in transition_matrix.items():
    total = sum(transitions.values())
    for possible_next_state in set(sequence):
        count = transitions[possible_next_state]
        transition_matrix[curr_state][possible_next_state] = (count + 1) / (total + V)

# Predict the next item based on the current state and its transition probabilities
curr_state = sequence[-1]
predicted_probs = transition_matrix[curr_state]
next_item = max(predicted_probs, key=predicted_probs.get)

print("Predicted next item:", next_item)
print("Target:", targetVal)
print("\nTransition Probabilities from state", curr_state, ":")
for state, prob in sorted(predicted_probs.items(), key=lambda x: x[1], reverse=True):
    print(f"Probability of transitioning to {state}: {prob:.4f}")