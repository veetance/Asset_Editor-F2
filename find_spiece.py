import os

def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None

path = find_file('spiece.model', 'C:\\MAIN-COMFY')
print(f"FOUND: {path}")
