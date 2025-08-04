# Claude CLI Token Counter

A comprehensive Python application to track token usage and costs from Claude CLI sessions with real-time monitoring capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

### **Command Line Interface** (`claude-tokens`)
- All-time usage summary
- Today's usage filtering (`--today`)
- Session-specific filtering (`--session ID`)
- Project-specific filtering (`--project NAME`)
- Detailed cost calculations with cache optimization tracking

### **Terminal UI Interface** (`claude-tokens --ui`)
- **Real-time Live Monitor** - Auto-refreshing dashboard with live status
- **Time Series Analytics** - Interactive graphs showing usage trends over time
- Clean professional interface
- Interactive navigation with multiple tabs
- Detailed breakdowns by model and time periods
- Recent activity tracking with timestamps
- Cache savings calculations and optimization insights
- Hourly usage analytics for the past 12 hours

## Quick Installation

### **Install from Source** (Recommended)
```bash
# Clone the repository
git clone https://github.com/Brayantcw/claude-token-counter.git
cd claude-token-counter

# Install the package
pip install .
```

### **Development Install**
```bash
# Clone and install in development mode
git clone https://github.com/Brayantcw/claude-token-counter.git
cd claude-token-counter
pip install -e .
```

### **One-line Install Script**
```bash
# Download and run install script
curl -sSL https://raw.githubusercontent.com/Brayantcw/claude-token-counter/main/install.sh | bash
```

## Usage

### Command Line Interface
```bash
# Basic usage - show all usage
claude-tokens

# Today's usage only  
claude-tokens --today

# Specific session
claude-tokens --session SESSION_ID

# Help
claude-tokens --help
```

### Terminal UI Interface
```bash
# Launch the interactive terminal UI (recommended)
claude-tokens --ui
```

**TUI Controls:**
- `Tab` / Arrow keys: Navigate between tabs
- `r`: Refresh data manually
- `q`: Quit
- **Live Monitor Tab**: Auto-refreshes every 10 seconds (can pause/resume)

## Data Source

The tool reads Claude CLI session data from `~/.claude/projects/` directory, parsing JSONL files to extract:
- Input/output token usage
- Cache creation and read tokens
- Model information
- Timestamps and session IDs

## Cost Calculation

Uses 2025 Claude API pricing:
- **Sonnet 4**: $3.00/$15.00 (input/output), $3.75/$0.30 (cache write/read) per 1M tokens
- **Sonnet 3.5**: $3.00/$15.00 (input/output), $3.75/$0.30 (cache write/read) per 1M tokens  
- **Opus**: $15.00/$75.00 (input/output), $18.75/$1.50 (cache write/read) per 1M tokens

## Real-time Monitoring

The **Live Monitor** tab provides:
- **Activity Status**: Shows current session state and time since last activity
- **Hourly Analytics**: Detailed breakdown of usage patterns by hour
- **Auto-refresh**: Updates every 10 seconds with pause/resume controls
- **Today's Totals**: Running counters for current day usage

## Time Series Analytics

The **Analytics** tab features interactive time series graphs with:
- **Multiple Time Ranges**: 24 hours, 2 days, 7 days, or 30 days
- **Different Metrics**: Toggle between tokens, cost, and request counts
- **Visual Trends**: Plotext-powered terminal graphs showing clear patterns
- **Period Summaries**: Statistics for the selected time range
- **Interactive Controls**: Easy switching between views with button controls

## Cache Savings

The tool highlights significant savings from Claude's prompt caching:
- Cache reads cost 90% less than regular input tokens
- Tracks both cache creation costs and read savings
- Shows total savings achieved through caching
- Real-time cache efficiency monitoring

## Requirements

- **Python 3.8+**
- **Claude CLI** (must be used at least once to generate data)
- **Terminal** with color support (for best TUI experience)

## Supported Platforms

- **macOS** 10.15+
- **Linux** (Ubuntu 18.04+, CentOS 7+, etc.)
- **Windows** (via WSL)

## Screenshots

### Terminal UI (TUI)
The beautiful terminal interface shows real-time monitoring, analytics graphs, and detailed breakdowns.

### Command Line Interface (CLI)
Clean, scriptable output perfect for automation and quick checks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Project Structure

```
claude-token-counter/
├── claude_token_counter/          # Main package
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   └── token_data.py         # Token data management
│   ├── ui/                       # User interfaces
│   │   ├── __init__.py
│   │   ├── cli.py               # Command line interface
│   │   ├── tui.py               # Terminal UI main app
│   │   └── components.py        # TUI components
│   ├── utils/                    # Utility functions
│   │   └── __init__.py
│   └── __init__.py
├── pyproject.toml               # Package configuration
├── install.sh                   # Installation script
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for creating Claude and the CLI
- [Textual](https://github.com/Textualize/textual) for the amazing TUI framework
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting