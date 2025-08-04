#!/bin/bash
# Claude Token Counter Installation Script for Mac/Linux

set -e

echo "🚀 Installing Claude Token Counter..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Install using pip
echo "📦 Installing claude-token-counter..."

if command -v pipx &> /dev/null; then
    echo "🔧 Using pipx for isolated installation..."
    pipx install .
elif python3 -m pip --version &> /dev/null; then
    echo "🔧 Using pip for installation..."
    python3 -m pip install --user .
else
    echo "❌ Neither pipx nor pip found. Please install pip."
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Usage:"
echo "  claude-tokens          # CLI version"
echo "  claude-tokens-tui      # Terminal UI version"
echo ""
echo "To get started:"
echo "  claude-tokens-tui"
echo ""
echo "📖 For more information, visit: https://github.com/yourusername/claude-token-counter"