import os

def modify_labels(directory):
    """
    Modifies all labels.txt files in the given directory.
    Changes class '3' to class '0' if it appears as the first number in each line.
    """
    count=0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):  # Ensuring we modify only text files
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                modified_lines = []
                for line in lines:
                    parts = line.split()
                    if parts and parts[0] != '0':  # Checking the first number
                        # print("count ",count)
                        # count=count+1
                        parts[0] = '0'  # Changing it to '0'
                    modified_lines.append(' '.join(parts) + '\n')
                
                with open(file_path, 'w') as f:
                    f.writelines(modified_lines)
                
                print(f"Updated {file_path}")

# Example usage
directory_path = "/home/cotseeds11/Desktop/v12/test/labels"  # Change this to your labels directory
modify_labels(directory_path)
