import os
path = r'C:\MAIN-COMFY\ComfyUI\custom_nodes\ComfyUI-WanVideoWrapper\configs\T5_tokenizer'
if os.path.exists(path):
    print(os.listdir(path))
else:
    print("NO")
