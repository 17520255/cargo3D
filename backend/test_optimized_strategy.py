#!/usr/bin/env python3
"""
Test script để kiểm tra thuật toán đóng gói tối ưu theo chiến lược:
1. Lấp đầy trục x (chiều rộng) tối ưu
2. Lấp đầy chiều cao (y)  
3. Lấp đầy từ trong ra ngoài (từ z=0 ra cửa)
4. Tối ưu hoá theo "khối"
"""

import time
from collections import defaultdict
import sys
import os

# Thêm đường dẫn để import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.packing_algorithm import PackingAlgorithm, Box as OldBox
from algorithms.enhanced_packing_algorithm import EnhancedPackingAlgorithm, Box as EnhancedBox
from algorithms.optimized_layer_packing import OptimizedLayerPackingAlgorithm, Box as OptimizedBox

def create_test_data():
    """Tạo dữ liệu test đa dạng để kiểm tra chiến lược"""
    
    # Test case 1: Box cùng kích thước, khác nhóm
    test1_boxes = [
        ("1", 500, 500, 500, "Box A1", "A", 10),
        ("2", 500, 500, 500, "Box A2", "A", 10),
        ("3", 500, 500, 500, "Box A3", "A", 10),
        ("4", 600, 400, 400, "Box B1", "B", 8),
        ("5", 600, 400, 400, "Box B2", "B", 8),
        ("6", 800, 300, 300, "Box C1", "C", 6),
    ]
    
    # Test case 2: Box có thể kết hợp lấp đầy chiều rộng
    test2_boxes = [
        ("7", 700, 800, 600, "Box D1", "D", 12),
        ("8", 700, 800, 600, "Box D2", "D", 12),
        ("9", 800, 600, 500, "Box E1", "E", 10),
        ("10", 800, 600, 500, "Box E2", "E", 10),
        ("11", 740, 500, 400, "Box F1", "F", 8),
        ("12", 740, 500, 400, "Box F2", "F", 8),
    ]
    
    # Test case 3: Box nhỏ có thể kết hợp
    test3_boxes = [
        ("13", 400, 300, 200, "Box G1", "G", 5),
        ("14", 400, 300, 200, "Box G2", "G", 5),
        ("15", 500, 300, 200, "Box G3", "G", 5),
        ("16", 640, 300, 200, "Box G4", "G", 5),
        ("17", 300, 400, 250, "Box H1", "H", 4),
        ("18", 300, 400, 250, "Box H2", "H", 4),
    ]
    
    return test1_boxes + test2_boxes + test3_boxes

def convert_to_algorithm_boxes(test_boxes, box_class):
    """Chuyển đổi test data thành box objects cho từng thuật toán"""
    boxes = []
    for box_data in test_boxes:
        box = box_class(
            id=box_data[0],
            width=box_data[1],
            height=box_data[2],
            depth=box_data[3],
            name=box_data[4],
            label=box_data[5],
            weight=box_data[6]
        )
        boxes.append(box)
    return boxes

