from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import *
from visualization.my_plot import MyPlot
from visualization.colreg_scenarios.colreg_plot import TrajectoryReceiver
from visualization.colreg_scenarios.plot_components.metric_components.risk_metric_component import RiskMetricComponent
from trajectory_planning.proximity_evaluator import TrajProximityEvaluator, TrajNavigationRiskEvaluator
from visualization.colreg_scenarios.plot_components.metric_components.proximity_metrics_component import DistanceAxesComponent, DCPAAxesComponent, TCPAAxesComponent

class TrajectoryMetricsPlot(TrajectoryReceiver, MyPlot):  
    def __init__(self, env : USVEnvironment, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        MyPlot.__init__(self)
        TrajectoryReceiver.__init__(self, env, trajectories)
        
        self.proximity_evaluator = TrajProximityEvaluator(trajectories=self.trajectories, env=self.env)
        self.risk_evaluator = TrajNavigationRiskEvaluator(trajectories=self.trajectories, env=self.env)
        
        DistanceAxesComponent(self.axes[0], self.env, self.proximity_evaluator.metrics).draw()
        DCPAAxesComponent(self.axes[1], self.env, self.proximity_evaluator.metrics).draw()
        TCPAAxesComponent(self.axes[2], self.env, self.proximity_evaluator.metrics).draw()
        RiskMetricComponent(self.axes[3], self.env, self.risk_evaluator.risk_metrics).draw()
        
        
    def create_fig(self):
        fig, axes = plt.subplots(1, 4, figsize=(12, 4), gridspec_kw={'width_ratios': [1, 1, 1, 1]})
        fig.subplots_adjust(wspace=0.5)
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        
