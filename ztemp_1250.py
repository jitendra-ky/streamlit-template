import threading
import subprocess
import time
import os

# Directory to store PID files
pids = []
is_executing_error = [False]

def run_command(command: list[str]) -> None:
    """
    Executes a shell command in a separate thread and manages its PID.
    """
    command = [str(c) for c in command]
    print(f"Running command: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    child_pid = process.pid

    # Record the PID
    pids.append(str(child_pid))

    stdout, stderr = process.communicate()

    # Cleanup PID file
    if str(child_pid) in pids:
        pids.remove(str(child_pid))

    # check if the process is killed
    if is_executing_error[0]:
        print(f"Process {child_pid}: stoped the executing as in other thread error occurred")
        return

    if process.returncode == 0:
        print(f"process {child_pid}: Command finished successfully: {' '.join(command)}")
    else:
        print(f"process {child_pid}: Command failed: {' '.join(command)}\nError: {stderr.decode().strip()}")
        is_executing_error[0] = True
        stop_all_processes()
        return

def stop_all_processes():
    """
    Stops all running processes by killing them based on stored PIDs.
    """
    print("Stopping all running processes...")
    # print(pids)
    for pid in pids:
        # print(pid)
        try:
            os.kill(int(pid), 9)  # SIGKILL
            # print(f"Successfully killed process with PID: {pid}")
        except Exception as e:
            print(f"Failed to kill process with PID: {pid}. Error: {e}")
    pids.clear()

# Example usage
if __name__ == "__main__":
    commands = [
        ["ping", "127.0.0.1", "-n", "10"],
        ["ping", "127.0.0.1", "-n", "10"],
        ["ping", "127.0.0.1", "-n", "15"],
        ["python", "-c", "import time; time.sleep(3); raise Exception('Simulated Error')"]
    ]
    is_executing_error[0] = False
    
    threads = []
    for cmd in commands:
        thread = threading.Thread(target=run_command, args=(cmd,))
        thread.start()
        threads.append(thread)

    # Wait for threads to finish
    for thread in threads:
        thread.join()
