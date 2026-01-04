#!/usr/bin/env python3
"""Diagnostic script to check CUDA/GPU availability for Whisper.

Run this script to diagnose why CUDA might not be available.
"""

import os
import platform
import subprocess
import sys


def main() -> None:
    """Run CUDA/GPU checks to diagnose Whisper performance issues.

    This script prints diagnostic information about the current Python
    environment, PyTorch installation, NVIDIA driver availability, and
    basic system details. It also prints recommended next steps when GPU
    acceleration is not available.
    """
    print("=" * 60)
    print("CUDA/GPU Diagnostic for Whisper")
    print("=" * 60)
    print()

    # Check 0: Environment info
    print("0. Checking Python environment...")
    print(f"   Python executable: {sys.executable}")
    if "VIRTUAL_ENV" in os.environ:
        print(f"   Virtual environment: {os.environ['VIRTUAL_ENV']}")
    else:
        print("   Virtual environment: Not activated (using system Python)")
    print(f"   Working directory: {os.getcwd()}")
    print()

    # Check 1: PyTorch installation
    print("1. Checking PyTorch installation...")
    try:
        import torch

        print(f"   ✅ PyTorch version: {torch.__version__}")
        print(f"   PyTorch location: {torch.__file__}")

        # Check if CUDA is available in PyTorch
        print(f"   CUDA available in PyTorch: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"   ✅ CUDA version: {torch.version.cuda}")
            print(f"   ✅ GPU device: {torch.cuda.get_device_name(0)}")
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"   ✅ VRAM: {vram_gb:.1f} GB")
        else:
            print("   ❌ CUDA not available in PyTorch")
            print()
            print("   This usually means:")
            print("   - PyTorch was installed without CUDA support (CPU-only version)")
            print("   - OR NVIDIA drivers are not installed")
            print()

            # Check if it's CPU-only PyTorch
            if "+cpu" in torch.__version__:
                print("   🔍 Detected: CPU-only PyTorch installation")
                print("   💡 Solution: Install CUDA-enabled PyTorch (see instructions below)")
            else:
                print("   🔍 PyTorch version doesn't indicate CPU-only")
                print("   💡 Check if NVIDIA drivers are installed")

    except ImportError:
        print("   ❌ PyTorch not installed")
        print("   💡 Install PyTorch first: uv pip install torch")

    print()

    # Check 2: NVIDIA drivers (Windows)
    print("2. Checking NVIDIA drivers (Windows)...")
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ NVIDIA drivers detected")
            print("   Output:")
            for line in result.stdout.split("\n")[:5]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("   ⚠️  nvidia-smi command failed")
            print("   This might mean:")
            print("   - NVIDIA drivers not installed")
            print("   - GPU not available")
    except FileNotFoundError:
        print("   ⚠️  nvidia-smi not found")
        print("   This usually means NVIDIA drivers are not installed")
    except subprocess.TimeoutExpired:
        print("   ⚠️  nvidia-smi timed out")
    except Exception as e:
        print(f"   ⚠️  Error checking drivers: {e}")

    print()

    # Check 3: System info
    print("3. System information...")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")

    print()
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print()

    try:
        import torch

        if not torch.cuda.is_available():
            print("To enable GPU support:")
            print()
            print("1. First, verify NVIDIA drivers are installed:")
            print("   - Windows: Check Device Manager > Display adapters")
            print("   - Or run: nvidia-smi (if installed)")
            print()
            print("2. Install CUDA-enabled PyTorch using uv (recommended):")
            print()
            print("   For CUDA 12.1 (recommended for CUDA 13.0 drivers):")
            print("   cd backend")
            print("   uv pip uninstall torch torchvision torchaudio")
            print(
                "   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            )
            print()
            print("   For CUDA 11.8 (fallback for older systems):")
            print("   cd backend")
            print("   uv pip uninstall torch torchvision torchaudio")
            print(
                "   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
            )
            print()
            print(
                "   Note: Check https://pytorch.org/get-started/locally/ for latest CUDA versions"
            )
            print()
            print("3. Restart your backend and check again")
            print()
            print("Note: If you're not using uv, replace 'uv pip' with 'pip' in the commands above")
    except ImportError:
        print("Install PyTorch first, then run this script again")

    print()


if __name__ == "__main__":
    main()
