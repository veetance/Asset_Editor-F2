import os

def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.join(root, name)

for p in find_file('spiece.model', 'C:\\MAIN-COMFY'):
    print(f"FOUND: |{p}|")
