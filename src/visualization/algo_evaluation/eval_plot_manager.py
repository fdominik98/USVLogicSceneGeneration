from datetime import datetime
import os
import tkinter as tk
from typing import Dict, List
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from model.environment.usv_config import ASSET_FOLDER
from evolutionary_computation.evaluation_data import EvaluationData
from visualization.algo_evaluation.risk_vector_plot import RiskVectorPlot
from visualization.algo_evaluation.eval_time_plot import EvalTimePlot
from visualization.algo_evaluation.success_rate_plot import SuccessRatePlot

class EvalPlotManager():
    def __init__(self, eval_datas : List[EvaluationData]): 
        self.eval_datas = eval_datas
        self.algo_success_rate_plot = SuccessRatePlot(self.eval_datas, 'algo')
        self.config_success_rate_plot = None
        self.algo_eval_time_plot = None
        self.config_eval_time_plot = None
        self.risk_vector_plot = None
        self.metrics_plot = None
        self.root = tk.Tk()
        self.root.resizable(True, True)
        self.image_folder = f'{ASSET_FOLDER}/images/exported_plots'
        
        self.root.option_add("*Font", ("Times New Roman", 14))
        
        self.root.title("Evaluation")

        # CANVAS FRAME
        self.canvas_frame = tk.Frame(master=self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            
        ## PLOT FRAME
        self.plot_frame = tk.Frame(master=self.canvas_frame)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = FigureCanvasTkAgg(self.algo_success_rate_plot.fig, master=self.plot_frame)
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
        self.plot_options = ["Algo Success Rate", "Config Success Rate", "Config Eval Time", "Algo Eval Time", "Risk Vector"]
        self.selected_plot = tk.StringVar()
        self.selected_plot.set(self.plot_options[0])  # Set the default value
        # Create the dropdown menu
        self.plot_dropdown = tk.OptionMenu(self.toolbar_frame, self.selected_plot, *self.plot_options, command=self.on_select_plot)
        self.plot_dropdown.pack(side=tk.LEFT, padx=5)
        
        self.to_pdf_button = tk.Button(self.toolbar_frame, text="PDF", command=self.to_pdf)
        self.to_pdf_button.pack(side=tk.LEFT, padx=5)
        
        
        ## EXIT BUTTONS
        exit_button = tk.Button(self.toolbar_frame, text="Exit", command=self.exit_application)
        exit_button.pack(side=tk.RIGHT, padx=5)
        continue_button = tk.Button(self.toolbar_frame, text="Continue", command=self.continue_application)
        continue_button.pack(side=tk.RIGHT, padx=5)
        
        
        ## CONTROL FRAME
        self.control_frame = tk.Frame(master=self.canvas_frame, width=70)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

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
        self.canvas.figure.savefig(f'{self.image_folder}/{file_name}.svg', format='svg', dpi=350)
        self.canvas.figure.savefig(f'{self.image_folder}/{file_name}.pdf', format='pdf', dpi=350)
        print('image saved')
        
    def on_select_plot(self, value):
        if value == 'Algo Success Rate':
            plot = self.algo_success_rate_plot
        elif value == 'Config Success Rate':
            if self.config_success_rate_plot is None:
                self.config_success_rate_plot = SuccessRatePlot(self.eval_datas, mode='config')
            plot = self.config_success_rate_plot
        elif value == 'Config Eval Time':
            if self.config_eval_time_plot is None:
                self.config_eval_time_plot = EvalTimePlot(self.eval_datas, mode='config')
            plot = self.config_eval_time_plot
        elif value == 'Algo Eval Time':
            if self.algo_eval_time_plot is None:
                self.algo_eval_time_plot = EvalTimePlot(self.eval_datas, mode='algo')
            plot = self.algo_eval_time_plot
        elif value == 'Risk Vector':
            if self.risk_vector_plot is None:
                self.risk_vector_plot = RiskVectorPlot(self.eval_datas)
            plot = self.risk_vector_plot
        else:
            raise Exception('Not implemented plot.')
        self.navigation_toolbar.destroy()
        self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(plot.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.navigation_toolbar = NavigationToolbar2Tk(self.canvas, self.navigation_frame)
        self.navigation_toolbar.update()
        self.navigation_toolbar.pack(fill=tk.BOTH, side=tk.LEFT)
        
  