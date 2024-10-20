import itertools
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import mannwhitneyu, ttest_ind
import cliffs_delta
from scipy.stats import rankdata

class MannWhitneyUCliffDelta():
    def __init__(self, samples : Dict[str, List[float]]) -> None:
        self.samples = samples
        
        pairs = list(itertools.combinations(samples.items(), 2))
        
        self.effect_sizes_cliff : Dict[Tuple[str, str], Tuple[float, str]] = {}
        self.effect_sizes_A12 : Dict[Tuple[str, str], float] = {}
        self.effect_sizes_cohens_d : Dict[Tuple[str, str], float] = {}
        self.p_values_mann_w : Dict[Tuple[str, str], float] = {}
        self.p_values_ttest : Dict[Tuple[str, str], float] = {}
        
        for algo1, algo2 in pairs:     
            stat, p_value = mannwhitneyu(algo1[1], algo2[1])
            self.p_values_mann_w[(algo1[0], algo2[0])] = p_value
            
            stat, p_value = ttest_ind(algo1[1], algo2[1])
            self.p_values_ttest[(algo1[0], algo2[0])] = p_value
            
            delta, interpretation = cliffs_delta.cliffs_delta(algo1[1], algo2[1])
            self.effect_sizes_cliff[(algo1[0], algo2[0])] = (delta, interpretation)
            
            self.effect_sizes_A12[(algo1[0], algo2[0])] = self.A12(algo1[1], algo2[1])
            self.effect_sizes_cohens_d[(algo1[0], algo2[0])] = self.cohens_d(algo1[1], algo2[1])
            
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