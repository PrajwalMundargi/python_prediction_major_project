# Merge Frequency Trend Visualization (Updated)

This system automatically tracks and visualizes merge frequency trends **only for organizations present in the `github_metrics` table**.

## Key Feature

**Filtered by `github_metrics` table**: Only organizations that exist in the `github_metrics` table are included in graphs and visualizations.

## How It Works

1. **Data Collection**: When you run the updater, it:
   - Fetches data from GitHub API
   - Updates `github_metrics` table (current values)
   - Stores historical snapshots in `historical_metrics` table

2. **Graph Generation**: When generating graphs:
   - Queries `github_metrics` table to get list of active organizations
   - Filters `historical_metrics` to only include those organizations
   - Generates visualizations for filtered data

## Usage

### Generate Overall Trend Graph

Shows average merge frequency for all organizations in `github_metrics`:

```bash
python -m app.visualization.merge_frequency_graph
```

### Generate Individual Organization Graphs

Generate graphs for all organizations in `github_metrics`:

```python
from app.visualization.merge_frequency_graph import generate_graphs_for_all_organizations

generate_graphs_for_all_organizations(days=30, output_dir="graphs/organizations")
```

Or generate for a specific organization (only if it exists in `github_metrics`):

```python
from app.visualization.merge_frequency_graph import generate_organization_specific_graph

generate_organization_specific_graph("homebrew", days=30)
```

### Automated Updates

The automation script now:
1. Updates GitHub metrics
2. Generates overall trend graph
3. Generates individual graphs for all organizations in `github_metrics`

```bash
# Run once
python -m app.automation.auto_update_graph once

# Run continuously (every 6 hours)
python -m app.automation.auto_update_graph
```

## Output Structure

```
graphs/
├── merge_frequency_trend.png          # Overall trend (filtered by github_metrics)
└── organizations/
    ├── merge_frequency_homebrew_30days.png
    ├── merge_frequency_django_30days.png
    └── ... (one graph per organization in github_metrics)
```

## Benefits

- **Focused Analysis**: Only shows data for organizations you're actively tracking
- **Automatic Filtering**: Excludes organizations that were removed or are no longer in `github_metrics`
- **Consistent Data**: Ensures graphs only show organizations with current data
- **Individual Tracking**: Generate separate graphs for each organization automatically

## Notes

- If an organization is removed from `github_metrics`, it will no longer appear in graphs
- Historical data is still stored in `historical_metrics`, but filtered out during visualization
- The system automatically adapts as you add/remove organizations from `github_metrics`

