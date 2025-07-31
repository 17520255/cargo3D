from app.services.packing_service import pack_goods_service
from app.api.models.schemas import PackingRequest, BoxRequest, ContainerRequest

def test_service_direct():
    """Test the service directly"""
    
    print("🔍 Testing service directly...")
    
    # Create request
    request = PackingRequest(
        goods=[
            BoxRequest(id="1", width=10, height=10, depth=10, name="Box 1", label="A", weight=5.0),
            BoxRequest(id="2", width=15, height=15, depth=15, name="Box 2", label="B", weight=8.0)
        ],
        container=ContainerRequest(width=50, height=50, depth=50)
    )
    
    try:
        print("✅ Created request")
        result = pack_goods_service(request)
        print("✅ Service completed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_service_direct() 