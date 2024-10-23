from collections import defaultdict
import pprint
from typing import Dict, List

import numpy as np

from evaluation.mann_whitney_u_cliff_delta import MannWhitneyUCliffDelta
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from visualization.algo_evaluation.algo_eval_utils import config_group_mapper


class TableGenerator():
    def __init__(self, eval_datas : List[EvaluationData]) -> None:
        self.eval_datas = eval_datas
        self.runtimes : Dict[int, Dict[str, List[float]]] = defaultdict(lambda : defaultdict(lambda : []))
        self.success_rates : Dict[int, Dict[str, List[int]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            group_key = eval_data.config_group
            self.success_rates[eval_data.vessel_number][group_key].append(0 if eval_data.best_fitness_index > 0.0 else 1)
            self.runtimes[eval_data.vessel_number][group_key].append(eval_data.evaluation_time)
        
        self.stat_sign_runtime : List[MannWhitneyUCliffDelta] = []
        self.stat_sign_success : List[FisherExactOddsRatio] = []
        self.average_runtimes : List[List[float]] = [[], []]
        self.success_rate_adjusted  : List[List[float]] = [[], []]
        
        for runtime_group_measurements, success_rate_group_measurements in zip(self.runtimes.values(), self.success_rates.values()): 
            if len(runtime_group_measurements) != 2:
                break
            runtime_data = list(runtime_group_measurements.values())
            success_rate_data = list(success_rate_group_measurements.values())
            group_labels = config_group_mapper(list(runtime_group_measurements.keys())) 
            
            mean_msr = np.mean(runtime_data[0])
            mean_sbo = np.mean(runtime_data[1])
            succ_msr = np.mean(success_rate_data[0])
            succ_sbo = np.mean(success_rate_data[1])
            
            self.average_runtimes[0] += [mean_msr]
            self.average_runtimes[1] += [mean_sbo]
            self.success_rate_adjusted[0] += [mean_msr / succ_msr]
            self.success_rate_adjusted[1] += [mean_sbo / succ_sbo]
                
            if len(runtime_data) != 0:
                stat_signif_runtime = MannWhitneyUCliffDelta({group : value for group, value in zip(group_labels, runtime_data)})
                stat_signif_success = FisherExactOddsRatio({group : value for group, value in zip(group_labels, success_rate_data)})
                self.stat_sign_runtime.append(stat_signif_runtime)
                self.stat_sign_success.append(stat_signif_success)
            
    def generate_stat_sign_table(self,):
        latex_code = "\\begin{tabular}{ccccc}\n"
        latex_code += "    \\toprule\n"
        latex_code += "    \(K\) & {} & {} & {} & {} \\\\\n".format(*[3, 4, 5, 6])
        latex_code += "    \\midrule\n"
        latex_code += "    \\textit{{p}} run t. & {:.0e} & {:.0e} & {:.0e} & {:.0e} \\\\\n".format(*[list(st.p_values_mann_w.values())[0] for st in self.stat_sign_runtime])
        latex_code += "    \\textit{{e}} run t. & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n".format(*[list(st.effect_sizes_cohens_d.values())[0] for st in self.stat_sign_runtime])
        latex_code += "    \\textit{{p}} suc. r. & {:.0e} & {:.0e} & {:.0e} & {:.0e} \\\\\n".format(*[list(st.p_values.values())[0] for st in self.stat_sign_success])
        latex_code += "    \\textit{{e}} suc. r. & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n".format(*[list(st.odds_ratios.values())[0] for st in self.stat_sign_success])
        latex_code += "    \\bottomrule\n"
        latex_code += "\\end{tabular}"
        print(latex_code)
        return latex_code
    
    
    def generate_runtime_summary_table(self):
        latex_code = "\\begin{tabular}{ccccc}\n"
        latex_code += "    \\toprule\n"
        latex_code += "    \(K\) & {} & {} & {} & {} \\\\\n".format(*[3, 4, 5, 6])
        latex_code += "    \\midrule\n"
        latex_code += "    Avg. time/run (s) & {:.1f} & {:.1f} & {:.1f} & {:.1f} \\\\\n".format(*self.average_runtimes[0])
        latex_code += "    (\\aMSR~| \\aSBO) & | {:.1f} & | {:.1f} & | {:.1f} & | {:.1f} \\\\\n".format(*self.average_runtimes[1])
        latex_code += "    Avg. time/scene (s) & {:.1f} & {:.1f} & {:.1f} & {:.1f} \\\\\n".format(*self.success_rate_adjusted[0])
        latex_code += "    (\\aMSR~| \\aSBO) & | {:.1f} & | {:.1f} & | {:.1f} & | {:.1f} \\\\\n".format(*self.success_rate_adjusted[1])
        latex_code += "    \\bottomrule\n"
        latex_code += "\\end{tabular}"
        print(latex_code)
        return latex_code