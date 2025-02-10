from typing import List
import numpy as np
from scipy.stats import mannwhitneyu, ttest_ind
import cliffs_delta
from scipy.stats import rankdata

class MannWhitneyUCliffDelta():
    def __init__(self, samples1 : List[float], samples2 : List[float]) -> None:
        samples1 = np.array(samples1, dtype=float)
        samples2 = np.array(samples2, dtype=float)
        stat, p_value = mannwhitneyu(samples1, samples2)
        self.p_value_mann_w = p_value
        
        stat, p_value = ttest_ind(samples1, samples2)
        self.p_value_ttest = p_value
        
        delta, interpretation = cliffs_delta.cliffs_delta(samples1, samples2)
        self.effect_size_cliff = (delta, interpretation)
        
        self.effect_size_A12 = self.A12(samples1, samples2)
        self.effect_size_cohens_d = self.cohens_d(samples1, samples2)
            
    def A12(self, x, y):
        """
        Compute Vargha and Delaney's A12 effect size.
        
        Parameters:
        x: list or numpy array of first sample
        y: list or numpy array of second sample
        
        Returns:
        A12: Vargha and Delaney's A12 effect size
        """
        combined = np.concatenate([x, y])
        ranks = rankdata(combined)
        
        nx = len(x)
        ny = len(y)
        
        rank_x = np.sum(ranks[:nx]) - (nx * (nx + 1)) / 2
        A12 = (rank_x - nx * ny / 2) / (nx * ny)
        
        return A12
    
    def cohens_d(self, x1, x2):
        # Calculate the size of each group
        n1, n2 = len(x1), len(x2)
        
        # Calculate the means of each group
        mean1, mean2 = np.mean(x1), np.mean(x2)
        
        # Calculate the standard deviations of each group
        std1, std2 = np.std(x1, ddof=1), np.std(x2, ddof=1)
        
        # Calculate the pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        # Calculate Cohen's d
        d = (mean1 - mean2) / pooled_std
        return d