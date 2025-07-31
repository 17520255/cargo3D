import time
from algorithms.packing_algorithm import PackingAlgorithm, Box as OldBox
from algorithms.enhanced_packing_algorithm import EnhancedPackingAlgorithm, Box as EnhancedBox

def test_compare_algorithms():
    """So sánh hiệu suất giữa thuật toán cũ và thuật toán mới"""
    
    print("🔍 So sánh hiệu suất thuật toán đóng gói...")
    
    # Tạo dữ liệu test
    test_boxes = [
        # id, width, height, depth, name, label, weight
        ("1", 700, 960, 690, "Box 1", "1", 10),
        ("2", 700, 960, 690, "Box 2", "1", 10),
        ("3", 700, 960, 690, "Box 3", "1", 10),
        ("4", 700, 960, 690, "Box 4", "1", 10),
        ("5", 700, 960, 690, "Box 5", "1", 10),
        ("6", 500, 500, 500, "Box 6", "2", 8),
        ("7", 500, 500, 500, "Box 7", "2", 8),
        ("8", 500, 500, 500, "Box 8", "2", 8),
        ("9", 800, 400, 600, "Box 9", "3", 12),
        ("10", 800, 400, 600, "Box 10", "3", 12),
    ]
    
    container_dimensions = {
        "width": 2340,
        "height": 2694,
        "depth": 12117
    }
    
    print(f"✅ Tạo {len(test_boxes)} boxes để test")
    print(f"✅ Container dimensions: {container_dimensions}")
    
    # Tạo danh sách box cho thuật toán cũ
    old_goods = []
    for box_data in test_boxes:
        box = OldBox(
            id=box_data[0],
            width=box_data[1],
            height=box_data[2],
            depth=box_data[3],
            name=box_data[4],
            label=box_data[5],
            weight=box_data[6]
        )
        old_goods.append(box)
    
    # Tạo danh sách box cho thuật toán mới
    enhanced_goods = []
    for box_data in test_boxes:
        box = EnhancedBox(
            id=box_data[0],
            width=box_data[1],
            height=box_data[2],
            depth=box_data[3],
            name=box_data[4],
            label=box_data[5],
            weight=box_data[6]
        )
        enhanced_goods.append(box)
    
    # Test thuật toán cũ
    print("\n📊 Test thuật toán cũ (Best Fit)...")
    old_algo = PackingAlgorithm()
    old_algo.set_algorithm("best_fit")  # Sử dụng Best Fit
    
    old_start_time = time.time()
    old_boxes, old_util = old_algo.pack(old_goods, container_dimensions)
    old_time = time.time() - old_start_time
    
    print(f"✅ Thuật toán cũ đặt được {len(old_boxes)}/{len(old_goods)} boxes")
    print(f"✅ Tỷ lệ sử dụng: {old_util:.2%}")
    print(f"✅ Thời gian thực thi: {old_time:.4f} giây")
    
    # Test thuật toán mới (Extreme Point)
    print("\n📊 Test thuật toán mới (Extreme Point + Layer-based)...")
    enhanced_algo = EnhancedPackingAlgorithm()
    
    enhanced_start_time = time.time()
    enhanced_boxes, enhanced_util = enhanced_algo.pack(enhanced_goods, container_dimensions)
    enhanced_time = time.time() - enhanced_start_time
    
    print(f"✅ Thuật toán mới đặt được {len(enhanced_boxes)}/{len(enhanced_goods)} boxes")
    print(f"✅ Tỷ lệ sử dụng: {enhanced_util:.2%}")
    print(f"✅ Thời gian thực thi: {enhanced_time:.4f} giây")
    
    # So sánh kết quả
    print("\n🏆 So sánh kết quả:")
    print(f"- Số lượng box đặt được: {'Thuật toán mới' if len(enhanced_boxes) > len(old_boxes) else 'Thuật toán cũ' if len(old_boxes) > len(enhanced_boxes) else 'Cả hai'} tốt hơn")
    print(f"- Tỷ lệ sử dụng: {'Thuật toán mới' if enhanced_util > old_util else 'Thuật toán cũ' if old_util > enhanced_util else 'Cả hai'} tốt hơn")
    print(f"- Thời gian thực thi: {'Thuật toán mới' if enhanced_time < old_time else 'Thuật toán cũ' if old_time < enhanced_time else 'Cả hai'} nhanh hơn")
    
    # Test thuật toán mới với tối ưu hóa
    print("\n📊 Test thuật toán mới với tối ưu hóa (nhiều chiến lược)...")
    
    enhanced_opt_start_time = time.time()
    enhanced_opt_boxes, enhanced_opt_util = enhanced_algo.optimize_packing(
        enhanced_goods, container_dimensions, respect_groups=True, time_limit=10
    )
    enhanced_opt_time = time.time() - enhanced_opt_start_time
    
    print(f"✅ Thuật toán mới (tối ưu) đặt được {len(enhanced_opt_boxes)}/{len(enhanced_goods)} boxes")
    print(f"✅ Tỷ lệ sử dụng: {enhanced_opt_util:.2%}")
    print(f"✅ Thời gian thực thi: {enhanced_opt_time:.4f} giây")
    
    print("\n🎉 Test hoàn thành!")

if __name__ == "__main__":
    test_compare_algorithms() 