#!/bin/bash
# Podcastfy setup script

echo "🔧 Updating system..."
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg

echo "🐍 Creating virtual environment..."
python3.11 -m venv .venv
source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Podcastfy environment setup complete."
echo "To activate later: source .venv/bin/activate"

