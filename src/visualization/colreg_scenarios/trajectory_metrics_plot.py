from typing import Dict, List, Optional, Tuple
from matplotlib import gridspec
import matplotlib.pyplot as plt
from model.environment.usv_environment import LogicalScenario
from model.environment.usv_config import *
from visualization.my_plot import MyPlot
from visualization.colreg_scenarios.colreg_plot import TrajectoryReceiver
from visualization.colreg_scenarios.plot_components.metric_components.risk_metric_component import RiskMetricComponent
from trajectory_planning.proximity_evaluator import TrajProximityEvaluator, TrajNavigationRiskEvaluator
from visualization.colreg_scenarios.plot_components.metric_components.proximity_metrics_component import DistanceAxesComponent, DCPAAxesComponent, TCPAAxesComponent

class TrajectoryMetricsPlot(TrajectoryReceiver, MyPlot):  
    def __init__(self, env : LogicalScenario, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float, float]]]] = None): 
        MyPlot.__init__(self)
        TrajectoryReceiver.__init__(self, env, trajectories)
        
        self.proximity_evaluator = TrajProximityEvaluator(trajectories=self.trajectories, env=self.env)
        self.risk_evaluator = TrajNavigationRiskEvaluator(trajectories=self.trajectories, env=self.env)
        
        ref_trajs = self.gen_trajectories()
        for id in ref_trajs.keys():
            if id != 0 and trajectories is not None:
                ref_trajs[id] = trajectories[id]
        self.ref_proximity_evaluator = TrajProximityEvaluator(trajectories=ref_trajs, env=self.env)
        self.ref_risk_evaluator = TrajNavigationRiskEvaluator(trajectories=ref_trajs, env=self.env)
        
        DistanceAxesComponent(self.axes[0], self.env, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        DCPAAxesComponent(self.axes[1], self.env, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        TCPAAxesComponent(self.axes[2], self.env, self.proximity_evaluator.metrics, self.ref_proximity_evaluator.metrics).draw()
        #RiskMetricComponent(self.axes[3], self.env, self.risk_evaluator.proximity_metrics, 'Proximity index', True, self.ref_risk_evaluator.proximity_metrics).draw()
        RiskMetricComponent(self.axes[3], self.env, self.risk_evaluator.danger_sector_metrics, 'DS-based index', True, self.ref_risk_evaluator.danger_sector_metrics).draw()
        
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
        
