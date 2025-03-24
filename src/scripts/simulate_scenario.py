import time
import traceback
from concrete_level.data_parser import EvalDataParser
from concrete_level.models.trajectory_manager import TrajectoryManager
from simulation.waraps_parser import WARAPSParser

def main():
    dp = EvalDataParser()
    data_models = dp.load_data_models()

    if len(data_models) == 0:
        exit(0)

    eval_data = data_models[0]
    trajectory_manager = TrajectoryManager(eval_data.best_scene)

    parser = WARAPSParser(trajectory_manager)

    for client in parser.agent_clients:
        client.connect()
        client.publish_command(parser.waypoint_map[client.vessel])
    try:
        while True:
            time.sleep(1)

    except Exception:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()