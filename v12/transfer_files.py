import shutil
import os

# Define source and destination folders
source_folder = "/home/cotseeds11/Desktop/v12/f/valid/labels"
destination_folder = "/home/cotseeds11/Desktop/v12/valid/labels"

# Ensure destination folder exists
os.makedirs(destination_folder, exist_ok=True)
count=1
# Move all files from source to destination
for file_name in os.listdir(source_folder):
    print("count : ",count)
    count+=1
    source_path = os.path.join(source_folder, file_name)
    destination_path = os.path.join(destination_folder, file_name)
    
    if os.path.isfile(source_path):  # Ensure it's a file
        shutil.move(source_path, destination_path)

print("All files have been moved successfully!")
