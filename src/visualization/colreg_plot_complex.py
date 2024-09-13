from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from model.usv_environment import USVEnvironment
from model.usv_config import *
from visualization.risk_metric_component import RiskMetricComponent
from visualization.colreg_plot import ColregPlot
from trajectory_planning.proximity_evaluator import ProximityEvaluator, RiskEvaluator
from visualization.proximity_metrics_component import DistanceAxesComponent, DCPAAxesComponent, TCPAAxesComponent
from visualization.ship_image_component import ShipImageComponent
from visualization.prime_component import PrimeComponent
from visualization.angle_circle_component import AngleCircleComponent
from visualization.distance_component import DistanceComponent
from visualization.vo_cone_component import VOConeComponent
from visualization.additional_vo_cone_component import AdditionalVOConeComponent

class ColregPlotComplex(ColregPlot):  
    def __init__(self, env : USVEnvironment, block=True, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        super().__init__(env, block, trajectories)   
        
    def create_fig(self):
        fig, axes = plt.subplots(1, 5, figsize=(12, 4), gridspec_kw={'width_ratios': [1, 1, 1, 1, 1]})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        self.ax : plt.Axes = self.axes[0]
        
    def configure(self):
        self.proximity_evaluator = ProximityEvaluator(trajectories=self.trajectories, env=self.env)
        self.risk_evaluator = RiskEvaluator(trajectories=self.trajectories, env=self.env)
        
        self.components |= {
            'distance' : DistanceAxesComponent(self.axes[1], True, self.env, self.proximity_evaluator.metrics),
            'DCPA' : DCPAAxesComponent(self.axes[2], True, self.env, self.proximity_evaluator.metrics),
            'TCPA' : TCPAAxesComponent(self.axes[3], True, self.env, self.proximity_evaluator.metrics),
            'RISK' : RiskMetricComponent(self.axes[4], True, self.env, self.risk_evaluator.risk_metrics),
            '2' : VOConeComponent(self.ax, False, self.env),
            '3' : AdditionalVOConeComponent(self.ax, False, self.env),
            '1' : DistanceComponent(self.ax, False, self.env),
            '6' : AngleCircleComponent(self.ax, False, self.env, linewidth=1.5),
            '8' : PrimeComponent(self.ax, False, self.env),
            '9' : ShipImageComponent(self.ax, True, self.env)                   
        }
