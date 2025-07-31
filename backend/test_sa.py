from algorithms.packing_algorithm import Box, SimulatedAnnealingPackingOptimizer

def test_simulated_annealing():
    """Test Simulated Annealing specifically"""
    
    print("🔥 Testing Simulated Annealing...")
    
    # Create test data
    goods = [
        Box(id="1", width=10, height=10, depth=10, name="Box 1", label="A", weight=5.0),
        Box(id="2", width=15, height=15, depth=15, name="Box 2", label="B", weight=8.0)
    ]
    
    container = {
        "width": 50,
        "height": 50,
        "depth": 50
    }
    
    try:
        sa = SimulatedAnnealingPackingOptimizer()
        sa_solution, sa_util = sa.pack(goods, container)
        print(f"✅ SA completed with {len(sa_solution)} boxes, utilization: {sa_util}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_simulated_annealing() 