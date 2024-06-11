import os
import random
import string

def create_random_text(length=10):
    """Generate random text of a given length."""
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))

def create_random_file(file_path, file_size=10):
    """Create a random text file with specified size."""
    with open(file_path, 'w') as file:
        file.write(create_random_text(file_size))

def create_random_filesystem(base_dir, num_dirs=5, num_files_per_dir=5, file_size=10):
    """Create a randomized file system with directories and random text files."""
    os.makedirs(base_dir, exist_ok=True)
    
    for dir_num in range(num_dirs):
        dir_path = os.path.join(base_dir, f"dir_{dir_num}")
        os.makedirs(dir_path, exist_ok=True)
        
        for file_num in range(num_files_per_dir):
            file_path = os.path.join(dir_path, f"file_{file_num}.txt")
            create_random_file(file_path, file_size)


def generate_random_id(length=10):
    """Generate a random id of a given length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# Usage
base_directory = 'random_filesystem'
num_directories = 3
num_files_per_directory = 4
file_size_in_chars = 20

create_random_filesystem(base_directory, num_directories, num_files_per_directory, file_size_in_chars)

print(f"Randomized file system created at: {os.path.abspath(base_directory)}")
