#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# Setup internal directory layers with explicit write permissions
export OLLAMA_MODELS="/tmp/ollama_models"
mkdir -p $OLLAMA_MODELS
mkdir -p ./ollama_env

echo "🐍 Installing python extraction bridges..."
pip install --quiet zstandard

echo "📥 Fetching official Ollama Linux archive stream..."
curl -L https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tar.zst -o ollama.tar.zst

echo "📦 Unpacking container layers using Python bridge..."
python3 -c "
import tarfile
import zstandard as zstd
with open('ollama.tar.zst', 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as reader:
        with tarfile.open(fileobj=reader, mode='r|') as tar:
            tar.extractall(path='./ollama_env')
"

# Bind the fresh unpacked binaries straight into execution space
export PATH=$PATH:$(pwd)/ollama_env/bin

echo "🚀 Starting Ollama background server process..."
./ollama_env/bin/ollama serve &

echo "⏳ Waiting for Ollama server to wake up..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 2
done

echo "🤖 Fetching model layer matrix (qwen2.5-coder:1.5b)..."
./ollama_env/bin/ollama pull qwen2.5-coder:1.5b

echo "🖥️ Launching Quantum Analytics UI Engine..."
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
