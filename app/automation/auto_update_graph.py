# app/automation/auto_update_graph.py
"""
Automated script to update merge frequency graphs.
This script can be run periodically (via cron, Task Scheduler, or as a service)
to automatically update the visualization.
"""
import time
import schedule
from app.visualization.merge_frequency_graph import generate_merge_frequency_graph
from app.visualization.generate_merge_dates_graphs import generate_all_merge_dates_graphs
from app.pipeline.update_github_metrics import update_github_data
from app.pipeline.fetch_merge_dates import fetch_all_merge_dates
import os

def update_data_and_graph():
    """Update GitHub data and regenerate the graph."""
    print("=" * 60)
    print(f"Automated Update Started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Step 1: Fetch merge dates from GitHub API
        print("\n1. Fetching merge dates from GitHub API (last 30 days)...")
        fetch_all_merge_dates(days=30, start_from_id=None)
        
        # Step 2: Update GitHub metrics (optional - for other metrics)
        print("\n2. Updating GitHub metrics...")
        update_github_data(start_from_id=None)  # Update all organizations
        
        # Step 3: Generate individual line graphs based on merge dates
        print("\n3. Generating individual merge frequency graphs from merge dates...")
        generate_all_merge_dates_graphs(
            days=30,
            output_dir=os.path.join("graphs", "organizations")
        )
        
        print("\nAutomated update completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: Error during automated update: {e}")
        print("=" * 60)


def run_daily_at_time(hour=2, minute=0):
    """
    Run daily updates at a specific time.
    
    Args:
        hour: Hour of day (0-23) to run update (default: 2 AM)
        minute: Minute of hour (0-59) to run update (default: 0)
    """
    print(f"Starting daily automated graph updater")
    print(f"Scheduled to run daily at {hour:02d}:{minute:02d}")
    print("Press Ctrl+C to stop")
    
    # Schedule the update
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(update_data_and_graph)
    
    # Run immediately on start
    print("\nRunning initial update...")
    update_data_and_graph()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nStopping automated updater...")


def run_continuous(update_interval_hours=6):
    """
    Run continuous updates at specified intervals.
    
    Args:
        update_interval_hours: Hours between each update (default: 6)
    """
    print(f"Starting automated graph updater (updates every {update_interval_hours} hours)")
    print("Press Ctrl+C to stop")
    
    # Schedule the update
    schedule.every(update_interval_hours).hours.do(update_data_and_graph)
    
    # Run immediately on start
    update_data_and_graph()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nStopping automated updater...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once and exit
        update_data_and_graph()
    elif len(sys.argv) > 1 and sys.argv[1] == "daily":
        # Run daily at specified time (default: 2:00 AM)
        hour = 2
        minute = 0
        if len(sys.argv) > 2:
            try:
                time_str = sys.argv[2]  # Format: "HH:MM" or "HH"
                if ":" in time_str:
                    hour, minute = map(int, time_str.split(":"))
                else:
                    hour = int(time_str)
            except (ValueError, IndexError):
                print("WARNING: Invalid time format. Using default 02:00")
        run_daily_at_time(hour=hour, minute=minute)
    else:
        # Run continuously
        interval = 6  # default 6 hours
        if len(sys.argv) > 1:
            try:
                interval = int(sys.argv[1])
            except ValueError:
                pass
        run_continuous(update_interval_hours=interval)

