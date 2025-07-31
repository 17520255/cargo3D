from app.services.packing_service import pack_goods_service
from app.api.models.schemas import PackingRequest, BoxRequest, ContainerRequest

def test_simple_packing():
    """Test the packing service with minimal data"""
    
    print("🔍 Testing simple packing...")
    
    # Create minimal request
    request = PackingRequest(
        goods=[
            BoxRequest(id="1", width=10, height=10, depth=10, name="Box 1", label="A", weight=5.0)
        ],
        container=ContainerRequest(width=50, height=50, depth=50)
    )
    
    try:
        print("✅ Created request")
        result = pack_goods_service(request)
        print("✅ Packing completed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_simple_packing() 