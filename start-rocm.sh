#!/usr/bin/env bash

# Get project root directory
PROJECT_ROOT=$(pwd)

# Set environment variables
export USE_GPU=true
export USE_ONNX=false
export PYTHONPATH=$PROJECT_ROOT:$PROJECT_ROOT/api
export MODEL_DIR=$PROJECT_ROOT/api/src/models
export VOICES_DIR=$PROJECT_ROOT/api/src/voices/v1_0
export WEB_PLAYER_PATH=$PROJECT_ROOT/web
export DEVICE="cuda" # PyTorch ROCm uses "cuda" device name

# ROCm / AMD GPU Fixes
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export ROCM_PATH=/opt/rocm-7.2.0
export HIP_PATH=/opt/rocm-7.2.0
export PATH=$ROCM_PATH/bin:$PATH
export CplusIncludePath=$ROCM_PATH/include:$CplusIncludePath
export C_INCLUDE_PATH=$ROCM_PATH/include:$C_INCLUDE_PATH

echo "🚀 Starting FastKoko with ROCm (AMD GPU) support..."

# Force ROCm 7.2 dependencies
echo "📦 Forcing ROCm 7.2 stack..."
uv pip install torch==2.11.0+rocm7.2 --index-url https://download.pytorch.org/whl/rocm7.2

# Set library path after install
TORCH_LIB=$($PROJECT_ROOT/.venv/bin/python -c "import torch, os; print(os.path.join(os.path.dirname(torch.__file__), 'lib'))")
export LD_LIBRARY_PATH=$TORCH_LIB:$LD_LIBRARY_PATH

# Verify ROCm status
echo "🔍 Verifying ROCm status..."
$PROJECT_ROOT/.venv/bin/python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'ROCm available: {torch.cuda.is_available()}'); print(f'ROCm version: {getattr(torch.version, \"hip\", \"N/A\")}'); print(f'Device Count: {torch.cuda.device_count()}')"

# Start the server
echo "🔥 Launching FastAPI server..."
$PROJECT_ROOT/.venv/bin/python -m uvicorn api.src.main:app --host 0.0.0.0 --port 8880
