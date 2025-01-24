import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from utils.file_system_utils import ASSET_FOLDER
from scenic.simulators.newtonian import NewtonianSimulator

random.seed(12345)
scenario : Scenario = scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/scenario.scenic', model='scenic.simulators.newtonian.model')
scene, numIterations = scenario.generate(maxIterations=np.inf)
simulator = NewtonianSimulator(render=True).simulate(scene, maxSteps=10, timestep=10)