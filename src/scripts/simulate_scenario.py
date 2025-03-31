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

    # Main loop: wait for a number input corresponding to a command index.
    while True:
        try:
            user_input = input("Enter command number: ").strip()
            # Convert the user input to an integer.
            command = int(user_input)
            
            for client in parser.agent_clients:
                # Get the command list for this client.
                if command == 1:
                    client.publish_command(parser.waypoint_map[client.vessel], trajectory_manager.concrete_scene[client.vessel].speed)
                    print(f"Sent command {command} to vessel {client.vessel}")
                else:
                    print(f"Invalid command number for vessel {client.vessel}.")
        except Exception:
            print(traceback.format_exc())
        
        # Optional: pause briefly between loops.
        time.sleep(1)

if __name__ == "__main__":
    main()