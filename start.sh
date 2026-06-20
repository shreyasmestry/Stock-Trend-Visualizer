#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

echo "📥 Installing Ollama binary locally..."
curl -fsSL https://ollama.com/install.sh | sh

echo "🚀 Starting Ollama background server process..."
ollama serve &

# Wait for the Ollama background process to listen on port 11434
echo "⏳ Waiting for Ollama server to wake up..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 2
done

echo "🤖 Fetching model layer matrix (qwen2.5-coder:1.5b)..."
ollama pull qwen2.5-coder:1.5b

echo "🖥️ Launching Quantum Analytics UI Engine..."
# Automatically binds to the port Render provides dynamically
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
