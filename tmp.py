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
    0, 1, 2, 1, 2, 0, 1, 2, 1, 0, 1, 0, 2, 0
]

#testing
removeNWeeks = 2
targetVal = None

#remove last n items for testing
for i in range(removeNWeeks):
    targetVal = sequence.pop()

print("Last val: ",sequence[-1])
# Order of the Markov Chain
order = 1
if len(sequence) < order:
    raise ValueError("The sequence length must be greater than the order of the Markov Chain.")

# Build the Markov Chain
transition_matrix = defaultdict(lambda: defaultdict(int))
for i in range(len(sequence) - order):
    curr_states = tuple(sequence[i:i+order])
    next_state = sequence[i+order]
    transition_matrix[curr_states][next_state] += 1

k = 0.1  # Smaller than 1 to reduce the uniformity effect of smoothing



# Convert counts to probabilities with smoothing
V = len(set(sequence))
for curr_states, transitions in transition_matrix.items():
    total = sum(transitions.values())
    for possible_next_state in set(sequence):
        count = transitions[possible_next_state]
        transition_matrix[curr_states][possible_next_state] = (count + 1) / (total + V * k)

# Predict the next item based on the current state and its transition probabilities
curr_states = tuple(sequence[-order:])
predicted_probs = transition_matrix[curr_states]
next_item = max(predicted_probs, key=predicted_probs.get)

print("Predicted next item:", next_item)
print("Target:", targetVal)

print(next_item == targetVal)

print("\nTransition Probabilities from state", curr_states, ":")
for state, prob in sorted(predicted_probs.items(), key=lambda x: x[1], reverse=True):
    print(f"Probability of transitioning to {state}: {prob:.4f}")