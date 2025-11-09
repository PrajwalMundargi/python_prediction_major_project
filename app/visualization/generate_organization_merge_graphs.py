# app/visualization/generate_organization_merge_graphs.py
"""
Generate graphs for each organization showing merge activity over time.
Uses data from organization_merge_dates table.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func
from app.common.database import SessionLocal
from app.models.organization_merge_dates import OrganizationMergeDate

# Try to import scipy for smooth curves, but make it optional
try:
    from scipy.interpolate import make_interp_spline
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def generate_organization_graph(org_slug, org_name, output_path, days=15):
    """
    Generate a wave graph for a specific organization showing merges_per_day vs merge_date.
    
    Args:
        org_slug: Organization slug
        org_name: Organization name
        output_path: Path to save the graph
        days: Number of days to display (default: 15)
    
    Returns:
        str: Path to saved graph, or None if failed
    """
    with SessionLocal() as session:
        # Get merge dates with merges_per_day for this organization
        merge_dates = session.query(
            OrganizationMergeDate.merge_date,
            OrganizationMergeDate.merges_per_day
        ).filter(
            OrganizationMergeDate.organization_slug == org_slug
        ).order_by(
            OrganizationMergeDate.merge_date
        ).all()
    
    if not merge_dates:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(merge_dates, columns=['merge_date', 'merges_per_day'])
    df['merge_date'] = pd.to_datetime(df['merge_date'])
    df = df.sort_values('merge_date')
    
    # Remove duplicates by date, keeping the first merges_per_day value for each date
    df = df.drop_duplicates(subset=['merge_date'], keep='first')
    
    # Create the wave plot with smooth curves
    plt.figure(figsize=(14, 7))
    
    # Create a smooth wave-like plot
    ax = plt.gca()
    
    # Plot with smooth interpolation for wave effect
    plt.plot(df['merge_date'], df['merges_per_day'], 
             marker='o', linewidth=2.5, markersize=8, 
             color='#2E86AB', label='Merges per Day')
    
    # Fill area under the curve for wave effect
    plt.fill_between(df['merge_date'], df['merges_per_day'], 
                     alpha=0.4, color='#2E86AB')
    
    # Add a smooth curve overlay for wave effect (if scipy is available)
    if HAS_SCIPY and len(df) > 3:
        try:
            # Convert dates to numeric for interpolation
            x_numeric = mdates.date2num(df['merge_date'])
            x_smooth = np.linspace(x_numeric.min(), x_numeric.max(), 300)
            spl = make_interp_spline(x_numeric, df['merges_per_day'], k=min(3, len(df)-1))
            y_smooth = spl(x_smooth)
            x_smooth_dates = mdates.num2date(x_smooth)
            
            plt.plot(x_smooth_dates, y_smooth, '--', linewidth=1.5, 
                    alpha=0.6, color='#A23B72', label='Trend Line')
        except:
            # If interpolation fails, just use the regular plot
            pass
    
    # Customize the plot
    plt.title(f'Merge Activity Wave - {org_name}', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Merge Date', fontsize=14)
    plt.ylabel('Merges per Day', fontsize=14)
    plt.grid(True, alpha=0.3, linestyle='--', which='both')
    plt.legend(loc='upper right', fontsize=10)
    
    # Set y-axis limits to show 1-5 range clearly
    plt.ylim(0, 6)
    plt.yticks(range(0, 6))
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
    plt.xticks(rotation=45, ha='right')
    
    # Add statistics text
    total_merges = df['merges_per_day'].sum()
    avg_merges = df['merges_per_day'].mean()
    max_merges = df['merges_per_day'].max()
    max_date = df.loc[df['merges_per_day'].idxmax(), 'merge_date']
    min_merges = df['merges_per_day'].min()
    min_date = df.loc[df['merges_per_day'].idxmin(), 'merge_date']
    
    stats_text = (f'Total: {total_merges:.0f} | Avg: {avg_merges:.2f} | '
                  f'Max: {max_merges} ({max_date.strftime("%Y-%m-%d")}) | '
                  f'Min: {min_merges} ({min_date.strftime("%Y-%m-%d")})')
    plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=10, style='italic')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the graph
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_all_organization_graphs(output_dir='graphs/organizations', days=15):
    """
    Generate graphs for all organizations in the organization_merge_dates table.
    
    Args:
        output_dir: Directory to save graphs
        days: Number of days to display (default: 15)
    
    Returns:
        list: List of paths to generated graphs
    """
    print("Generating merge activity graphs for all organizations...")
    print("=" * 60)
    
    # Get all unique organizations
    with SessionLocal() as session:
        organizations = session.query(
            OrganizationMergeDate.organization_slug,
            OrganizationMergeDate.organization_name
        ).distinct().all()
    
    if not organizations:
        print("WARNING: No organizations found in organization_merge_dates table.")
        return []
    
    print(f"Found {len(organizations)} organizations to process")
    print("=" * 60)
    
    generated_graphs = []
    successful = 0
    failed = 0
    
    for org_slug, org_name in organizations:
        try:
            # Create safe filename from organization name
            safe_name = "".join(c for c in org_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{org_slug}_{safe_name}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Generate graph
            result = generate_organization_graph(org_slug, org_name, output_path, days=days)
            
            if result:
                generated_graphs.append(result)
                successful += 1
                print(f"  Generated graph for {org_name}")
            else:
                failed += 1
                print(f"  WARNING: No data for {org_name}")
                
        except Exception as e:
            failed += 1
            print(f"  ERROR: Error generating graph for {org_name}: {e}")
            continue
    
    print("=" * 60)
    print(f"Completed! Generated {successful} graphs, {failed} failed/skipped")
    print(f"Graphs saved to: {output_dir}")
    print("=" * 60)
    
    return generated_graphs


def generate_overall_trend_graph(output_path='graphs/overall_merge_trend.png', days=15):
    """
    Generate an overall trend graph showing merge activity across all organizations.
    
    Args:
        output_path: Path to save the graph
        days: Number of days to display (default: 15)
    
    Returns:
        str: Path to saved graph, or None if failed
    """
    print("Generating overall merge trend graph...")
    
    with SessionLocal() as session:
        # Get merge counts per day across all organizations
        merge_dates = session.query(
            OrganizationMergeDate.merge_date,
            func.count(OrganizationMergeDate.id).label('merge_count')
        ).group_by(
            OrganizationMergeDate.merge_date
        ).order_by(
            OrganizationMergeDate.merge_date
        ).all()
    
    if not merge_dates:
        print("WARNING: No merge dates found.")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(merge_dates, columns=['merge_date', 'merge_count'])
    df['merge_date'] = pd.to_datetime(df['merge_date'])
    df = df.sort_values('merge_date')
    
    # Create the plot
    plt.figure(figsize=(14, 7))
    plt.plot(df['merge_date'], df['merge_count'], marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
    plt.fill_between(df['merge_date'], df['merge_count'], alpha=0.3, color='#2E86AB')
    
    # Customize the plot
    plt.title('Overall Merge Activity Trend (All Organizations)', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Total Merges per Day', fontsize=14)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xticks(rotation=45, ha='right')
    
    # Add statistics text
    total_merges = df['merge_count'].sum()
    avg_merges = df['merge_count'].mean()
    max_merges = df['merge_count'].max()
    max_date = df.loc[df['merge_count'].idxmax(), 'merge_date']
    min_merges = df['merge_count'].min()
    min_date = df.loc[df['merge_count'].idxmin(), 'merge_date']
    
    stats_text = (f'Total Merges: {total_merges} | Avg/Day: {avg_merges:.1f} | '
                  f'Max: {max_merges} ({max_date.strftime("%Y-%m-%d")}) | '
                  f'Min: {min_merges} ({min_date.strftime("%Y-%m-%d")})')
    plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=10, style='italic')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the graph
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Overall trend graph saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    
    # Generate overall trend graph
    generate_overall_trend_graph()
    
    # Generate individual organization graphs
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = 'graphs/organizations'
    
    generate_all_organization_graphs(output_dir=output_dir)