def analyze_packing_result(boxes, container_dims, algorithm_name):
    """Phân tích kết quả đóng gói theo chiến lược"""
    print(f"\n📊 PHÂN TÍCH KẾT QUẢ - {algorithm_name}")
    print("=" * 60)
    
    if not boxes:
        print("❌ Không có box nào được đặt")
        return
    
    # 1. Phân tích lấp đầy trục x (chiều rộng)
    print("1️⃣ PHÂN TÍCH LẤP ĐẦY TRỤC X (CHIỀU RỘNG):")
    
    # Nhóm box theo z và y để phân tích từng hàng
    rows = defaultdict(list)
    for box in boxes:
        row_key = (round(box.position['z'], 1), round(box.position['y'], 1))
        rows[row_key].append(box)
    
    total_width_efficiency = 0
    row_count = 0
    
    for (z, y), row_boxes in rows.items():
        # Sắp xếp theo x
        row_boxes.sort(key=lambda b: b.position['x'])
        
        # Tính tổng chiều rộng của hàng
        total_row_width = sum(box.width for box in row_boxes)
        width_efficiency = total_row_width / container_dims['width']
        
        print(f"  Hàng tại (z={z}, y={y}): {len(row_boxes)} box, "
              f"chiều rộng {total_row_width:.0f}/{container_dims['width']:.0f} "
              f"({width_efficiency:.1%})")
        
        # Kiểm tra xem các box có liền kề không
        gaps = []
        for i in range(len(row_boxes) - 1):
            gap = row_boxes[i+1].position['x'] - (row_boxes[i].position['x'] + row_boxes[i].width)
            gaps.append(gap)
        
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            print(f"    → Khoảng trống trung bình: {avg_gap:.1f}mm")
        
        total_width_efficiency += width_efficiency
        row_count += 1
    
    avg_width_efficiency = total_width_efficiency / row_count if row_count > 0 else 0
    print(f"  📈 Hiệu quả lấp đầy chiều rộng trung bình: {avg_width_efficiency:.1%}")
    
    # 2. Phân tích lấp đầy chiều cao (y)
    print("\n2️⃣ PHÂN TÍCH LẤP ĐẦY CHIỀU CAO (Y):")
    
    # Nhóm box theo z để phân tích từng lớp
    layers = defaultdict(list)
    for box in boxes:
        layer_key = round(box.position['z'], 1)
        layers[layer_key].append(box)
    
    for z, layer_boxes in sorted(layers.items()):
        # Tính chiều cao sử dụng của lớp
        max_y = max(box.position['y'] + box.height for box in layer_boxes)
        height_efficiency = max_y / container_dims['height']
        
        print(f"  Lớp z={z}: {len(layer_boxes)} box, "
              f"chiều cao {max_y:.0f}/{container_dims['height']:.0f} "
              f"({height_efficiency:.1%})")
        
        # Phân tích stacking - tìm các box chồng lên nhau
        stacks = defaultdict(list)
        for box in layer_boxes:
            stack_key = (round(box.position['x'], 1), round(box.position['z'], 1))
            stacks[stack_key].append(box)
        
        stack_count = sum(1 for stack in stacks.values() if len(stack) > 1)
        print(f"    → Số cột có chồng box: {stack_count}/{len(stacks)}")
    
    # 3. Phân tích lấp đầy từ trong ra ngoài (z)
    print("\n3️⃣ PHÂN TÍCH LẤP ĐẦY TỪ TRONG RA NGOÀI (Z):")
    
    # Sắp xếp box theo z
    sorted_by_z = sorted(boxes, key=lambda b: b.position['z'])
    
    # Tìm khoảng trống lớn nhất theo z
    z_positions = sorted(set(box.position['z'] for box in boxes))
    
    print(f"  Số lớp z: {len(z_positions)}")
    print(f"  Vị trí z: {[f'{z:.0f}' for z in z_positions[:5]]}" + 
          ("..." if len(z_positions) > 5 else ""))
    
    # Kiểm tra có bắt đầu từ z=0 không
    starts_from_zero = min(box.position['z'] for box in boxes) < 10
    print(f"  ✅ Bắt đầu từ z≈0: {'Có' if starts_from_zero else 'Không'}")
    
    # Tính độ đầy theo z
    max_z = max(box.position['z'] + box.depth for box in boxes)
    z_efficiency = max_z / container_dims['depth']
    print(f"  📈 Hiệu quả sử dụng độ sâu: {z_efficiency:.1%}")
    
    # 4. Phân tích tối ưu hóa theo "khối"
    print("\n4️⃣ PHÂN TÍCH TỐI ƯU HÓA THEO KHỐI:")
    
    # Nhóm box theo label
    groups = defaultdict(list)
    for box in boxes:
        groups[box.label].append(box)
    
    for label, group_boxes in groups.items():
        if len(group_boxes) <= 1:
            continue
            
        print(f"  Nhóm {label}: {len(group_boxes)} box")
        
        # Tính độ phân tán của nhóm
        center_x = sum(box.position['x'] + box.width/2 for box in group_boxes) / len(group_boxes)
        center_y = sum(box.position['y'] + box.height/2 for box in group_boxes) / len(group_boxes)
        center_z = sum(box.position['z'] + box.depth/2 for box in group_boxes) / len(group_boxes)
        
        distances = []
        for box in group_boxes:
            box_center_x = box.position['x'] + box.width/2
            box_center_y = box.position['y'] + box.height/2
            box_center_z = box.position['z'] + box.depth/2
            
            distance = ((box_center_x - center_x)**2 + 
                       (box_center_y - center_y)**2 + 
                       (box_center_z - center_z)**2)**0.5
            distances.append(distance)
        
        avg_distance = sum(distances) / len(distances)
        container_diagonal = (container_dims['width']**2 + 
                            container_dims['height']**2 + 
                            container_dims['depth']**2)**0.5
        
        compactness = 1 - (avg_distance / container_diagonal)
        print(f"    → Độ gần nhau: {compactness:.1%}")
        
        # Kiểm tra có tạo thành khối không
        if compactness > 0.8:
            print(f"    ✅ Tạo thành khối tốt")
        elif compactness > 0.6:
            print(f"    ⚠️ Tạo thành khối trung bình")
        else:
            print(f"    ❌ Box bị phân tán")

