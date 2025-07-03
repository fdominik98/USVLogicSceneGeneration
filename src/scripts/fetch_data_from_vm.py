import stat
from multiprocessing import Process
from typing import List
import paramiko
import os
from tqdm import tqdm

from utils.evaluation_config import SB
from utils.file_system_utils import GEN_DATA_FOLDER, SSH_KEY_FILE

ADDRESSES = {
    "measurements" : "129.192.68.81",
    # "measurements2" : "129.192.70.172",
    # "measurements3" : "129.192.69.183",
    # "measurements4" : "129.192.69.250",
}

base_folders = ["Base_test_2_vessel_0_obstacle_scenarios",
                "Base_test_3_vessel_0_obstacle_scenarios",
                "Base_test_4_vessel_0_obstacle_scenarios",
                "Base_test_5_vessel_0_obstacle_scenarios",
                "Base_test_6_vessel_0_obstacle_scenarios"]

msr_folders = ["MSR_test_2_vessel_0_obstacle_scenarios",
                "MSR_test_3_vessel_0_obstacle_scenarios",
                "MSR_test_4_vessel_0_obstacle_scenarios",
                "MSR_test_5_vessel_0_obstacle_scenarios",
                "MSR_test_6_vessel_0_obstacle_scenarios"]

FOLDERS = {
    "measurements" : [f'{f}/{SB.upper()}' for f in base_folders],
    # "measurements2" : [f'{f}/{RS.upper()}' for f in base_folders],
    # "measurements3" : [f'{f}/{TS_RS.upper()}' for f in base_folders]",
    # "measurements4" : [f'{f}/{CD_RS.upper()}' for f in msr_folders],
}

def fetch_files_over_ssh(hostname, port, key_filepath, remote_folder : str, local_folder, measurement_folders : List[str]):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect
        key = paramiko.RSAKey.from_private_key_file(key_filepath)
        ssh.connect(hostname=hostname, port=port, username='ubuntu', pkey=key, key_filename=key_filepath)

        sftp = ssh.open_sftp()

        files_to_download = []
        total_bytes = 0

        for measurement_folder in measurement_folders:
            new_remote_folder = f'{remote_folder}/{measurement_folder}'
            def list_leaf_files(sftp : paramiko.SFTPClient, remote_dir : str):
                leaf_files = []
                for entry in sftp.listdir_attr(remote_dir):
                    remote_path = f'{remote_dir}/{entry.filename}'

                    if stat.S_ISDIR(entry.st_mode):  # Check if it's a directory
                        # Recurse into subdirectory
                        leaf_files.extend(list_leaf_files(sftp, remote_path))
                    else:
                        leaf_files.append(paramiko.SFTPAttributes())
                        leaf_files[-1].__dict__.update(entry.__dict__)
                        leaf_files[-1].filename = os.path.relpath(remote_path, new_remote_folder).replace('\\', '/')  # Normalize path for consistency
                return leaf_files
            file_list = list_leaf_files(sftp, new_remote_folder)

            # Calculate total bytes to download
            for file_attr in file_list:
                filename = file_attr.filename
                remote_file = f'{new_remote_folder}/{filename}'
                local_file = f'{local_folder}/{measurement_folder}/{filename}'
                file_size = file_attr.st_size

                # Skip existing complete files
                if os.path.exists(local_file): #and os.path.getsize(local_file) == file_size:
                    print(f"✔️ Skipping {filename} (already exists and is complete)")
                    continue

                files_to_download.append((remote_file, local_file, file_size))
                total_bytes += file_size

        # Create global progress bar
        with tqdm(total=total_bytes, unit='B', unit_scale=True, desc="Total Progress", ascii=True) as global_pbar:
            for remote_file, local_file, file_size in files_to_download:
                #print(f"⬇️ Downloading {os.path.basename(remote_file)} ({file_size} bytes)")

                def callback_transferred(bytes_transferred, total_bytes_inner):
                    global_pbar.update(bytes_transferred - callback_transferred.last_bytes)
                    callback_transferred.last_bytes = bytes_transferred

                callback_transferred.last_bytes = 0
                try:
                    os.makedirs(os.path.dirname(local_file), exist_ok=True)
                    sftp.get(remote_file, local_file, callback=callback_transferred)
                except Exception as e:
                    print(f"❌ Failed to download {os.path.basename(remote_file)}: {e}")
                    continue

        sftp.close()
        ssh.close()
        print("✅ All files transferred successfully.")

    except Exception as e:
        print(f"❌ Failed to fetch files: {e}")

# Example usage
if __name__ == "__main__":
    
    processes: List[Process] = []
    for measurement_name, address in ADDRESSES.items():
        process = Process(target=fetch_files_over_ssh, kwargs={
            "hostname": address,
            "port": 22,
            "key_filepath": SSH_KEY_FILE,
            "remote_folder": f"/home/ubuntu/Desktop/USVLogicSceneGeneration/assets/gen_data",
            "local_folder": f"{GEN_DATA_FOLDER}",
            "measurement_folders": FOLDERS[measurement_name]
        })
        process.start()
        processes.append(process)
    for p in processes:
        p.join()
            