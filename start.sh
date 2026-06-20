#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# Define a writeable models directory inside the container's scratch space
export OLLAMA_MODELS="/tmp/ollama_models"
mkdir -p $OLLAMA_MODELS

echo "📥 Downloading pre-compiled Ollama binary archive directly..."
# Download the direct Linux build archive (.tar.zst)
curl -L https://ollama.com/download/ollama-linux-amd64.tar.zst -o ollama.tar.zst

echo "📦 Extracting Ollama archive layers locally..."
# Extract using tar (modern tar handles .zst automatically if zstd is present, or we can unpack the binary stream)
mkdir -p ./ollama_env
tar -xf ollama.tar.zst -C ./ollama_env

# Add extracted binaries to our executable lookup environment PATH
export PATH=$PATH:$(pwd)/ollama_env/bin:$(pwd)/ollama_env/lib/ollama

echo "🚀 Starting Ollama background server process..."
./ollama_env/bin/ollama serve &

# Wait for the Ollama background process to listen on port 11434
echo "⏳ Waiting for Ollama server to wake up..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 2
done

echo "🤖 Fetching model layer matrix (qwen2.5-coder:1.5b)..."
./ollama_env/bin/ollama pull qwen2.5-coder:1.5b

echo "🖥️ Launching Quantum Analytics UI Engine..."
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
