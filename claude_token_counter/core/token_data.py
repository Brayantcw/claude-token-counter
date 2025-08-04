"""
Token data management and processing.
"""

import json
from datetime import datetime, date, timedelta
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Claude API pricing (per 1M tokens) - 2025 rates
PRICING = {
    'claude-sonnet-4-20250514': {
        'input': 3.0,
        'output': 15.0,
        'cache_write': 3.75,
        'cache_read': 0.30
    },
    'claude-3-5-sonnet-20241022': {
        'input': 3.0,
        'output': 15.0,
        'cache_write': 3.75,
        'cache_read': 0.30
    },
    'claude-3-opus-20240229': {
        'input': 15.0,
        'output': 75.0,
        'cache_write': 18.75,
        'cache_read': 1.50
    }
}


class TokenData:
    """Class to handle token data operations"""
    
    def __init__(self):
        self.usage_data = []
        self.load_data()
    
    def find_claude_data_dir(self) -> Optional[Path]:
        """Find the Claude CLI data directory."""
        home = Path.home()
        claude_dir = home / '.claude' / 'projects'
        return claude_dir if claude_dir.exists() else None
    
    def parse_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse a JSONL file and extract token usage data."""
        usage_data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        # Extract usage data from assistant messages
                        if (data.get('type') == 'assistant' and 
                            'message' in data and 
                            'usage' in data['message']):
                            
                            usage = data['message']['usage']
                            model = data['message'].get('model', 'unknown')
                            timestamp = data.get('timestamp', '')
                            
                            usage_data.append({
                                'model': model,
                                'timestamp': timestamp,
                                'input_tokens': usage.get('input_tokens', 0),
                                'output_tokens': usage.get('output_tokens', 0),
                                'cache_creation_input_tokens': usage.get('cache_creation_input_tokens', 0),
                                'cache_read_input_tokens': usage.get('cache_read_input_tokens', 0),
                                'session_id': data.get('sessionId', ''),
                                'project_dir': Path(file_path).parent.name
                            })
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception:
            pass
        
        return usage_data
    
    def load_data(self) -> None:
        """Load all usage data from Claude CLI files."""
        claude_dir = self.find_claude_data_dir()
        if not claude_dir:
            return
        
        jsonl_files = list(claude_dir.glob('**/*.jsonl'))
        self.usage_data = []
        
        for file_path in jsonl_files:
            usage_data = self.parse_jsonl_file(file_path)
            self.usage_data.extend(usage_data)
    
    def calculate_cost(self, usage_entry: Dict[str, Any]) -> float:
        """Calculate cost for a single usage entry."""
        model = usage_entry['model']
        pricing = PRICING.get(model, PRICING['claude-sonnet-4-20250514'])
        
        input_cost = (usage_entry['input_tokens'] / 1_000_000) * pricing['input']
        output_cost = (usage_entry['output_tokens'] / 1_000_000) * pricing['output']
        cache_write_cost = (usage_entry['cache_creation_input_tokens'] / 1_000_000) * pricing['cache_write']
        cache_read_cost = (usage_entry['cache_read_input_tokens'] / 1_000_000) * pricing['cache_read']
        
        return input_cost + output_cost + cache_write_cost + cache_read_cost
    
    def get_local_datetime(self, timestamp_str: str) -> Optional[datetime]:
        """Convert UTC timestamp to local timezone."""
        try:
            # Parse UTC timestamp
            utc_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Convert to local timezone
            local_dt = utc_dt.astimezone()
            return local_dt
        except Exception:
            return None
    
    def get_summary_stats(self, filter_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Get summary statistics."""
        data = filter_data if filter_data is not None else self.usage_data
        
        if not data:
            return {
                'total_requests': 0,
                'total_input': 0,
                'total_output': 0,
                'total_cache_creation': 0,
                'total_cache_read': 0,
                'total_cost': 0.0,
                'models': {}
            }
        
        total_input = sum(entry['input_tokens'] for entry in data)
        total_output = sum(entry['output_tokens'] for entry in data)
        total_cache_creation = sum(entry['cache_creation_input_tokens'] for entry in data)
        total_cache_read = sum(entry['cache_read_input_tokens'] for entry in data)
        total_cost = sum(self.calculate_cost(entry) for entry in data)
        
        # Model breakdown
        models = defaultdict(lambda: {
            'requests': 0, 'input_tokens': 0, 'output_tokens': 0,
            'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'cost': 0
        })
        
        for entry in data:
            model = entry['model']
            models[model]['requests'] += 1
            models[model]['input_tokens'] += entry['input_tokens']
            models[model]['output_tokens'] += entry['output_tokens']
            models[model]['cache_creation_input_tokens'] += entry['cache_creation_input_tokens']
            models[model]['cache_read_input_tokens'] += entry['cache_read_input_tokens']
            models[model]['cost'] += self.calculate_cost(entry)
        
        return {
            'total_requests': len(data),
            'total_input': total_input,
            'total_output': total_output,
            'total_cache_creation': total_cache_creation,
            'total_cache_read': total_cache_read,
            'total_cost': total_cost,
            'models': dict(models)
        }
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity."""
        recent = sorted(self.usage_data, key=lambda x: x['timestamp'], reverse=True)[:limit]
        return recent
    
    def get_today_data(self) -> List[Dict[str, Any]]:
        """Get today's usage data."""
        today = date.today().isoformat()
        return [entry for entry in self.usage_data if entry['timestamp'].startswith(today)]
    
    def get_hourly_usage(self, hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Get usage data grouped by hour for the last N hours."""
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)
        
        hourly_data = {}
        
        for entry in self.usage_data:
            try:
                local_timestamp = self.get_local_datetime(entry['timestamp'])
                if local_timestamp and local_timestamp.replace(tzinfo=None) >= cutoff:
                    hour_key = local_timestamp.strftime('%H:00')
                    if hour_key not in hourly_data:
                        hourly_data[hour_key] = {'tokens': 0, 'cost': 0, 'requests': 0}
                    
                    total_tokens = (entry['input_tokens'] + entry['output_tokens'] + 
                                  entry['cache_creation_input_tokens'] + entry['cache_read_input_tokens'])
                    
                    hourly_data[hour_key]['tokens'] += total_tokens
                    hourly_data[hour_key]['cost'] += self.calculate_cost(entry)
                    hourly_data[hour_key]['requests'] += 1
            except Exception:
                continue
        
        return hourly_data
    
    def get_recent_trend(self, minutes: int = 60) -> List[int]:
        """Get recent usage trend for sparkline."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=minutes)
        
        # Create 10-minute buckets
        buckets = []
        for i in range(6):  # 6 buckets of 10 minutes each
            bucket_start = cutoff + timedelta(minutes=i*10)
            bucket_end = bucket_start + timedelta(minutes=10)
            bucket_tokens = 0
            
            for entry in self.usage_data:
                try:
                    local_timestamp = self.get_local_datetime(entry['timestamp'])
                    if local_timestamp:
                        local_naive = local_timestamp.replace(tzinfo=None)
                        if bucket_start <= local_naive < bucket_end:
                            total_tokens = (entry['input_tokens'] + entry['output_tokens'] + 
                                          entry['cache_creation_input_tokens'] + entry['cache_read_input_tokens'])
                            bucket_tokens += total_tokens
                except Exception:
                    continue
            
            buckets.append(bucket_tokens)
        
        return buckets
    
    def get_time_series_data(self, days: int = 7) -> Tuple[Dict[str, Dict[str, Any]], str]:
        """Get time series data for plotting."""
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        
        # Group data by day or hour depending on range
        if days <= 2:
            # Hourly data for short ranges
            time_format = '%Y-%m-%d %H:00'
        else:
            # Daily data for longer ranges
            time_format = '%Y-%m-%d'
        
        time_series = defaultdict(lambda: {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'cost': 0,
            'requests': 0
        })
        
        for entry in self.usage_data:
            try:
                local_timestamp = self.get_local_datetime(entry['timestamp'])
                if local_timestamp and local_timestamp.replace(tzinfo=None) >= cutoff:
                    if days <= 2:
                        # Round to nearest hour
                        time_key = local_timestamp.replace(minute=0, second=0, microsecond=0)
                    else:
                        # Round to day
                        time_key = local_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    time_str = time_key.strftime(time_format)
                    
                    time_series[time_str]['input_tokens'] += entry['input_tokens']
                    time_series[time_str]['output_tokens'] += entry['output_tokens']
                    time_series[time_str]['total_tokens'] += (
                        entry['input_tokens'] + entry['output_tokens'] +
                        entry['cache_creation_input_tokens'] + entry['cache_read_input_tokens']
                    )
                    time_series[time_str]['cost'] += self.calculate_cost(entry)
                    time_series[time_str]['requests'] += 1
                    
            except Exception:
                continue
        
        return dict(time_series), time_format