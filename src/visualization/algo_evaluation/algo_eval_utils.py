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
        label = ''
        if 'nsga2' in name.lower():
            label = 'NSGA2'
        elif 'nsga3' in name.lower():
            label = 'NSGA3'
        elif 'ga' in name.lower():
            label = 'GA'
        elif 'de' in name.lower():
            label = 'DE'
        elif 'pso' in name.lower():
            label = 'PSO'
        else:
            raise Exception('Unknown measurement name')
        aggregate = ''
        if 'all' in name.lower():
            aggregate = 'A'
        elif 'vessel' in name.lower():
            aggregate = 'V'
        elif 'category' in name.lower():
            aggregate = 'C'
        else:
            raise Exception('Unknown measurement name')
        labels.append(label + '_' + aggregate)
    return labels

full_blue_spectrum_shades = [(i / 4, 0.5, 1 - i / 4) for i in range(5)]
algo_colors = full_blue_spectrum_shades