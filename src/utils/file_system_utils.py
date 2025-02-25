import os

ASSET_FOLDER = f'{os.path.dirname(os.path.abspath(__file__))}/../../assets'

ROOT_FOLDER = f'{os.path.dirname(os.path.abspath(__file__))}/../..'

def get_all_file_paths(directory, extension):
    if not os.path.isdir(directory):
        raise ValueError('THe path is not a directory or invalid.')
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if f'.{extension}' in file:
                file_paths.append(os.path.join(root, file))
    return file_paths