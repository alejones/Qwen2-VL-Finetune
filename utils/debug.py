# /home/app/debug_gpu.py
"""
Debug script to check GPU availability and CUDA setup
"""

import torch
import os
import subprocess

def main():
    print("=== GPU Debug Information ===")
    
    # Basic CUDA info
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"PyTorch version: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"GPU count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GB")
    
    # Environment variables
    print("\n=== Environment Variables ===")
    cuda_vars = [k for k in os.environ.keys() if 'CUDA' in k]
    for var in cuda_vars:
        print(f"{var}: {os.environ[var]}")
    
    # Test basic GPU operations
    print("\n=== GPU Operations Test ===")
    try:
        if torch.cuda.is_available():
            # Test tensor creation
            x = torch.randn(100, 100).cuda()
            print("✓ GPU tensor creation successful")
            
            # Test basic operation
            y = x @ x.T
            print("✓ GPU matrix multiplication successful")
            
            # Test memory pinning
            cpu_tensor = torch.randn(100, 100)
            pinned_tensor = cpu_tensor.pin_memory()
            print("✓ Memory pinning successful")
            
            # Test moving to GPU
            gpu_tensor = pinned_tensor.cuda()
            print("✓ CPU to GPU transfer successful")
            
        else:
            print("✗ CUDA not available")
    except Exception as e:
        print(f"✗ GPU test failed: {e}")
    
    # Check nvidia-smi
    print("\n=== nvidia-smi output ===")
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"nvidia-smi failed: {result.stderr}")
    except Exception as e:
        print(f"nvidia-smi error: {e}")

if __name__ == "__main__":
    main()