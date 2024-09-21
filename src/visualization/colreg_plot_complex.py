from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from model.usv_environment import USVEnvironment
from model.usv_config import *
from visualization.risk_metric_component import RiskMetricComponent
from visualization.colreg_plot import ColregPlot
from trajectory_planning.proximity_evaluator import ProximityEvaluator, RiskEvaluator
from visualization.proximity_metrics_component import DistanceAxesComponent, DCPAAxesComponent, TCPAAxesComponent

class ColregPlotComplex(ColregPlot):  
    def __init__(self, env : USVEnvironment, block=True, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        super().__init__(env, block, trajectories)  
        
        self.proximity_evaluator = ProximityEvaluator(trajectories=self.trajectories, env=self.env)
        self.risk_evaluator = RiskEvaluator(trajectories=self.trajectories, env=self.env)
        self.components += [
            DistanceAxesComponent(self.axes[1], self.env, self.proximity_evaluator.metrics),
            DCPAAxesComponent(self.axes[2], self.env, self.proximity_evaluator.metrics),
            TCPAAxesComponent(self.axes[3], self.env, self.proximity_evaluator.metrics),
            RiskMetricComponent(self.axes[4], self.env, self.risk_evaluator.risk_metrics),
        ] 
        
    def create_fig(self):
        fig, axes = plt.subplots(1, 5, figsize=(12, 4), gridspec_kw={'width_ratios': [1, 1, 1, 1, 1]})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        self.ax : plt.Axes = self.axes[0]
        
