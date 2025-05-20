import os
import re
from collections import defaultdict

def count_unique_first_numbers(folder_path):
    number_counts = defaultdict(int)
    number_pattern = re.compile(r"^\s*(\d+)")  # Matches the first number in each line

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    match = number_pattern.match(line)
                    if match:
                        number = int(match.group(1))
                        number_counts[number] += 1

    return number_counts

# Specify your folder path
folder_path = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/test/labels"

# Run the function
unique_counts = count_unique_first_numbers(folder_path)

# Print results
for number, count in sorted(unique_counts.items()):
    print(f"{number}: {count}")
