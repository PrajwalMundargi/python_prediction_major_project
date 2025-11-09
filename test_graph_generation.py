# test_graph_generation.py
"""
Test script to verify graph generation works correctly.
Creates sample historical data and generates graphs.
"""
from app.common.database import SessionLocal
from app.models.historical_metrics import HistoricalMetrics
from app.models.github_metrics import GitHubMetrics
from app.visualization.merge_frequency_graph import generate_merge_frequency_graph, generate_graphs_for_all_organizations
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create sample historical data for testing."""
    print("Creating test historical data...")
    
    with SessionLocal() as session:
        # Get organizations from github_metrics
        orgs = session.query(GitHubMetrics.slug, GitHubMetrics.name).limit(5).all()
        
        if not orgs:
            print("WARNING: No organizations in github_metrics. Cannot create test data.")
            return False
        
        print(f"Found {len(orgs)} organizations. Creating historical data...")
        
        # Create historical data for the last 7 days
        for slug, name in orgs:
            base_frequency = random.uniform(0.5, 0.9)
            
            for day_offset in range(7, 0, -1):
                date = datetime.utcnow() - timedelta(days=day_offset)
                # Add some variation to simulate trends
                variation = random.uniform(-0.05, 0.05)
                frequency = max(0.0, min(1.0, base_frequency + variation))
                
                historical_entry = HistoricalMetrics(
                    organization_slug=slug,
                    organization_name=name,
                    merge_frequency=round(frequency, 3),
                    total_prs=random.randint(100, 1000),
                    merged_prs=int((frequency * random.randint(100, 1000))),
                    recorded_at=date
                )
                session.add(historical_entry)
        
        session.commit()
        print(f"Created historical data for {len(orgs)} organizations over 7 days")
        return True

def test_graph_generation():
    """Test graph generation."""
    print("\n" + "="*60)
    print("🧪 Testing Graph Generation")
    print("="*60)
    
    # Create test data
    if not create_test_data():
        return
    
    # Test 1: Overall trend graph
    print("\nTest 1: Generating overall trend graph...")
    try:
        result = generate_merge_frequency_graph(days=7, output_path="test_overall_trend.png")
        if result:
            print(f"Overall graph generated successfully: {result}")
        else:
            print("Failed to generate overall graph")
    except Exception as e:
        print(f"ERROR: Error generating overall graph: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Individual organization graphs
    print("\nTest 2: Generating individual organization graphs...")
    try:
        results = generate_graphs_for_all_organizations(days=7, output_dir="test_graphs/organizations")
        if results:
            print(f"Generated {len(results)} individual graphs")
            for graph in results[:3]:  # Show first 3
                print(f"   - {graph}")
        else:
            print("WARNING: No individual graphs generated")
    except Exception as e:
        print(f"ERROR: Error generating individual graphs: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Graph generation test completed!")
    print("="*60)

if __name__ == "__main__":
    test_graph_generation()

