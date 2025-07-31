from app.services.packing_service import pack_goods_service
from app.api.models.schemas import PackingRequest, BoxRequest, ContainerRequest

def test_step_by_step():
    """Test the packing service step by step"""
    
    print("🔍 Testing step by step...")
    
    # Step 1: Create request
    print("Step 1: Creating request...")
    request = PackingRequest(
        goods=[
            BoxRequest(id="1", width=10, height=10, depth=10, name="Box 1", label="A", weight=5.0),
            BoxRequest(id="2", width=15, height=15, depth=15, name="Box 2", label="B", weight=8.0)
        ],
        container=ContainerRequest(width=50, height=50, depth=50)
    )
    print("✅ Request created")
    
    # Step 2: Convert to Box objects
    print("Step 2: Converting to Box objects...")
    from algorithms.packing_algorithm import Box
    goods = [Box(**box.dict()) for box in request.goods]
    print(f"✅ Created {len(goods)} boxes")
    
    # Step 3: Test each algorithm individually
    print("Step 3: Testing algorithms individually...")
    
    # Test GA
    print("Testing GA...")
    from algorithms.packing_algorithm import ImprovedGeneticPackingOptimizer
    ga = ImprovedGeneticPackingOptimizer(population_size=10, generations=5)
    container = request.container.dict()
    try:
        best_chromosome, fitness = ga.optimize(goods, container)
        print(f"✅ GA completed with {len(best_chromosome)} boxes, fitness: {fitness}")
    except Exception as e:
        print(f"❌ GA error: {str(e)}")
        import traceback
        print(f"GA traceback: {traceback.format_exc()}")
    
    # Test SA
    print("Testing SA...")
    from algorithms.packing_algorithm import SimulatedAnnealingPackingOptimizer
    sa = SimulatedAnnealingPackingOptimizer()
    try:
        sa_solution, sa_util = sa.pack(goods, container)
        print(f"✅ SA completed with {len(sa_solution)} boxes, utilization: {sa_util}")
    except Exception as e:
        print(f"❌ SA error: {str(e)}")
        import traceback
        print(f"SA traceback: {traceback.format_exc()}")
    
    # Test EP
    print("Testing EP...")
    from algorithms.packing_algorithm import ExtremePointPackingOptimizer
    ep = ExtremePointPackingOptimizer()
    try:
        ep_solution, ep_util = ep.pack(goods, container)
        print(f"✅ EP completed with {len(ep_solution)} boxes, utilization: {ep_util}")
    except Exception as e:
        print(f"❌ EP error: {str(e)}")
        import traceback
        print(f"EP traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_step_by_step() 