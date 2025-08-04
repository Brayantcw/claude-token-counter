"""
TUI Components for Claude Token Counter
"""

from datetime import datetime
from textual.widgets import Static, DataTable, Button
from textual.containers import Horizontal, VerticalScroll
from textual.app import ComposeResult
from ..core.token_data import TokenData


class GraphGenerator:
    """Generates ASCII graphs for token usage data."""
    
    def __init__(self, token_data: TokenData):
        self.token_data = token_data
    
    def format_number(self, num: float, metric: str) -> str:
        """Format numbers with K/M suffixes."""
        if metric == 'cost':
            # For cost, keep decimal places
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            else:
                return f"{num:.2f}"
        else:
            # For tokens and requests, use integers
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            else:
                return f"{int(num)}"
    
    def generate_graph(self, days: int, metric: str) -> str:
        """Generate ASCII bar chart."""
        time_series, time_format = self.token_data.get_time_series_data(days)
        
        if not time_series:
            return "No data available for the selected time range."
        
        # Sort data by time
        sorted_data = sorted(time_series.items())
        
        if not sorted_data:
            return "No data points available."
        
        # Get values and labels
        values = [item[1][metric] for item in sorted_data]
        labels = [item[0] for item in sorted_data]
        
        if not values or max(values) == 0:
            return "No activity in the selected time range."
        
        # Create ASCII bar chart with wider bars
        max_val = max(values)
        chart_height = 15
        bar_width = 6  # Each bar is 6 characters wide
        
        # Scale values to chart height
        scaled_values = [int((v / max_val) * chart_height) if max_val > 0 else 0 for v in values]
        
        # Build the chart
        chart_lines = []
        
        # Title
        if metric == 'total_tokens':
            title = f"Token Usage Over Time ({days}d)"
        elif metric == 'cost':
            title = f"Cost Over Time ({days}d)"
        elif metric == 'requests':
            title = f"Requests Over Time ({days}d)"
        
        chart_lines.append(title.center(110))
        chart_lines.append("")
        
        # Y-axis labels and bars (wider bars for better labels)
        for row in range(chart_height, -1, -1):
            y_value = max_val * row / chart_height
            formatted_y = self.format_number(y_value, metric)
            line = f"{formatted_y:>8} │"
            
            for i, scaled_val in enumerate(scaled_values):
                if scaled_val >= row:
                    line += "█" * bar_width  # Wide bar
                else:
                    line += " " * bar_width  # Wide empty space
            
            chart_lines.append(line)
        
        # X-axis (match total width of all bars)
        x_axis = "         └" + "─" * (len(scaled_values) * bar_width)
        chart_lines.append(x_axis)
        
        # Create horizontal date labels (centered under wide bars)
        label_line = "          "  # Match Y-axis spacing
        
        # Show labels for all bars since we have space now
        for i in range(len(scaled_values)):
            label = labels[i]
            if days > 2:
                # Format as M/D
                date_part = label.split()[0]
                try:
                    parts = date_part.split('-')
                    month = int(parts[1])
                    day = int(parts[2])
                    short_date = f"{month}/{day}"
                    # Center the date under the wide bar
                    label_line += f"{short_date:^{bar_width}}"
                except:
                    label_line += f"{i:^{bar_width}}"
            else:
                # Format as HH:MM for hourly data
                time_part = label.split()[-1] if ' ' in label else label
                try:
                    time_str = time_part[:5]  # HH:MM
                    label_line += f"{time_str:^{bar_width}}"
                except:
                    label_line += f"{i:^{bar_width}}"
        
        chart_lines.append(label_line)
        
        return "\n".join(chart_lines)


class SummaryTab(Static):
    """Summary statistics tab."""
    
    def __init__(self, token_data: TokenData):
        super().__init__()
        self.token_data = token_data
    
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("**Token Usage Summary**", classes="header")
            yield Static(id="summary-stats")
            yield Static(id="model-breakdown")
    
    def on_mount(self):
        self.update_summary()
    
    def update_summary(self):
        stats = self.token_data.get_summary_stats()
        
        # Summary stats
        summary_text = f"""
**Total Statistics**
├── Total Requests: {stats['total_requests']:,}
├── Input Tokens: {stats['total_input']:,}
├── Output Tokens: {stats['total_output']:,}
├── Cache Creation: {stats['total_cache_creation']:,}
├── Cache Read: {stats['total_cache_read']:,}
├── Total Tokens: {stats['total_input'] + stats['total_output'] + stats['total_cache_creation'] + stats['total_cache_read']:,}
└── Total Cost: ${stats['total_cost']:.4f}
"""
        
        self.query_one("#summary-stats").update(summary_text)
        
        # Model breakdown
        model_text = "\n**Model Breakdown**\n"
        for model, data in stats['models'].items():
            total_tokens = data['input_tokens'] + data['output_tokens'] + data['cache_creation_input_tokens'] + data['cache_read_input_tokens']
            model_text += f"""
**{model}**
├── Requests: {data['requests']:,}
├── Tokens: {total_tokens:,}
├── Input/Output: {data['input_tokens']:,} / {data['output_tokens']:,}
├── Cache: {data['cache_creation_input_tokens']:,} writes, {data['cache_read_input_tokens']:,} reads
└── Cost: ${data['cost']:.4f}
"""
        
        self.query_one("#model-breakdown").update(model_text)


