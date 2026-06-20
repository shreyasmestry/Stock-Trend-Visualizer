#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# Define a writeable models directory inside the container's scratch space
export OLLAMA_MODELS="/tmp/ollama_models"
mkdir -p $OLLAMA_MODELS

echo "📥 Downloading the raw pre-compiled Ollama binary from GitHub releases..."
# Pulling the direct, official static compiled Linux binary
curl -L https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64 -o ollama

echo "🔑 Giving executable permissions to the binary..."
chmod +x ollama

echo "🚀 Starting Ollama background server process..."
./ollama serve &

# Wait for the Ollama background process to listen on port 11434
echo "⏳ Waiting for Ollama server to wake up..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 2
done

echo "🤖 Fetching model layer matrix (qwen2.5-coder:1.5b)..."
./ollama pull qwen2.5-coder:1.5b

echo "🖥️ Launching Quantum Analytics UI Engine..."
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
