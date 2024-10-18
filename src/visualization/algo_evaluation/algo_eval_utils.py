from typing import List

from matplotlib.colors import to_rgb
import numpy as np


def vessel_number_mapper(vessel_nums : List[int]):
    labels : List[str] = []
    for vessel_num in vessel_nums:
        if vessel_num == 6:
            labels.append('6 Vessels')
        elif vessel_num == 5:
            labels.append('5 Vessels') 
        elif vessel_num == 4:
            labels.append('4 Vessels')
        elif vessel_num == 3:
            labels.append('3 Vessels')
        else:
            raise Exception('Unknown measurement name')
    return labels
        
def algo_mapper(names : List[str]):
    labels : List[str] = []
    for name in names:
        label = ''
        if 'nsga2' in name.lower():
            label = 'N2'
        elif 'nsga3' in name.lower():
            label = 'N3'
        elif 'ga' in name.lower():
            label = 'GA'
        elif 'de' in name.lower():
            label = 'DE'
        elif 'pso' in name.lower():
            label = 'PSO'
        else:
            raise Exception('Unknown algorithm name')
        aggregate = ''
        if 'all' in name.lower():
            aggregate = 'A'
        elif 'vessel' in name.lower():
            aggregate = 'V'
        elif 'category' in name.lower():
            aggregate = 'C'
        else:
            aggregate = ''
        labels.append(label + '-' + aggregate)
    return labels


def config_group_mapper(config_groups : List[str]):
    labels : List[str] = []
    for name in config_groups:
        if 'sbo' in name.lower():
            labels.append('SBO')
        elif 'msr' in name.lower():
            labels.append('MSR')
        elif 'f3' in name.lower():
           labels.append(r'$F_3$')
        elif 'f2' in name.lower():
            labels.append(r'$F_2$')
        elif 'f1' in name.lower():
            labels.append(r'$F_1$')
        else:
            raise Exception('Unknown config group name')
    return labels

def group_colors(size):
    # Convert the colors to RGB format
    color1_rgb = np.array((0, 0.5, 1))
    if size == 1:
        return color1_rgb
    color2_rgb = np.array((1, 0.5, 0))
    # Generate a range of colors by linear interpolation
    colors = [color1_rgb + (color2_rgb - color1_rgb) * i / (size - 1) for i in range(size)]
    return [np.array([color[0], color[1], color[2], 0.7]) for color in colors]