class RecentActivityTab(Static):
    """Recent activity tab."""
    
    def __init__(self, token_data: TokenData):
        super().__init__()
        self.token_data = token_data
    
    def compose(self) -> ComposeResult:
        yield Static("**Recent Activity**", classes="header")
        yield DataTable(id="recent-table")
    
    def on_mount(self):
        self.update_recent()
    
    def update_recent(self):
        table = self.query_one("#recent-table", DataTable)
        table.clear(columns=True)
        
        table.add_columns("Time", "Model", "Tokens", "Cost")
        
        recent = self.token_data.get_recent_activity(15)
        for entry in recent:
            local_timestamp = self.token_data.get_local_datetime(entry['timestamp'])
            timestamp = local_timestamp.strftime('%H:%M:%S') if local_timestamp else 'Unknown'
            model = entry['model'][:20]
            total_tokens = entry['input_tokens'] + entry['output_tokens'] + entry['cache_creation_input_tokens'] + entry['cache_read_input_tokens']
            cost = self.token_data.calculate_cost(entry)
            
            table.add_row(
                timestamp,
                model,
                f"{total_tokens:,}",
                f"${cost:.4f}"
            )


class TodayTab(Static):
    """Today's usage tab."""
    
    def __init__(self, token_data: TokenData):
        super().__init__()
        self.token_data = token_data
    
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("**Today's Usage**", classes="header")
            yield Static(id="today-stats")
    
    def on_mount(self):
        self.update_today()
    
    def update_today(self):
        today_data = self.token_data.get_today_data()
        stats = self.token_data.get_summary_stats(today_data)
        
        if stats['total_requests'] == 0:
            self.query_one("#today-stats").update("No usage today yet.")
            return
        
        today_text = f"""
**Today's Statistics**
├── Requests: {stats['total_requests']:,}
├── Input Tokens: {stats['total_input']:,}
├── Output Tokens: {stats['total_output']:,}
├── Cache Creation: {stats['total_cache_creation']:,}
├── Cache Read: {stats['total_cache_read']:,}
└── Cost: ${stats['total_cost']:.4f}

**Savings from Caching**
Cache reads would cost ${(stats['total_cache_read'] / 1_000_000) * 3.0:.4f} as regular input
Actual cache cost: ${(stats['total_cache_read'] / 1_000_000) * 0.30:.4f}
You saved: ${((stats['total_cache_read'] / 1_000_000) * 3.0) - ((stats['total_cache_read'] / 1_000_000) * 0.30):.4f} (90% savings!)
"""
        
        self.query_one("#today-stats").update(today_text)


