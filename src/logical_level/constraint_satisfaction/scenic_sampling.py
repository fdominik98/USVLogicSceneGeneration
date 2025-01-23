import random, scenic
from scenic.core.scenarios import Scenario
from utils.file_system_utils import ASSET_FOLDER

random.seed(12345)
scenario : Scenario = scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/scenario.scenic')
scene, numIterations = scenario.generate()
print(f'ego has foo = {scene.egoObject.foo}')