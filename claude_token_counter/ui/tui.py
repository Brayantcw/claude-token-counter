#!/usr/bin/env python3
"""
Claude CLI Token Counter - Terminal User Interface

A beautiful TUI for tracking Claude CLI token usage and costs.
"""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.binding import Binding

from ..core.token_data import TokenData
from .components import (
    SummaryTab, RecentActivityTab, TodayTab, 
    MonitorTab, AnalyticsTab
)


class ClaudeTokenTUI(App):
    """Claude Token Counter TUI Application."""
    
    CSS = """
        .header {
            text-align: center;
            margin: 1;
            color: $accent;
            text-style: bold;
        }

        .subheader {
            margin: 1 0;
            color: $secondary;
            text-style: bold;
        }

        #summary-stats, #model-breakdown, #today-stats, #live-stats, #hourly-breakdown {
            margin: 1;
            padding: 1;
            border: solid $primary;
        }

        #toggle-refresh {
            margin: 1;
        }

        .controls-text {
            margin: 1;
            text-align: center;
            color: $accent;
        }

        /* Button styling fixes */
        Button {
            margin: 0 1;
            min-width: 10;  /* Increased from 8 */
            width: auto;    /* Allow auto width */
            height: 3;
            color: white;
            text-align: center;
        }

        .range-button {
            margin: 0 1;
            min-width: 8;
            max-width: 12;
            height: 3;
            border: solid $primary;
        }

        .range-button.active-range {
            background: $accent;
            color: $text;
            border: solid $accent;
        }

        .button-row {
            align: center middle;
            margin: 1;
            height: auto;
        }

        /* Horizontal container fixes */
        Horizontal {
            height: auto;
            align: center middle;
        }

        .separator {
            color: $secondary;
        }

        #graph-display {
            margin: 1;
            padding: 1;
            border: solid $accent;
            height: 25;
        }

        #graph-stats {
            margin: 1;
            padding: 1;
            border: solid $primary;
        }

        DataTable {
            margin: 1;
        }

        TabbedContent {
            margin: 1;
        }
        """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.token_data = TokenData()
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with TabbedContent(initial="monitor"):
            with TabPane("Live Monitor", id="monitor"):
                yield MonitorTab(self.token_data)
                
            with TabPane("Today", id="today"):
                yield TodayTab(self.token_data)
                
            with TabPane("Recent Activity", id="recent"):
                yield RecentActivityTab(self.token_data)
                
            with TabPane("Analytics", id="analytics"):
                yield AnalyticsTab(self.token_data)
                
            with TabPane("Summary", id="summary"):
                yield SummaryTab(self.token_data)
        
        yield Footer()
    
    def action_refresh(self):
        """Refresh data."""
        self.token_data.load_data()
        
        # Update all tabs
        try:
            monitor_tab = self.query_one(MonitorTab)
            monitor_tab.update_monitor()
        except:
            pass
        
        try:
            summary_tab = self.query_one(SummaryTab)
            summary_tab.update_summary()
        except:
            pass
        
        try:
            recent_tab = self.query_one(RecentActivityTab)
            recent_tab.update_recent()
        except:
            pass
        
        try:
            today_tab = self.query_one(TodayTab)
            today_tab.update_today()
        except:
            pass
        
        try:
            analytics_tab = self.query_one(AnalyticsTab)
            analytics_tab.update_graph()
        except:
            pass
        
        self.notify("Data refreshed!")


def main():
    """Main entry point for the TUI."""
    app = ClaudeTokenTUI()
    app.run()


if __name__ == "__main__":
    main()