def test_all_algorithms():
    """Test và so sánh tất cả thuật toán"""
    print("🔍 KIỂM TRA THUẬT TOÁN ĐÓNG GÓI THEO CHIẾN LƯỢC")
    print("=" * 80)
    
    # Tạo dữ liệu test
    test_boxes = create_test_data()
    container_dims = {"width": 2340, "height": 2694, "depth": 12117}
    
    print(f"📦 Dữ liệu test: {len(test_boxes)} box")
    print(f"📏 Container: {container_dims['width']} x {container_dims['height']} x {container_dims['depth']}")
    
    results = {}
    
    # Test thuật toán cũ (Best Fit)
    print("\n" + "="*80)
    print("🔧 TEST THUẬT TOÁN CŨ (BEST FIT)")
    print("="*80)
    
    old_boxes = convert_to_algorithm_boxes(test_boxes, OldBox)
    old_algo = PackingAlgorithm()
    old_algo.set_algorithm("best_fit")
    
    start_time = time.time()
    old_result, old_util = old_algo.pack(old_boxes, container_dims)
    old_time = time.time() - start_time
    
    results['Best Fit'] = {
        'boxes': len(old_result),
        'utilization': old_util,
        'time': old_time,
        'result': old_result
    }
    
    print(f"✅ Đặt được: {len(old_result)}/{len(old_boxes)} box ({len(old_result)/len(old_boxes)*100:.1f}%)")
    print(f"✅ Tỷ lệ sử dụng: {old_util:.2%}")
    print(f"✅ Thời gian: {old_time:.3f}s")
    
    analyze_packing_result(old_result, container_dims, "THUẬT TOÁN CŨ (BEST FIT)")
    
    # Test thuật toán enhanced
    print("\n" + "="*80)
    print("🔧 TEST THUẬT TOÁN ENHANCED (EXTREME POINT)")
    print("="*80)
    
    enhanced_boxes = convert_to_algorithm_boxes(test_boxes, EnhancedBox)
    enhanced_algo = EnhancedPackingAlgorithm()
    
    start_time = time.time()
    enhanced_result, enhanced_util = enhanced_algo.pack(enhanced_boxes, container_dims)
    enhanced_time = time.time() - start_time
    
    results['Enhanced'] = {
        'boxes': len(enhanced_result),
        'utilization': enhanced_util,
        'time': enhanced_time,
        'result': enhanced_result
    }
    
    print(f"✅ Đặt được: {len(enhanced_result)}/{len(enhanced_boxes)} box ({len(enhanced_result)/len(enhanced_boxes)*100:.1f}%)")
    print(f"✅ Tỷ lệ sử dụng: {enhanced_util:.2%}")
    print(f"✅ Thời gian: {enhanced_time:.3f}s")
    
    analyze_packing_result(enhanced_result, container_dims, "THUẬT TOÁN ENHANCED")
    
    # Test thuật toán tối ưu mới
    print("\n" + "="*80)
    print("🔧 TEST THUẬT TOÁN TỐI ƯU MỚI (OPTIMIZED LAYER)")
    print("="*80)
    
    optimized_boxes = convert_to_algorithm_boxes(test_boxes, OptimizedBox)
    optimized_algo = OptimizedLayerPackingAlgorithm()
    
    start_time = time.time()
    optimized_result, optimized_util = optimized_algo.pack(optimized_boxes, container_dims)
    optimized_time = time.time() - start_time
    
    results['Optimized'] = {
        'boxes': len(optimized_result),
        'utilization': optimized_util,
        'time': optimized_time,
        'result': optimized_result
    }
    
    print(f"✅ Đặt được: {len(optimized_result)}/{len(optimized_boxes)} box ({len(optimized_result)/len(optimized_boxes)*100:.1f}%)")
    print(f"✅ Tỷ lệ sử dụng: {optimized_util:.2%}")
    print(f"✅ Thời gian: {optimized_time:.3f}s")
    
    analyze_packing_result(optimized_result, container_dims, "THUẬT TOÁN TỐI ƯU MỚI")
    
    # So sánh tổng kết
    print("\n" + "="*80)
    print("🏆 TỔNG KẾT SO SÁNH")
    print("="*80)
    
    print(f"{'Thuật toán':<20} {'Box đặt':<10} {'Tỷ lệ sử dụng':<15} {'Thời gian':<10}")
    print("-" * 60)
    
    for name, result in results.items():
        print(f"{name:<20} {result['boxes']:<10} {result['utilization']:<15.2%} {result['time']:<10.3f}s")
    
    # Tìm thuật toán tốt nhất
    best_algo = max(results.items(), key=lambda x: (x[1]['boxes'], x[1]['utilization']))
    print(f"\n🥇 Thuật toán tốt nhất: {best_algo[0]}")
    print(f"   → Đặt được {best_algo[1]['boxes']} box với tỷ lệ sử dụng {best_algo[1]['utilization']:.2%}")
    
    # Đánh giá thực hiện chiến lược
    print(f"\n📋 ĐÁNH GIÁ THỰC HIỆN CHIẾN LƯỢC:")
    
    if optimized_util >= max(old_util, enhanced_util):
        print("✅ Thuật toán tối ưu mới có hiệu suất tốt nhất")
    else:
        print("⚠️ Thuật toán tối ưu mới chưa đạt hiệu suất cao nhất")
    
    print("\n🎯 KHUYẾN NGHỊ:")
    if optimized_util > old_util * 1.1:  # Cải thiện > 10%
        print("✅ Thuật toán mới thực hiện tốt chiến lược đã đề ra")
        print("✅ Nên sử dụng thuật toán mới cho production")
    elif optimized_util > old_util:
        print("⚠️ Thuật toán mới có cải thiện nhưng chưa đáng kể")
        print("⚠️ Cần tiếp tục tối ưu hóa")
    else:
        print("❌ Thuật toán mới chưa hiệu quả hơn thuật toán cũ")
        print("❌ Cần xem xét lại implementation")

if __name__ == "__main__":
    test_all_algorithms()