class MonitorTab(Static):
    """Real-time monitoring tab."""
    
    def __init__(self, token_data: TokenData):
        super().__init__()
        self.token_data = token_data
        self.auto_refresh = True
        self.refresh_timer = None
    
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("**Real-time Token Monitor**", classes="header")
            yield Static(id="live-stats")
            yield Static(id="hourly-breakdown")
            yield Static("\n**Live Updates Every 10 seconds**", classes="subheader")
            yield Button("Pause Auto-refresh", id="toggle-refresh")
    
    def on_mount(self):
        self.update_monitor()
        self.start_auto_refresh()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        if self.refresh_timer:
            self.refresh_timer.stop()
        self.refresh_timer = self.set_interval(10.0, self.auto_update)
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        if self.refresh_timer:
            self.refresh_timer.stop()
            self.refresh_timer = None
    
    def auto_update(self):
        """Auto-update the monitor if enabled."""
        if self.auto_refresh:
            self.token_data.load_data()
            self.update_monitor()
    
    def update_monitor(self):
        """Update the monitor display."""
        # Live stats
        recent_data = self.token_data.get_recent_activity(5)
        if recent_data:
            latest = recent_data[0]
            local_timestamp = self.token_data.get_local_datetime(latest['timestamp'])
            if local_timestamp:
                time_ago = (datetime.now() - local_timestamp.replace(tzinfo=None)).total_seconds()
            else:
                time_ago = float('inf')
            
            if time_ago < 60:
                status = f"ACTIVE - Last activity: {int(time_ago)}s ago"
            elif time_ago < 3600:
                status = f"Recent activity: {int(time_ago/60)}m ago"
            else:
                status = f"Last activity: {int(time_ago/3600)}h ago"
        else:
            status = "No recent activity"
        
        today_stats = self.token_data.get_summary_stats(self.token_data.get_today_data())
        
        live_text = f"""
**Current Session Status**: {status}
**Today's Totals**:
├── Requests: {today_stats['total_requests']:,}
├── Total Tokens: {today_stats['total_input'] + today_stats['total_output'] + today_stats['total_cache_creation'] + today_stats['total_cache_read']:,}
└── Cost: ${today_stats['total_cost']:.4f}
"""
        
        self.query_one("#live-stats").update(live_text)
        
        # Hourly breakdown
        hourly_data = self.token_data.get_hourly_usage(12)
        if hourly_data:
            hourly_text = "\n**Last 12 Hours Breakdown**:\n"
            for hour, data in sorted(hourly_data.items()):
                hourly_text += f"{hour}: {data['tokens']:,} tokens, {data['requests']} requests, ${data['cost']:.3f}\n"
        else:
            hourly_text = "\nNo activity in the last 12 hours"
        
        self.query_one("#hourly-breakdown").update(hourly_text)
    
    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button press for pause/resume."""
        button = event.button
        if button.id == "toggle-refresh":
            self.auto_refresh = not self.auto_refresh
            if self.auto_refresh:
                button.label = "Pause Auto-refresh"
                self.start_auto_refresh()
            else:
                button.label = "Resume Auto-refresh"
                self.stop_auto_refresh()


class AnalyticsTab(Static):
    """Analytics tab with time series graphs."""
    
    def __init__(self, token_data: TokenData):
        super().__init__()
        self.token_data = token_data
        self.current_days = 7
        self.current_metric = 'total_tokens'
        self.graph_generator = GraphGenerator(token_data)
    
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("**Token Usage Analytics**", classes="header")
            
            # Time Range Controls with better spacing
            yield Static("**Time Range:**", classes="controls-text")
            with Horizontal(classes="button-row"):
                yield Button("24h", id="range-1", classes="range-button")
                yield Button("2d", id="range-2", classes="range-button") 
                yield Button("7d", id="range-7", classes="range-button active-range")
                yield Button("30d", id="range-30", classes="range-button")
            
            yield Static(id="graph-display")
            yield Static(id="graph-stats")
    
    def on_mount(self):
        self.update_graph()
    
    def update_graph(self):
        """Update the graph display."""
        graph = self.graph_generator.generate_graph(self.current_days, self.current_metric)
        self.query_one("#graph-display").update(f"```\n{graph}\n```")
        
        # Update stats
        time_series, _ = self.token_data.get_time_series_data(self.current_days)
        if time_series:
            total_tokens = sum(data['total_tokens'] for data in time_series.values())
            total_cost = sum(data['cost'] for data in time_series.values())
            total_requests = sum(data['requests'] for data in time_series.values())
            
            stats_text = f"""**Period Summary ({self.current_days}d)**:
├── Total Tokens: {total_tokens:,}
├── Total Cost: ${total_cost:.4f}
├── Total Requests: {total_requests:,}
└── Avg Tokens/Request: {total_tokens/max(1, total_requests):,.0f}"""
        else:
            stats_text = "No data available for the selected period."
        
        self.query_one("#graph-stats").update(stats_text)
    
    def update_button_states(self):
        """Update button active states."""
        range_map = {1: "range-1", 2: "range-2", 7: "range-7", 30: "range-30"}
        active_id = range_map.get(self.current_days, "range-7")
        
        for button_id in ["range-1", "range-2", "range-7", "range-30"]:
            try:
                button = self.query_one(f"#{button_id}", Button)
                if button_id == active_id:
                    button.add_class("active-range")
                else:
                    button.remove_class("active-range")
            except:
                pass
    
    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button press for time range controls."""
        button = event.button
        
        # Handle time range buttons
        if button.id.startswith("range-"):            
            # Set new range
            range_map = {"range-1": 1, "range-2": 2, "range-7": 7, "range-30": 30}
            self.current_days = range_map.get(button.id, 7)
            
            # Update button states
            self.update_button_states()
            
            # Update graph with new settings
            self.update_graph()