#!/usr/bin/env bash
set -euo pipefail

echo "== Virgo-Eye: Ollama setup =="

# Install Ollama if missing
if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Pulling Qwen2-VL 7B..."
ollama pull qwen2-vl:7b

echo "Pulling LLaVA fallback..."
ollama pull llava:7b || true

echo "Creating Virgo Modelfile..."
( cd "$(dirname "$0")/.." && ollama create virgo-qwen2-vl -f models/Modelfile )

echo "Verifying..."
ollama list
echo "Done. Set VIRGO_MODEL=virgo-qwen2-vl in backend/.env and run the API."