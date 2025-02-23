from datetime import datetime
import os
import tkinter as tk
from typing import Dict, List
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from utils.file_system_utils import ASSET_FOLDER
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.evaluation_plots.diversity_statistics_table import AmbiguousDiversityStatisticsTable, DiversityStatisticsTable
from visualization.evaluation_plots.runtime_statistics_table import RuntimeStatisticsTable
from visualization.evaluation_plots.scenario_type_statistics_plot import ScenarioTypeStatisticsPlot
from visualization.evaluation_plots.scenario_type_statistics_table import ScenarioTypeStatisticsTable
from visualization.plotting_utils import DummyEvalPlot, EvalPlot
from visualization.evaluation_plots.diversity_plot import AmbiguousDiversityPlot, DiversityPlot, UnspecifiedDiversityPlot
from visualization.evaluation_plots.risk_vector_plot import RiskVectorPlot
from visualization.evaluation_plots.runtime_plot import RuntimePlot
from visualization.evaluation_plots.success_rate_plot import SuccessRatePlot
class PlotWrapper():
    def __init__(self, plot_class, args):
        self.plot_class = plot_class
        self.args = args
        self.plot = None
    def get(self) -> EvalPlot:
        if self.plot is None:
            self.plot = self.plot_class(**self.args)
        return self.plot
    
class EvalPlotManager():
    def __init__(self, eval_datas : List[EvaluationData]): 
        self.eval_datas = eval_datas
        self.plots : Dict[str, PlotWrapper] = {
            "Home" : PlotWrapper(DummyEvalPlot, {'eval_datas': self.eval_datas}),
            "Scenario Type Statistics" : PlotWrapper(ScenarioTypeStatisticsPlot, {'eval_datas': self.eval_datas}),
            "Diversity" : PlotWrapper(DiversityPlot, {'eval_datas': self.eval_datas}),
            "Ambiguous Diversity" : PlotWrapper(AmbiguousDiversityPlot, {'eval_datas': self.eval_datas}),
            "Unspecified Diversity" : PlotWrapper(UnspecifiedDiversityPlot, {'eval_datas': self.eval_datas}),
            "Success Rate" : PlotWrapper(SuccessRatePlot, {'eval_datas': self.eval_datas, 'is_algo': False}),
            "Runtime (successful)" : PlotWrapper(RuntimePlot, {'eval_datas': self.eval_datas, 'is_all': False, 'is_algo': False}),
            "Runtime (all)" : PlotWrapper(RuntimePlot, {'eval_datas': self.eval_datas, 'is_all': True, 'is_algo': False}),
            "Risk Vector Proximity index" : PlotWrapper(RiskVectorPlot, {'eval_datas': self.eval_datas, 'metric' : 'proximity'}),
            "Risk Vector DS index" : PlotWrapper(RiskVectorPlot, {'eval_datas': self.eval_datas, 'metric' : 'ds'}),
            "Risk Vector DCPA" : PlotWrapper(RiskVectorPlot, {'eval_datas': self.eval_datas, 'metric' : 'dcpa'}),
            "Risk Vector TCPA" : PlotWrapper(RiskVectorPlot, {'eval_datas': self.eval_datas, 'metric' : 'tcpa'}),
            "Diversity Statistics Test" : PlotWrapper(DiversityStatisticsTable, {'eval_datas': self.eval_datas}),
            "Ambiguous Diversity Statistics Test" : PlotWrapper(AmbiguousDiversityStatisticsTable, {'eval_datas': self.eval_datas}),
            "Runtime Statistical Test" : PlotWrapper(RuntimeStatisticsTable, {'eval_datas': self.eval_datas}),
            'Scenario Type Statistical Test' : PlotWrapper(ScenarioTypeStatisticsTable, {'eval_datas': self.eval_datas}),
        }
        
        self.root = tk.Tk()
        self.root.resizable(True, True)
        self.image_folder = f'{ASSET_FOLDER}/images/exported_plots'
        
        self.root.option_add("*Font", ("Times New Roman", 14))
        
        self.root.title(f"Evaluation - {list(self.plots.keys())[0]}")

        # CANVAS FRAME
        self.canvas_frame = tk.Frame(master=self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            
        ## PLOT FRAME
        self.plot_frame = tk.Frame(master=self.canvas_frame)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = FigureCanvasTkAgg(list(self.plots.values())[0].get().fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # TOOLBAR FRAME
        self.toolbar_frame = tk.Frame(master=self.root, height=50)
        self.toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.toolbar_frame.pack_propagate(False)
        
        ## TOOLBAR
        self.navigation_frame = tk.Frame(self.toolbar_frame)
        self.navigation_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.navigation_toolbar = NavigationToolbar2Tk(self.canvas, self.navigation_frame)
        self.navigation_toolbar.update()
        self.navigation_toolbar.pack(fill=tk.BOTH, side=tk.LEFT)
        
        ## PLOT SELECTION
        self.plot_options = list(self.plots.keys())
        self.selected_plot = tk.StringVar()
        self.selected_plot.set(self.plot_options[0])  # Set the default value
        # Create the dropdown menu
        self.plot_dropdown = tk.OptionMenu(self.toolbar_frame, self.selected_plot, *self.plot_options, command=self.on_select_plot)
        self.plot_dropdown.pack(side=tk.LEFT, padx=5)
        
        self.to_pdf_button = tk.Button(self.toolbar_frame, text="PDF", command=self.to_pdf)
        self.to_pdf_button.pack(side=tk.LEFT, padx=5)
        self.root.bind('<e>', lambda event: self.to_pdf())
        
        ## EXIT BUTTONS
        exit_button = tk.Button(self.toolbar_frame, text="Exit", command=self.exit_application)
        exit_button.pack(side=tk.RIGHT, padx=5)
        continue_button = tk.Button(self.toolbar_frame, text="Continue", command=self.continue_application)
        continue_button.pack(side=tk.RIGHT, padx=5)
        
        self.root.wait_window()
        
        
    def sort_dict(self, dicts : List[Dict[str, plt.Artist]]) -> List[List[plt.Artist]]:
        artists = []
        for dict in dicts:
            artists.append([value for key, value in sorted(dict.items())])
        return artists
    
    def exit_application(self):
        self.root.destroy()
        os._exit(0)
        
    def continue_application(self):
        self.root.destroy()
        
    def to_pdf(self):
        file_name = f'{self.selected_plot.get()}_{datetime.now().isoformat().replace(":","-")}'
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
        self.canvas.figure.savefig(f'{self.image_folder}/{file_name}.svg', format='svg', bbox_inches='tight', dpi=350)
        self.canvas.figure.savefig(f'{self.image_folder}/{file_name}.pdf', format='pdf', bbox_inches='tight', dpi=350)
        print('image saved')
        
        
    def on_select_plot(self, value):
        plot = self.plots[value].get()        
        self.navigation_toolbar.destroy()
        self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(plot.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.navigation_toolbar = NavigationToolbar2Tk(self.canvas, self.navigation_frame)
        self.navigation_toolbar.update()
        self.navigation_toolbar.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.root.title(f"Evaluation - {value}")
        
  
  