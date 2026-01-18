import os

def find_transformer_config(path):
    for root, dirs, files in os.walk(path):
        if 'config.json' in files:
            full_path = os.path.join(root, 'config.json')
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    if 'FluxTransformer2DModel' in content:
                        print(f"FOUND: {full_path}")
            except:
                pass

find_transformer_config('C:\\MAIN-COMFY')
