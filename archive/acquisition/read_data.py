import pickle
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filename = "dataset_06_04_2023.pkl"
    with open('dataset_06_04_2023.pkl', 'rb') as f:
        vectors = pickle.load(f)
        vectors = np.asarray(vectors)
        plt.plot(vectors[1][2])
        plt.show()
