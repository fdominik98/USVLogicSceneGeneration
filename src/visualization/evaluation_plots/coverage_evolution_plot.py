from typing import List, Set, Tuple
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
from functional_level.models.model_parser import ModelParser
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from utils.evaluation_config import SB_BASE, SB_MSR, RS, TS_CD_RS
from visualization.plotting_utils import EvalPlot

class CoverageEvolutionPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], is_second_level_abstraction = False): 
        self.is_second_level_abstraction = is_second_level_abstraction
        super().__init__(eval_datas, is_all=True)
        
    @property   
    def config_groups(self) -> List[str]:
        #return [SB_BASE, RS, SB_MSR, TS_CD_RS, 'common_ocean_benchmark']
        return [SB_BASE, RS, SB_MSR, TS_CD_RS]
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        #return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        
    
    def calculate_coverages_by_timestamps(self, actor_numbers_by_type : Tuple[int, int], comparison_group : str, seed : int,
                                          timestamps : np.ndarray, pred) -> List[float]:
        data = self.measurements[actor_numbers_by_type][comparison_group][seed]
        coverage = [(0, 0.0)]
        covered_classes : Set[int] = set()
        coverages_by_timestamp = []
        
        for d in data:
            next_timestamp = coverage[-1][1] + d.evaluation_time
            if d.is_valid and d.best_scene.second_level_hash not in covered_classes and pred(d):
                covered_classes.add(d.best_scene.second_level_hash)
            coverage.append((len(covered_classes), next_timestamp))
                
        # find the last timestamp in the coverage that is less than or equal to each timestamp in timestamps
        for timestamp in timestamps:
            last_coverage = next((c for c in reversed(coverage) if c[1] <= timestamp), None)
            if last_coverage is not None:
                coverages_by_timestamp.append(last_coverage[0] / ModelParser.TOTAL_FECS[actor_numbers_by_type] * 100)
            else:
                coverages_by_timestamp.append(coverages_by_timestamp[-1] if coverages_by_timestamp else 0)
        return coverages_by_timestamp
    
    def aggregate_data(self, actor_numbers_by_type : Tuple[int, int], comparison_group : str,
                            timestamps : np.ndarray, pred) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        seeds = self.measurements[actor_numbers_by_type][comparison_group].keys()
        if len(seeds) == 0:
            return np.array([0]*timestamps), np.array([0]*timestamps), np.array([0]*timestamps)
        # Create a 2D array: rows = seeds, columns = timestamps
        coverages_by_seed = []
        for seed in seeds:
            coverages = self.calculate_coverages_by_timestamps(actor_numbers_by_type, comparison_group, seed, timestamps, pred)
            coverages_by_seed.append(coverages)
        # Now coverages_by_seed is a list of lists: [ [cov_t1, cov_t2, ...], ... for each seed ]
        coverages_by_seed = np.array(coverages_by_seed)  # shape: (num_seeds, num_timestamps)
        # Calculate median, q1, q3 across seeds for each timestamp
        median = np.median(coverages_by_seed, axis=0)
        q1 = np.percentile(coverages_by_seed, 25, axis=0)
        q3 = np.percentile(coverages_by_seed, 75, axis=0)
        print(median[-1])
        return median, q1, q3
    
    @staticmethod
    def calculate_runtime(data : List[EvaluationData]) -> float:
        """Calculate the total runtime for a list of EvaluationData."""
        return sum(d.evaluation_time for d in data)
    
    def create_timestamps(self, actor_numbers_by_type) -> np.ndarray:
        max_runtime = 0.0
        for comparison_group in self.comparison_groups:
            for seed in self.measurements[actor_numbers_by_type][comparison_group].keys():
                runtime = self.calculate_runtime(self.measurements[actor_numbers_by_type][comparison_group][seed])
                if runtime > max_runtime:
                    max_runtime = runtime
        return np.linspace(0, max_runtime, 400)
    
    
    def crop_data(self, timestamps : np.ndarray, data : List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Tuple[np.ndarray, List[Tuple[np.ndarray, np.ndarray, np.ndarray]]]:
        # Find the last index where any y-series changes
        last_change_indices = []

        for median, q1, q3 in data:
            change_indices = np.where((np.diff(median) != 0) | (np.diff(q1) != 0) | (np.diff(q3) != 0))[0]
            if len(change_indices) > 0:
                last_change = change_indices[-1] + 1  # +1 to include the last change point
                last_change_indices.append(last_change)

        # Determine the global last change index
        if last_change_indices:
            global_last_change_index = max(last_change_indices)
        else:
            global_last_change_index = len(timestamps) - 1  # No change in any series
            
        timestamps_trimmed = timestamps[:global_last_change_index + 1]
        data_trimmed = [(median[:global_last_change_index + 1], q1[:global_last_change_index + 1], q3[:global_last_change_index + 1],) for median, q1, q3 in data]
        return timestamps_trimmed, data_trimmed
            
            
    def create_fig(self) -> plt.Figure:
        fig = plt.figure(figsize=(3 * self.vessel_num_count, 1.5 * 1), constrained_layout=True)
        gs = gridspec.GridSpec(1, self.vessel_num_count, height_ratios=[1]) 
        # Top axes spans all 6 columns
        ax_top = [fig.add_subplot(gs[0, i]) for i in range(self.vessel_num_count)] 
        # Bottom row: 6 equal-width axes
        # ax_bottom = [fig.add_subplot(gs[1, i]) for i in range(self.vessel_num_count)] 
        # axes = [ax_top, ax_bottom]
        axes = [ax_top]
        
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            axi : plt.Axes = axes[0][i]
            axi.set_title(self.vessel_num_labels[i], fontweight='bold')   
            row_label = "Covered\n" + r"$\bf{relevant}$" +"\nFECs" 
            self.init_axi(i, axi, row_label)
            if i == 0:
                self.set_yticks(axi, range(101), unit='%', tick_number=6)
            axi.set_ylim(0, 105)
            
            timestamps = self.create_timestamps(actor_number_by_type)
            data = []
            for j, comparison_group in enumerate(self.comparison_groups):
                median, q1, q3 = self.aggregate_data(actor_number_by_type, comparison_group, timestamps, lambda d : d.best_scene.is_relevant_by_fec)
                data.append((median, q1, q3))
                
            timestamps, data = self.crop_data(timestamps, data)
            
            for j, comparison_group in enumerate(self.comparison_groups):                        
                median, q1, q3 = data[j]                
                axi.plot(timestamps, median, color=self.colors[j], linestyle='-', linewidth=1.5, label=r"$\bf{" + self.group_labels[j] + r"}$")
                
                axi.fill_between(timestamps, q1, q3, color=self.colors[j], alpha=0.3)
                
                self.set_xticks(axi, timestamps, unit='s', tick_number=6)
                
        # Get handles and labels from the last axis (or any axis — all are the same here)
        handles, labels = axes[0][0].get_legend_handles_labels()
        # Add one legend to the figure (outside bottom)
        axes[0][0].legend(handles, labels, ncol=1, fontsize=10, loc='lower right')
        return fig
        