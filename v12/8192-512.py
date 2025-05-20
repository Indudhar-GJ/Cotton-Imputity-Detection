import cv2
import os

# Input folder containing images
input_folder = "/home/cotseeds11/Desktop/v12/images"

# Output folders
output_folders = ["output_tiles_10", "output_tiles_20", "output_tiles_30", "output_tiles_40"]

# Create output folders if they don't exist
for folder in output_folders:
    os.makedirs(folder, exist_ok=True)

# Get all image files in the input folder and sort them
image_files = sorted(os.listdir(input_folder))

# Process each image
for index, image_file in enumerate(image_files):
    image_path = os.path.join(input_folder, image_file)

    # Load image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Skipping {image_path}, unable to read.")
        continue

    # Get image dimensions
    h, w, _ = image.shape

    # Validate image size
    if w != 8192 or h != 512:
        print(f"Skipping {image_path}, incorrect dimensions: {w}x{h}")
        continue

    # Get the base name of the image (without extension)
    image_name = os.path.splitext(image_file)[0]

    # Split and distribute tiles into different folders
    for j in range(16):  # 16 tiles per image
        tile = image[:, j * 512:(j + 1) * 512]  # Slice the width
        
        # Assign tile to one of the 4 folders in a round-robin fashion
        folder_index = (j % 4)  # Distribute tiles evenly across the 4 folders
        tile_filename = os.path.join(output_folders[folder_index], f"{image_name}_tile_{j}.jpg")
        
        cv2.imwrite(tile_filename, tile)

    print(f"Processed {image_path}, tiles distributed into 4 folders")

print("Processing complete.")

