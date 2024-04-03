import numpy as np
import random


class HighLevel:

    num_silos = 10

    def get_random_int_array(self, num_rows, num_cols, max_val):
        rows = []
        for row in range(0, num_rows):
            row = []
            for col in range(0, num_cols):
                row.append(random.randint(0, max_val))
            rows.append(row)

        return np.array(rows)

    def get_siloed_array(self, array):
        return array // (HighLevel.num_silos + 1)

    def variety(self, array):
        total = 0
        for i in range(0, array.shape[1]):
            col = array[:, i].flatten()
            total += len(np.unique(col))
        return total/array.shape[1]

    def balance(self, array):
        total = 0
        for i in range(0, array.shape[1]):
            col = array[:, i].flatten()
            counts = np.bincount(col, None, HighLevel.num_silos)
            u_counts = np.unique(counts)
            total += 1/(1 + np.std(u_counts))
        return total/array.shape[1]

    def normalise(self, list):
        return (list - np.min(list))/(np.max(list) - np.min(list))

hl = HighLevel()
varieties = []
balances = []
arrays = []
for i in range(0, 10000):
    array = hl.get_random_int_array(10, 10, 100)
    arrays.append(array)
    siloed_array = hl.get_siloed_array(array)
    varieties.append(hl.variety(siloed_array))
    balances.append(hl.balance(siloed_array))


total_scores = hl.normalise(varieties) + hl.normalise(balances)
best_ind = np.argmax(total_scores)
worst_ind = np.argmin(total_scores)

print(hl.get_siloed_array(arrays[best_ind]))
print(varieties[best_ind])
print(balances[best_ind])
print("---")

print(hl.get_siloed_array(arrays[worst_ind]))
print(varieties[worst_ind])
print(balances[worst_ind])
print("---")

