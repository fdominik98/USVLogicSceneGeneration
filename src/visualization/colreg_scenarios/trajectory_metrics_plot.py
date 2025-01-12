from typing import List, Union
from matplotlib import gridspec
import matplotlib.pyplot as plt
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.trajectories import Trajectories
from utils.asv_utils import *
from visualization.my_plot import MyPlot
from visualization.colreg_scenarios.colreg_plot import TrajectoryReceiver
from visualization.colreg_scenarios.plot_components.metric_components.risk_metric_component import RiskMetricComponent
from evaluation.proximity_evaluator import TrajProximityEvaluator, TrajNavigationRiskEvaluator
from visualization.colreg_scenarios.plot_components.metric_components.proximity_metrics_component import DistanceAxesComponent, DCPAAxesComponent, TCPAAxesComponent

class TrajectoryMetricsPlot(TrajectoryReceiver, MyPlot):  
    def __init__(self, trajectories : Union[Trajectories, ConcreteScene]): 
        MyPlot.__init__(self)
        TrajectoryReceiver.__init__(self, trajectories)
        
        self.proximity_evaluator = TrajProximityEvaluator(trajectories=self.trajectories)
        self.risk_evaluator = TrajNavigationRiskEvaluator(trajectories=self.trajectories)

        self.ref_proximity_evaluator = TrajProximityEvaluator(trajectories=self.default_trajectories)
        self.ref_risk_evaluator = TrajNavigationRiskEvaluator(trajectories=self.default_trajectories)
        
        DistanceAxesComponent(self.axes[0], self.trajectories, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        DCPAAxesComponent(self.axes[1], self.trajectories, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        TCPAAxesComponent(self.axes[2], self.trajectories, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        #RiskMetricComponent(self.axes[3], self.trajectories, self.risk_evaluator.proximity_metrics, 'Proximity index', True, self.ref_risk_evaluator.proximity_metrics).draw()
        RiskMetricComponent(self.axes[3], self.trajectories, self.risk_evaluator.danger_sector_metrics, 'DS-based index', True, self.ref_risk_evaluator.danger_sector_metrics).draw()
        
        self.fig.tight_layout()
        
        
    def create_fig(self):
        self.fig : plt.Figure = plt.figure(figsize=(12, 3))
        # Create a GridSpec with 2 rows and 2 columns
        gs = gridspec.GridSpec(2, 3, height_ratios=[1,1], width_ratios=[1, 1, 1])

        ax4 = self.fig.add_subplot(gs[0, 2])
        # Create axes for the first column (occupying both rows)
        ax1 = self.fig.add_subplot(gs[1, 0])
        ax2 = self.fig.add_subplot(gs[1, 1])
        ax3 = self.fig.add_subplot(gs[1, 2])

        #ax5 = self.fig.add_subplot(gs[1, 3])
        
        self.fig.subplots_adjust(wspace=0.5)
        
        self.axes : List[plt.Axes] = [ax1, ax2, ax3, ax4]
        
