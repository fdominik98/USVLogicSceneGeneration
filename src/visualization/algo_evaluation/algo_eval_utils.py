from typing import List


def vessel_number_mapper(names : List[str]):
    labels : List[str] = []
    for name in names:
        if '6' in name.lower():
            labels.append('6 Vessels')
        elif '5' in name.lower():
            labels.append('5 Vessels') 
        elif '4' in name.lower():
            labels.append('4 Vessels')
        elif '3' in name.lower():
            labels.append('3 Vessels')
        else:
            raise Exception('Unknown measurement name')
    return labels
        
def algo_mapper(names : List[str]):
    labels : List[str] = []
    for name in names:
        if 'nsga2' in name.lower():
            labels.append('NSGA2') 
        elif 'nsga3' in name.lower():
            labels.append('NSGA3')
        elif 'ga' in name.lower():
            labels.append('GA')
        elif 'de' in name.lower():
            labels.append('DE')
        elif 'pso' in name.lower():
            labels.append('PSO')
        else:
            raise Exception('Unknown measurement name')
    return labels

full_blue_spectrum_shades = [(i / 4, 0.5, 1 - i / 4) for i in range(5)]
algo_colors = full_blue_spectrum_shades