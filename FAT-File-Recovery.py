import struct
import os

# Define constants based on FAT16 filesystem specifications
BPB_BytsPerSec = 512  # Bytes per sector
BPB_SecPerClus = 4    # Sectors per cluster
BPB_RsvdSecCnt = 1    # Reserved sectors count
BPB_NumFATs = 2       # Number of FATs
BPB_FATSz16 = 115     # FAT size (in sectors)
BPB_RootEntCnt = 512  # Root directory entries count

# Calculate FAT size, root directory start, and root directory size based on given constants
FAT_SIZE = BPB_FATSz16 * BPB_BytsPerSec
ROOT_DIR_START = BPB_FATSz16 * BPB_BytsPerSec * BPB_NumFATs
ROOT_DIR_SIZE = 32 * BPB_RootEntCnt
CLUSTER_SIZE = BPB_BytsPerSec * BPB_SecPerClus  # Calculate cluster size
EOF_MARKER = 0xFFFF  # End-of-file marker for FAT16

# Function to parse the FAT from the given image file
def parse_fat(file_path):
    with open(file_path, 'rb') as f:
        # Read the FAT data based on FAT_SIZE
        fat_data = f.read(FAT_SIZE)
        # Split the data into 16-bit entries
        fat_entries = [fat_data[i:i+2] for i in range(0, len(fat_data), 2)]
        # Convert each 16-bit entry into an integer
        fat_values = [struct.unpack('<H', entry)[0] for entry in fat_entries]
        # Return the list of FAT values
        return fat_values

# Function to save FAT values to a file
def save_to_file(output_path, fat_values):
    with open(output_path, 'w') as out_file:
        for value in fat_values:
            out_file.write(f"{value}\n")

# Function to identify start and end of contiguous chains in FAT
def identify_chains(fat_values):
    beginnings = []
    endings = []
    # Loop through FAT values starting from the second entry
    for i in range(1, len(fat_values)):
        # Identify the start of a chain
        if fat_values[i-1] != i:
            beginnings.append(i)
        # Identify the end of a chain
        if fat_values[i] != i+1:
            endings.append(i)
    return beginnings, endings

# Function to identify FAT entries that mark the start of a file
def identify_file_starts(beginnings, endings, fat_values):
    file_starts = []
    # Loop through each beginning of a chain
    for beginning in beginnings:
        file_start = True
        # Loop through each ending of a chain
        for ending in endings:
            # Check if an ending points to the current beginning
            if fat_values[ending] == beginning:
                file_start = False
                break
        if file_start:
            file_starts.append(beginning)
    return file_starts

# Function to extract files based on FAT values and starting locations
def extract_files_from_clusters(image_path, fat_values, file_start_locations, output_dir):
    with open(image_path, 'rb') as f:
        for start in file_start_locations:
            # Generate a unique filename for each file
            output_file_path = os.path.join(output_dir, f"recovered_file_{start}.dat")
            with open(output_file_path, 'wb') as out_file:
                current_cluster = start
                # Loop until EOF marker or end of FAT
                while current_cluster < len(fat_values) and fat_values[current_cluster] != EOF_MARKER:
                    # Calculate the byte offset for the current cluster
                    offset = (current_cluster - 2) * CLUSTER_SIZE + ROOT_DIR_START + ROOT_DIR_SIZE
                    f.seek(offset)
                    # Read data from the cluster and write to the output file
                    data = f.read(CLUSTER_SIZE)
                    out_file.write(data)
                    # Move to the next cluster in the chain
                    current_cluster = fat_values[current_cluster]
            # Remove trailing null bytes from the extracted file
            with open(output_file_path, 'rb+') as out_file:
                if out_file.tell() > 0:  # If file is not empty
                    out_file.seek(-1, os.SEEK_END)
                    while out_file.read(1) == b'\x00':
                        out_file.seek(-1, os.SEEK_CUR)
                        out_file.truncate()

# Main script execution
image_path = "C:\\Users\\lukep\\OneDrive\\Documents\\Digital_Forensics\\exam-1.image\\exam-1.image\\exam.image"
output_path = "C:\\Users\\lukep\\OneDrive\\Documents\\Digital_Forensics\\FAT_output.txt"
output_directory = "C:\\Users\\lukep\\OneDrive\\Documents\\Digital_Forensics\\Recovered_Files"

# Parse FAT values from the image
fat_values = parse_fat(image_path)
# Identify starts and ends of chains
beginnings, endings = identify_chains(fat_values)
# Identify FAT entries that mark the start of files
file_start_locations = identify_file_starts(beginnings, endings, fat_values)
# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
# Extract files using the identified starting locations
extract_files_from_clusters(image_path, fat_values, file_start_locations, output_directory)

# Print identified locations for debugging
print(f"File start locations: {file_start_locations}")
print(f"Beginnings of chains: {beginnings}")
print(f"Endings of chains: {endings}")
