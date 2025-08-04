#!/usr/bin/env python3
"""
Claude CLI Token Counter - Command Line Interface

A simple Python program to track token usage and costs from Claude CLI sessions.
Reads JSONL files from ~/.claude/projects/ and calculates token usage and costs.
"""

import argparse
from datetime import date
from collections import defaultdict
from pathlib import Path

from ..core.token_data import TokenData


def format_timestamp(timestamp_str: str) -> str:
    """Convert ISO timestamp to readable local date."""
    try:
        from datetime import datetime
        # Parse UTC timestamp and convert to local timezone
        utc_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        local_dt = utc_dt.astimezone()
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str


def print_summary(usage_data, title="Token Usage Summary"):
    """Print a formatted summary of token usage and costs."""
    if not usage_data:
        print(f"\n{title}")
        print("No usage data found.")
        return
    
    token_data = TokenData()
    
    # Calculate totals
    total_input = sum(entry['input_tokens'] for entry in usage_data)
    total_output = sum(entry['output_tokens'] for entry in usage_data)
    total_cache_creation = sum(entry['cache_creation_input_tokens'] for entry in usage_data)
    total_cache_read = sum(entry['cache_read_input_tokens'] for entry in usage_data)
    
    total_cost = sum(token_data.calculate_cost(entry) for entry in usage_data)
    
    # Model breakdown
    model_stats = defaultdict(lambda: {
        'input_tokens': 0, 'output_tokens': 0, 
        'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 
        'requests': 0, 'cost': 0
    })
    
    for entry in usage_data:
        model = entry['model']
        model_stats[model]['input_tokens'] += entry['input_tokens']
        model_stats[model]['output_tokens'] += entry['output_tokens']
        model_stats[model]['cache_creation_input_tokens'] += entry['cache_creation_input_tokens']
        model_stats[model]['cache_read_input_tokens'] += entry['cache_read_input_tokens']
        model_stats[model]['requests'] += 1
        model_stats[model]['cost'] += token_data.calculate_cost(entry)
    
    print(f"\n{title}")
    print("=" * 60)
    print(f"Total Requests: {len(usage_data)}")
    print(f"Input Tokens: {total_input:,}")
    print(f"Output Tokens: {total_output:,}")
    print(f"Cache Creation Tokens: {total_cache_creation:,}")
    print(f"Cache Read Tokens: {total_cache_read:,}")
    print(f"Total Tokens: {total_input + total_output + total_cache_creation + total_cache_read:,}")
    print(f"Total Cost: ${total_cost:.4f}")
    
    print(f"\nModel Breakdown:")
    print("-" * 60)
    for model, stats in model_stats.items():
        total_tokens = stats['input_tokens'] + stats['output_tokens'] + stats['cache_creation_input_tokens'] + stats['cache_read_input_tokens']
        print(f"{model}:")
        print(f"   Requests: {stats['requests']}")
        print(f"   Tokens: {total_tokens:,} (In: {stats['input_tokens']:,}, Out: {stats['output_tokens']:,})")
        print(f"   Cache: {stats['cache_creation_input_tokens']:,} writes, {stats['cache_read_input_tokens']:,} reads")
        print(f"   Cost: ${stats['cost']:.4f}")
        print()


def main():
    """Main function to run the token counter."""
    parser = argparse.ArgumentParser(description='Count Claude CLI token usage and costs')
    parser.add_argument('--ui', action='store_true', help='Launch terminal UI interface')
    parser.add_argument('--today', action='store_true', help='Show only today\'s usage')
    parser.add_argument('--session', help='Show usage for specific session ID')
    parser.add_argument('--project', help='Show usage for specific project directory')
    args = parser.parse_args()
    
    # Launch TUI if --ui flag is provided
    if args.ui:
        from .tui import main as tui_main
        tui_main()
        return
    
    print("Claude CLI Token Counter")
    print("=" * 40)
    
    # Initialize token data
    token_data = TokenData()
    
    # Find Claude data directory
    claude_dir = token_data.find_claude_data_dir()
    if not claude_dir:
        print("Claude data directory not found")
        print("Make sure you have used Claude CLI at least once.")
        return
    
    print(f"Scanning: {claude_dir}")
    
    # Find all JSONL files
    jsonl_files = list(claude_dir.glob('**/*.jsonl'))
    
    if not jsonl_files:
        print("No JSONL files found in Claude data directory.")
        return
    
    print(f"Found {len(jsonl_files)} session files")
    
    if not token_data.usage_data:
        print("No usage data found in session files.")
        return
    
    # Filter data based on arguments
    filtered_data = token_data.usage_data
    title = "All Time Token Usage Summary"
    
    if args.today:
        filtered_data = token_data.get_today_data()
        title = "Today's Token Usage Summary"
    
    if args.session:
        filtered_data = [entry for entry in filtered_data 
                        if entry['session_id'] == args.session]
        title = f"Session {args.session} Usage Summary"
    
    if args.project:
        filtered_data = [entry for entry in filtered_data 
                        if entry['project_dir'] == args.project]
        title = f"Project '{args.project}' Usage Summary"
    
    # Print summary
    print_summary(filtered_data, title)
    
    # Show recent activity
    if not args.session and not args.project:
        recent_data = token_data.get_recent_activity(5)
        
        if recent_data:
            print(f"\nRecent Activity:")
            print("-" * 60)
            for entry in recent_data:
                timestamp = format_timestamp(entry['timestamp'])
                cost = token_data.calculate_cost(entry)
                total_tokens = entry['input_tokens'] + entry['output_tokens'] + entry['cache_creation_input_tokens'] + entry['cache_read_input_tokens']
                print(f"{timestamp} | {entry['model'][:20]} | {total_tokens:,} tokens | ${cost:.4f}")


if __name__ == '__main__':
    main()