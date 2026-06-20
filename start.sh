#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

echo "📥 Downloading pre-compiled Ollama binary directly..."
# Download the direct Linux build archive
curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama.tgz

echo "📦 Extracting Ollama binary locally..."
# Extract it directly into our workspace directory
tar -xzf ollama.tgz

# Add current workspace to the PATH environment variable so the system finds 'ollama'
export PATH=$PATH:$(pwd)/bin:$(pwd)

echo "🚀 Starting Ollama background server process..."
# Run the binary we just extracted in the background
./bin/ollama serve &

# Wait for the Ollama background process to listen on port 11434
echo "⏳ Waiting for Ollama server to wake up..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 2
done

echo "🤖 Fetching model layer matrix (qwen2.5-coder:1.5b)..."
./bin/ollama pull qwen2.5-coder:1.5b

echo "🖥️ Launching Quantum Analytics UI Engine..."
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
