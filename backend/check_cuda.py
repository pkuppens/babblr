#!/usr/bin/env python3
"""Diagnostic script to check CUDA/GPU availability for Whisper.

Run this script to diagnose why CUDA might not be available.
"""

import logging
import os
import platform
import subprocess
import sys

# Configure logging for standalone script output
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run CUDA/GPU checks to diagnose Whisper performance issues.

    This script logs diagnostic information about the current Python
    environment, PyTorch installation, NVIDIA driver availability, and
    basic system details. It also logs recommended next steps when GPU
    acceleration is not available.
    """
    logger.info("=" * 60)
    logger.info("CUDA/GPU Diagnostic for Whisper")
    logger.info("=" * 60)
    logger.info("")

    # Check 0: Environment info
    logger.info("0. Checking Python environment...")
    logger.info(f"   Python executable: {sys.executable}")
    if "VIRTUAL_ENV" in os.environ:
        logger.info(f"   Virtual environment: {os.environ['VIRTUAL_ENV']}")
    else:
        logger.info("   Virtual environment: Not activated (using system Python)")
    logger.info(f"   Working directory: {os.getcwd()}")
    logger.info("")

    # Check 1: PyTorch installation
    logger.info("1. Checking PyTorch installation...")
    try:
        import torch

        logger.info(f"   [OK] PyTorch version: {torch.__version__}")
        logger.info(f"   PyTorch location: {torch.__file__}")

        # Check if CUDA is available in PyTorch
        logger.info(f"   CUDA available in PyTorch: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            logger.info(f"   [OK] CUDA version: {torch.version.cuda}")
            logger.info(f"   [OK] GPU device: {torch.cuda.get_device_name(0)}")
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"   [OK] VRAM: {vram_gb:.1f} GB")
        else:
            logger.info("   [ERROR] CUDA not available in PyTorch")
            logger.info("")
            logger.info("   This usually means:")
            logger.info("   - PyTorch was installed without CUDA support (CPU-only version)")
            logger.info("   - OR NVIDIA drivers are not installed")
            logger.info("")

            # Check if it's CPU-only PyTorch
            if "+cpu" in torch.__version__:
                logger.info("   [INFO] Detected: CPU-only PyTorch installation")
                logger.info(
                    "   [INFO] Solution: Install CUDA-enabled PyTorch (see instructions below)"
                )
            else:
                logger.info("   [INFO] PyTorch version doesn't indicate CPU-only")
                logger.info("   [INFO] Check if NVIDIA drivers are installed")

    except ImportError:
        logger.info("   [ERROR] PyTorch not installed")
        logger.info("   [INFO] Install PyTorch first: uv pip install torch")

    logger.info("")

    # Check 2: NVIDIA drivers (Windows)
    logger.info("2. Checking NVIDIA drivers (Windows)...")
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("   [OK] NVIDIA drivers detected")
            logger.info("   Output:")
            for line in result.stdout.split("\n")[:5]:
                if line.strip():
                    logger.info(f"   {line}")
        else:
            logger.info("   [WARNING] nvidia-smi command failed")
            logger.info("   This might mean:")
            logger.info("   - NVIDIA drivers not installed")
            logger.info("   - GPU not available")
    except FileNotFoundError:
        logger.info("   [WARNING] nvidia-smi not found")
        logger.info("   This usually means NVIDIA drivers are not installed")
    except subprocess.TimeoutExpired:
        logger.info("   [WARNING] nvidia-smi timed out")
    except Exception as e:
        logger.info(f"   [WARNING] Error checking drivers: {e}")

    logger.info("")

    # Check 3: System info
    logger.info("3. System information...")
    logger.info(f"   OS: {platform.system()} {platform.release()}")
    logger.info(f"   Architecture: {platform.machine()}")

    logger.info("")
    logger.info("=" * 60)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 60)
    logger.info("")

    try:
        import torch

        if not torch.cuda.is_available():
            logger.info("To enable GPU support:")
            logger.info("")
            logger.info("1. First, verify NVIDIA drivers are installed:")
            logger.info("   - Windows: Check Device Manager > Display adapters")
            logger.info("   - Or run: nvidia-smi (if installed)")
            logger.info("")
            logger.info("2. Install CUDA-enabled PyTorch using uv (recommended):")
            logger.info("")
            logger.info("   For CUDA 12.1 (recommended for CUDA 13.0 drivers):")
            logger.info("   cd backend")
            logger.info("   uv pip uninstall torch torchvision torchaudio")
            logger.info(
                "   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            )
            logger.info("")
            logger.info("   For CUDA 11.8 (fallback for older systems):")
            logger.info("   cd backend")
            logger.info("   uv pip uninstall torch torchvision torchaudio")
            logger.info(
                "   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
            )
            logger.info("")
            logger.info(
                "   Note: Check https://pytorch.org/get-started/locally/ for latest CUDA versions"
            )
            logger.info("")
            logger.info("3. Restart your backend and check again")
            logger.info("")
            logger.info(
                "Note: If you're not using uv, replace 'uv pip' with 'pip' in the commands above"
            )
    except ImportError:
        logger.info("Install PyTorch first, then run this script again")

    logger.info("")


if __name__ == "__main__":
    main()
