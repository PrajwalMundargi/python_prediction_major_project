# Merge Frequency Trend Visualization

This system automatically tracks and visualizes merge frequency trends for GitHub organizations.

## Features

- **Historical Tracking**: Stores merge frequency snapshots over time
- **Automated Updates**: Automatically updates data and regenerates graphs
- **Trend Analysis**: Shows increasing/decreasing rates with trend lines
- **Multiple Views**: Overall trends and organization-specific graphs

## Setup

### 1. Create the Historical Metrics Table

First, create the database table to store historical data:

```bash
python -m app.scripts.create_historical_table
```

### 2. Update GitHub Metrics (with Historical Tracking)

The update script now automatically stores historical snapshots:

```bash
python -m app.pipeline.update_github_metrics 76
```

Each time you run the updater, it will:
- Update current metrics
- Store a historical snapshot
- Track changes over time

## Usage

### Generate Overall Trend Graph

Generate a graph showing average merge frequency trends across all organizations:

```bash
# Default: Last 30 days
python -m app.visualization.merge_frequency_graph

# Custom: Last 60 days
python -m app.visualization.merge_frequency_graph 60
```

The graph will be saved to `graphs/merge_frequency_trend.png`

### Generate Organization-Specific Graph

Generate a graph for a specific organization:

```python
from app.visualization.merge_frequency_graph import generate_organization_specific_graph

generate_organization_specific_graph("homebrew", days=30)
```

### Automated Updates

#### Option 1: Run Once

Update data and graph once:

```bash
python -m app.automation.auto_update_graph once
```

#### Option 2: Continuous Updates

Run continuous updates every 6 hours (default):

```bash
python -m app.automation.auto_update_graph
```

Or specify custom interval (in hours):

```bash
python -m app.automation.auto_update_graph 12  # Every 12 hours
```

#### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at specific time)
4. Action: Start a program
5. Program: `python`
6. Arguments: `-m app.automation.auto_update_graph once`
7. Start in: Your project directory

#### Option 4: Linux Cron Job

Add to crontab (`crontab -e`):

```bash
# Update every 6 hours
0 */6 * * * cd /path/to/project && python -m app.automation.auto_update_graph once
```

## Graph Features

The generated graphs include:

1. **Average Merge Frequency Trend**: Shows overall trend with trend line
2. **Rate of Change**: Displays percentage increase/decrease
3. **Organization Count**: Shows how many organizations are being tracked
4. **Summary Statistics**: Period, averages, highs, lows, and overall change

## File Structure

```
app/
├── models/
│   └── historical_metrics.py      # Historical data model
├── visualization/
│   └── merge_frequency_graph.py   # Graph generation
├── automation/
│   └── auto_update_graph.py       # Automated updates
└── scripts/
    └── create_historical_table.py # Table creation
```

## Output

Graphs are saved to:
- Overall trend: `graphs/merge_frequency_trend.png`
- Organization-specific: `merge_frequency_{slug}_{days}days.png`

## Notes

- Historical data is stored automatically when you run the updater
- Graphs update automatically when you run the automation script
- The system tracks merge frequency changes over time
- Trend lines show whether merge frequency is increasing or decreasing

