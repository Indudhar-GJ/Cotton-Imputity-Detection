import subprocess
import time

script_path = "/media/cotseeds33/FreeAgent Drive/cotseeds/Cotseeds_Final/Code/GUI1.py"  # Change this to your script's filename

def run_script_for_duration(script, duration=30):
    print("Started running the script")
    process = subprocess.Popen(["python3", script])  # Runs the script
    
    try:
        time.sleep(duration)  # Wait for the specified duration
    except KeyboardInterrupt:
        print("Stopping early...")
    finally:
        process.terminate()  # Stop the script
        process.wait()
        print("Script stopped.")

if __name__ == "__main__":
    run_script_for_duration(script_path)

