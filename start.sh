#!/usr/bin/env bash
set -e
echo "🖥️ Launching Quantum Analytics UI Engine..."
streamlit run stv.py --server.port $PORT --server.address 0.0.0.0
