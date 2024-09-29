from abc import ABC, abstractmethod
from matplotlib import pyplot as plt


class MyPlot(ABC):
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 12
   
    def __init__(self) -> None:
        super().__init__()
        self.create_fig()
        
        
    @abstractmethod
    def create_fig(self):
        pass