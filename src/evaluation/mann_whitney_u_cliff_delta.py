import itertools
from typing import Dict, List, Tuple
from scipy.stats import mannwhitneyu
import cliffs_delta

class MannWhitneyUCliffDelta():
    def __init__(self, samples : Dict[str, List[float]]) -> None:
        self.samples = samples
        
        pairs = list(itertools.combinations(samples.items(), 2))
        
        self.effect_size : Dict[Tuple[str, str], Tuple[float, str]]
        self.p_values : Dict[Tuple[str, str], float]
        
        for algo1, algo2 in pairs:     
            stat, p_value = mannwhitneyu(algo1[1], algo2[1], alternative='two-sided')
            delta, interpretation = cliffs_delta.cliffs_delta(algo1[1], algo2[1])
            self.effect_size[(algo1[0], algo2[0])] = (delta, interpretation)
            self.effect_size[(algo2[0], algo1[0])] = (delta, interpretation)
            self.p_values[(algo1[0], algo2[0])] = p_value
            self.p_values[(algo2[0], algo1[0])] = p_value