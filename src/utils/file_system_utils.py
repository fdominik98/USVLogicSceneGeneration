import os

ASSET_FOLDER = f'{os.path.dirname(os.path.abspath(__file__))}/../../assets'

GEN_DATA_FOLDER = f'{ASSET_FOLDER}/gen_data'
FUNCTIONAL_MODELS_FOLDER = f'{ASSET_FOLDER}/functional_models'
SCENIC_FOLDER = f'{ASSET_FOLDER}/scenic'
COMMON_OCEAN_FOLDER = f'{ASSET_FOLDER}/common_ocean_scenarios'
PROJECT_REPORT_FOLDER = f'{ASSET_FOLDER}/project_report'
IMAGES_FOLDER = f'{ASSET_FOLDER}/images'
EXPORTED_PLOTS_FOLDER = f'{IMAGES_FOLDER}/exported_plot'
SIMULATION_FOLDER = f'{ASSET_FOLDER}/simulation'

from pathlib import Path

_initialized = False  # Global flag

def ensure_directories():
    global _initialized
    if _initialized:
        return  # Skip if already initialized

    folders = [
        ASSET_FOLDER,
        GEN_DATA_FOLDER,
        FUNCTIONAL_MODELS_FOLDER,
        SCENIC_FOLDER,
        COMMON_OCEAN_FOLDER,
        PROJECT_REPORT_FOLDER,
        IMAGES_FOLDER,
        EXPORTED_PLOTS_FOLDER,
        SIMULATION_FOLDER,
    ]

    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)

    _initialized = True  # Mark as initialized

# Call once at the beginning
ensure_directories()



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