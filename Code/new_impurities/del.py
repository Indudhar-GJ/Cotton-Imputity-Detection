import roboflow
import os

# Initialize Roboflow with your API key
rf = roboflow.Roboflow(api_key="iBOcTr8aEyP11fHTJ9fS")

print(rf.workspace())
# Define workspace and project
workspace_id = "testing-huzh8"
project_id = "test-pznlf"
project = rf.workspace(workspace_id).project(project_id)

# Specify the folder containing images
folder_path = "/home/cotseeds11/Desktop/Cotseeds_Final/Code/new_impurities"

# Loop through each image in the folder and upload it
for filename in os.listdir(folder_path):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):  # Filter for image files
        image_path = os.path.join(folder_path, filename)
        print(f"Uploading {filename}...")
        project.upload(
            image_path=image_path,
            batch_name="Batch1",
            split="train",
            num_retry_uploads=3
        )

print("All images uploaded successfully!")

# from roboflow import Roboflow
# rf = Roboflow(api_key="iBOcTr8aEyP11fHTJ9fS")
# print(rf.workspace().projects())  # List all accessible workspaces

# testing-huzh8/test-pznlf