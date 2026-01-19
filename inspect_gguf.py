"""
Inspect GGUF file metadata to extract model config.
"""
import struct

GGUF_PATH = r"d:\FLUX-2-KLIEN\models\flux-klein\flux-2-klein-9b-Q8_0.gguf"

def read_gguf_header(path):
    """Read GGUF file header and metadata."""
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != b'GGUF':
            print("Not a valid GGUF file!")
            return
        
        version = struct.unpack('<I', f.read(4))[0]
        tensor_count = struct.unpack('<Q', f.read(8))[0]
        metadata_kv_count = struct.unpack('<Q', f.read(8))[0]
        
        print(f"GGUF Version: {version}")
        print(f"Tensor count: {tensor_count}")
        print(f"Metadata entries: {metadata_kv_count}")
        print("-" * 50)
        
        for i in range(min(metadata_kv_count, 100)):
            try:
                key_len = struct.unpack('<Q', f.read(8))[0]
                key = f.read(key_len).decode('utf-8')
                value_type = struct.unpack('<I', f.read(4))[0]
                
                if value_type == 4:  # UINT32
                    value = struct.unpack('<I', f.read(4))[0]
                elif value_type == 5:  # INT32
                    value = struct.unpack('<i', f.read(4))[0]
                elif value_type == 6:  # FLOAT32
                    value = struct.unpack('<f', f.read(4))[0]
                elif value_type == 7:  # BOOL
                    value = struct.unpack('<?', f.read(1))[0]
                elif value_type == 8:  # STRING
                    str_len = struct.unpack('<Q', f.read(8))[0]
                    value = f.read(str_len).decode('utf-8')
                elif value_type == 10:  # UINT64
                    value = struct.unpack('<Q', f.read(8))[0]
                else:
                    print(f"{key}: <unknown type {value_type}>")
                    continue
                
                print(f"{key}: {value}")
            except Exception as e:
                print(f"Error at entry {i}: {e}")
                break

if __name__ == "__main__":
    read_gguf_header(GGUF_PATH)
