from typing import List
import numpy as np
from scipy.stats import chi2_contingency, entropy

class ChiSquareCramersV():
    def __init__(self, freq1 : List[int], list1 : List[int], freq2 : List[int], list2 : List[int]) -> None:
        freq1 = np.array(freq1) / len(list1)
        freq2 = np.array(freq2) / len(list2)
        
        # Expected frequencies: average of A and B
        expected = (freq1 + freq2) / 2

        # Compute Chi-square statistic
        self.chi2_stat = np.sum((freq1 - expected) ** 2 / expected)
        self.p_value = chi2_contingency([freq1 * len(list1), freq2 * len(list2)]).pvalue

        # Avoid zero probabilities by adding a small value
        freq1 += 1e-10
        freq2 += 1e-10

        # Normalize
        freq1 /= freq1.sum()
        freq2 /= freq2.sum()

        # Compute KL divergence
        self.kl_div = entropy(freq1, freq2)  # KL(A || B)