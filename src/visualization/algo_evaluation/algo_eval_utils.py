from typing import List


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
        labels.append(label + '_' + aggregate)
    return labels


def config_group_mapper(config_groups : List[str]):
    labels : List[str] = []
    for name in config_groups:
        if 'f4' in name.lower():
            labels.append(r'$F_4$')
        elif 'f3' in name.lower():
           labels.append(r'$F_3$')
        elif 'f2' in name.lower():
            labels.append(r'$F_2$')
        elif 'f1' in name.lower():
            labels.append(r'$F_1$')
        else:
            raise Exception('Unknown config group name')
    return labels

full_blue_spectrum_shades = [(i / 8, 0.5, 1 - i / 8) for i in range(9)]
algo_colors = full_blue_spectrum_shades