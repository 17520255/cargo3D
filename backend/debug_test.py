from algorithms.packing_algorithm import Box, ImprovedGeneticPackingOptimizer, SimulatedAnnealingPackingOptimizer, ExtremePointPackingOptimizer

def test_packing_step_by_step():
    """Test packing algorithms step by step"""
    
    print("🔍 Testing packing algorithms step by step...")
    
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
    
    print(f"✅ Created {len(goods)} boxes")
    print(f"✅ Container dimensions: {container}")
    
    try:
        # Test 1: Genetic Algorithm
        print("\n🧬 Testing Genetic Algorithm...")
        ga = ImprovedGeneticPackingOptimizer(population_size=10, generations=5)
        best_chromosome, fitness = ga.optimize(goods, container)
        print(f"✅ GA completed with {len(best_chromosome)} boxes, fitness: {fitness}")
        
        # Test 2: Simulated Annealing
        print("\n🔥 Testing Simulated Annealing...")
        sa = SimulatedAnnealingPackingOptimizer()
        sa_solution, sa_util = sa.pack(goods, container)
        print(f"✅ SA completed with {len(sa_solution)} boxes, utilization: {sa_util}")
        
        # Test 3: Extreme Point
        print("\n📍 Testing Extreme Point...")
        ep = ExtremePointPackingOptimizer()
        ep_solution, ep_util = ep.pack(goods, container)
        print(f"✅ EP completed with {len(ep_solution)} boxes, utilization: {ep_util}")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_packing_step_by_step() 