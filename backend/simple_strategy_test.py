#!/usr/bin/env python3
"""
Test đơn giản để đánh giá thuật toán theo 4 chiến lược:
1. Lấp đầy trục x (chiều rộng) tối ưu
2. Lấp đầy chiều cao (y)  
3. Lấp đầy từ trong ra ngoài (từ z=0 ra cửa)
4. Tối ưu hoá theo "khối"
"""

import time
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.packing_algorithm import PackingAlgorithm, Box as OldBox
from algorithms.optimized_layer_packing import OptimizedLayerPackingAlgorithm, Box as OptimizedBox

def create_simple_test_data():
    """Tạo dữ liệu test đơn giản để kiểm tra chiến lược"""
    
    # Test case: Box có thể kết hợp lấp đầy chiều rộng container (2340mm)
    test_boxes = [
        # Nhóm A: 3 box 780x500x600 = 2340x500x600 (lấp đầy chính xác chiều rộng)
        ("A1", 780, 500, 600, "Box A1", "A", 10),
        ("A2", 780, 500, 600, "Box A2", "A", 10),
        ("A3", 780, 500, 600, "Box A3", "A", 10),
        
        # Nhóm B: 2 box 1170x400x500 = 2340x400x500 (lấp đầy chính xác chiều rộng)
        ("B1", 1170, 400, 500, "Box B1", "B", 8),
        ("B2", 1170, 400, 500, "Box B2", "B", 8),
        
        # Nhóm C: 4 box 585x300x400 = 2340x300x400 (lấp đầy chính xác chiều rộng)
        ("C1", 585, 300, 400, "Box C1", "C", 6),
        ("C2", 585, 300, 400, "Box C2", "C", 6),
        ("C3", 585, 300, 400, "Box C3", "C", 6),
        ("C4", 585, 300, 400, "Box C4", "C", 6),
    ]
    
    return test_boxes

def analyze_width_filling_strategy(boxes, container_width):
    """Phân tích chiến lược lấp đầy trục x"""
    print("1️⃣ PHÂN TÍCH CHIẾN LƯỢC LẤP ĐẦY TRỤC X:")
    
    # Nhóm box theo z và y để phân tích từng hàng
    rows = defaultdict(list)
    for box in boxes:
        row_key = (round(box.position['z'], 1), round(box.position['y'], 1))
        rows[row_key].append(box)
    
    perfect_rows = 0
    good_rows = 0
    total_rows = len(rows)
    
    for (z, y), row_boxes in rows.items():
        # Sắp xếp theo x
        row_boxes.sort(key=lambda b: b.position['x'])
        
        # Tính tổng chiều rộng của hàng
        total_row_width = sum(box.width for box in row_boxes)
        width_efficiency = total_row_width / container_width
        
        print(f"  Hàng (z={z}, y={y}): {len(row_boxes)} box, "
              f"rộng {total_row_width:.0f}/{container_width:.0f}mm ({width_efficiency:.1%})")
        
        # Kiểm tra khoảng trống
        if width_efficiency >= 0.99:  # >= 99%
            perfect_rows += 1
            print("    ✅ Lấp đầy hoàn hảo!")
        elif width_efficiency >= 0.85:  # >= 85%
            good_rows += 1
            print("    ✅ Lấp đầy tốt")
        else:
            print("    ❌ Lấp đầy kém")
        
        # Kiểm tra các box có liền kề không
        gaps = []
        for i in range(len(row_boxes) - 1):
            gap = row_boxes[i+1].position['x'] - (row_boxes[i].position['x'] + row_boxes[i].width)
            gaps.append(gap)
        
        if gaps and max(gaps) > 1:
            print(f"    ⚠️ Có khoảng trống lớn nhất: {max(gaps):.1f}mm")
    
    print(f"  📊 Tổng kết: {perfect_rows} hàng hoàn hảo, {good_rows} hàng tốt / {total_rows} hàng")
    return perfect_rows, good_rows, total_rows

def analyze_height_filling_strategy(boxes, container_height):
    """Phân tích chiến lược lấp đầy chiều cao"""
    print("\n2️⃣ PHÂN TÍCH CHIẾN LƯỢC LẤP ĐẦY CHIỀU CAO:")
    
    # Nhóm box theo z để phân tích từng lớp
    layers = defaultdict(list)
    for box in boxes:
        layer_key = round(box.position['z'], 1)
        layers[layer_key].append(box)
    
    stacking_layers = 0
    total_layers = len(layers)
    
    for z, layer_boxes in sorted(layers.items()):
        # Tính chiều cao sử dụng của lớp
        max_y = max(box.position['y'] + box.height for box in layer_boxes)
        height_efficiency = max_y / container_height
        
        print(f"  Lớp z={z}: {len(layer_boxes)} box, "
              f"cao {max_y:.0f}/{container_height:.0f}mm ({height_efficiency:.1%})")
        
        # Phân tích stacking - tìm các box chồng lên nhau
        stacks = defaultdict(list)
        for box in layer_boxes:
            stack_key = (round(box.position['x'], 1), round(box.position['z'], 1))
            stacks[stack_key].append(box)
        
        stacked_columns = sum(1 for stack in stacks.values() if len(stack) > 1)
        total_columns = len(stacks)
        
        if stacked_columns > 0:
            stacking_layers += 1
            print(f"    ✅ Có chồng: {stacked_columns}/{total_columns} cột")
        else:
            print(f"    ❌ Không có chồng: 0/{total_columns} cột")
    
    print(f"  📊 Tổng kết: {stacking_layers}/{total_layers} lớp có chồng box")
    return stacking_layers, total_layers

def analyze_depth_filling_strategy(boxes, container_depth):
    """Phân tích chiến lược lấp đầy từ trong ra ngoài"""
    print("\n3️⃣ PHÂN TÍCH CHIẾN LƯỢC LẤP ĐẦY TỪ TRONG RA NGOÀI:")
    
    # Sắp xếp box theo z
    sorted_by_z = sorted(boxes, key=lambda b: b.position['z'])
    
    # Kiểm tra có bắt đầu từ z=0 không
    min_z = min(box.position['z'] for box in boxes)
    starts_from_zero = min_z < 50  # Cho phép sai số 50mm
    
    print(f"  Vị trí z nhỏ nhất: {min_z:.1f}mm")
    print(f"  ✅ Bắt đầu từ z≈0: {'Có' if starts_from_zero else 'Không'}")
    
    # Tính độ đầy theo z
    max_z = max(box.position['z'] + box.depth for box in boxes)
    z_efficiency = max_z / container_depth
    print(f"  📈 Sử dụng độ sâu: {max_z:.0f}/{container_depth:.0f}mm ({z_efficiency:.1%})")
    
    # Kiểm tra thứ tự z có hợp lý không
    z_positions = sorted(set(box.position['z'] for box in boxes))
    print(f"  Số lớp z: {len(z_positions)}")
    
    if len(z_positions) <= 3:
        print(f"  Vị trí z: {[f'{z:.0f}' for z in z_positions]}")
    else:
        print(f"  Vị trí z: {[f'{z:.0f}' for z in z_positions[:3]]}... (+{len(z_positions)-3} lớp)")
    
    return starts_from_zero, z_efficiency

def analyze_block_optimization_strategy(boxes):
    """Phân tích chiến lược tối ưu hóa theo khối"""
    print("\n4️⃣ PHÂN TÍCH CHIẾN LƯỢC TỐI ƯU HÓA THEO KHỐI:")
    
    # Nhóm box theo label
    groups = defaultdict(list)
    for box in boxes:
        groups[box.label].append(box)
    
    compact_groups = 0
    total_groups = len(groups)
    
    for label, group_boxes in groups.items():
        if len(group_boxes) <= 1:
            print(f"  Nhóm {label}: {len(group_boxes)} box (bỏ qua)")
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
        max_distance = max(distances)
        
        print(f"    → Khoảng cách trung bình từ tâm: {avg_distance:.1f}mm")
        print(f"    → Khoảng cách xa nhất: {max_distance:.1f}mm")
        
        # Đánh giá mức độ gần nhau
        if max_distance < 1000:  # < 1m
            compact_groups += 1
            print(f"    ✅ Tạo thành khối compact")
        elif max_distance < 2000:  # < 2m
            print(f"    ⚠️ Tạo thành khối trung bình")
        else:
            print(f"    ❌ Box bị phân tán")
    
    print(f"  📊 Tổng kết: {compact_groups}/{total_groups} nhóm tạo thành khối compact")
    return compact_groups, total_groups

def test_strategy_implementation():
    """Test implementation của 4 chiến lược"""
    print("🎯 KIỂM TRA THỰC HIỆN 4 CHIẾN LƯỢC ĐÓNG GÓI")
    print("=" * 80)
    
    # Tạo dữ liệu test
    test_boxes = create_simple_test_data()
    container_dims = {"width": 2340, "height": 2694, "depth": 12117}
    
    print(f"📦 Dữ liệu test: {len(test_boxes)} box")
    print(f"📏 Container: {container_dims['width']} x {container_dims['height']} x {container_dims['depth']}")
    
    # Hiển thị thiết kế test
    print("\n📋 THIẾT KẾ TEST:")
    print("- Nhóm A: 3 box 780x500x600 → tổng 2340x500x600 (lấp đầy chính xác chiều rộng)")
    print("- Nhóm B: 2 box 1170x400x500 → tổng 2340x400x500 (lấp đầy chính xác chiều rộng)")
    print("- Nhóm C: 4 box 585x300x400 → tổng 2340x300x400 (lấp đầy chính xác chiều rộng)")
    
    results = {}
    
    # Test thuật toán cũ
    print("\n" + "="*80)
    print("🔧 TEST THUẬT TOÁN CŨ (BEST FIT)")
    print("="*80)
    
    old_boxes = [OldBox(b[0], b[1], b[2], b[3], b[4], b[5], b[6]) for b in test_boxes]
    old_algo = PackingAlgorithm()
    old_algo.set_algorithm("best_fit")
    
    start_time = time.time()
    old_result, old_util = old_algo.pack(old_boxes, container_dims)
    old_time = time.time() - start_time
    
    print(f"✅ Đặt được: {len(old_result)}/{len(old_boxes)} box ({len(old_result)/len(old_boxes)*100:.1f}%)")
    print(f"✅ Tỷ lệ sử dụng: {old_util:.2%}")
    print(f"✅ Thời gian: {old_time:.3f}s")
    
    # Phân tích chiến lược thuật toán cũ
    if old_result:
        print(f"\n📊 PHÂN TÍCH CHIẾN LƯỢC - THUẬT TOÁN CŨ")
        print("-" * 60)
        
        old_perfect_rows, old_good_rows, old_total_rows = analyze_width_filling_strategy(old_result, container_dims['width'])
        old_stacking_layers, old_total_layers = analyze_height_filling_strategy(old_result, container_dims['height'])
        old_starts_from_zero, old_z_efficiency = analyze_depth_filling_strategy(old_result, container_dims['depth'])
        old_compact_groups, old_total_groups = analyze_block_optimization_strategy(old_result)
        
        results['old'] = {
            'boxes': len(old_result),
            'utilization': old_util,
            'time': old_time,
            'width_perfect': old_perfect_rows / old_total_rows if old_total_rows > 0 else 0,
            'height_stacking': old_stacking_layers / old_total_layers if old_total_layers > 0 else 0,
            'depth_from_zero': old_starts_from_zero,
            'block_compact': old_compact_groups / old_total_groups if old_total_groups > 0 else 0
        }
    
    # Test thuật toán mới
    print("\n" + "="*80)
    print("🔧 TEST THUẬT TOÁN MỚI (OPTIMIZED LAYER)")
    print("="*80)
    
    optimized_boxes = [OptimizedBox(b[0], b[1], b[2], b[3], b[4], b[5], b[6]) for b in test_boxes]
    optimized_algo = OptimizedLayerPackingAlgorithm()
    
    start_time = time.time()
    optimized_result, optimized_util = optimized_algo.pack(optimized_boxes, container_dims)
    optimized_time = time.time() - start_time
    
    print(f"✅ Đặt được: {len(optimized_result)}/{len(optimized_boxes)} box ({len(optimized_result)/len(optimized_boxes)*100:.1f}%)")
    print(f"✅ Tỷ lệ sử dụng: {optimized_util:.2%}")
    print(f"✅ Thời gian: {optimized_time:.3f}s")
    
    # Phân tích chiến lược thuật toán mới
    if optimized_result:
        print(f"\n📊 PHÂN TÍCH CHIẾN LƯỢC - THUẬT TOÁN MỚI")
        print("-" * 60)
        
        opt_perfect_rows, opt_good_rows, opt_total_rows = analyze_width_filling_strategy(optimized_result, container_dims['width'])
        opt_stacking_layers, opt_total_layers = analyze_height_filling_strategy(optimized_result, container_dims['height'])
        opt_starts_from_zero, opt_z_efficiency = analyze_depth_filling_strategy(optimized_result, container_dims['depth'])
        opt_compact_groups, opt_total_groups = analyze_block_optimization_strategy(optimized_result)
        
        results['optimized'] = {
            'boxes': len(optimized_result),
            'utilization': optimized_util,
            'time': optimized_time,
            'width_perfect': opt_perfect_rows / opt_total_rows if opt_total_rows > 0 else 0,
            'height_stacking': opt_stacking_layers / opt_total_layers if opt_total_layers > 0 else 0,
            'depth_from_zero': opt_starts_from_zero,
            'block_compact': opt_compact_groups / opt_total_groups if opt_total_groups > 0 else 0
        }
    
    # So sánh và kết luận
    print("\n" + "="*80)
    print("🏆 SO SÁNH VÀ KẾT LUẬN")
    print("="*80)
    
    if 'old' in results and 'optimized' in results:
        old = results['old']
        opt = results['optimized']
        
        print(f"{'Tiêu chí':<25} {'Thuật toán cũ':<15} {'Thuật toán mới':<15} {'Kết luận'}")
        print("-" * 70)
        print(f"{'Số box đặt được':<25} {old['boxes']:<15} {opt['boxes']:<15} {'🥇 Mới' if opt['boxes'] > old['boxes'] else '🥇 Cũ' if old['boxes'] > opt['boxes'] else '🤝 Hòa'}")
        print(f"{'Tỷ lệ sử dụng':<25} {old['utilization']:<15.1%} {opt['utilization']:<15.1%} {'🥇 Mới' if opt['utilization'] > old['utilization'] else '🥇 Cũ' if old['utilization'] > opt['utilization'] else '🤝 Hòa'}")
        print(f"{'Lấp đầy chiều rộng':<25} {old['width_perfect']:<15.1%} {opt['width_perfect']:<15.1%} {'🥇 Mới' if opt['width_perfect'] > old['width_perfect'] else '🥇 Cũ' if old['width_perfect'] > opt['width_perfect'] else '🤝 Hòa'}")
        print(f"{'Chồng theo chiều cao':<25} {old['height_stacking']:<15.1%} {opt['height_stacking']:<15.1%} {'🥇 Mới' if opt['height_stacking'] > old['height_stacking'] else '🥇 Cũ' if old['height_stacking'] > opt['height_stacking'] else '🤝 Hòa'}")
        print(f"{'Bắt đầu từ z=0':<25} {'✅' if old['depth_from_zero'] else '❌':<15} {'✅' if opt['depth_from_zero'] else '❌':<15} {'🥇 Mới' if opt['depth_from_zero'] and not old['depth_from_zero'] else '🥇 Cũ' if old['depth_from_zero'] and not opt['depth_from_zero'] else '🤝 Hòa'}")
        print(f"{'Tạo khối compact':<25} {old['block_compact']:<15.1%} {opt['block_compact']:<15.1%} {'🥇 Mới' if opt['block_compact'] > old['block_compact'] else '🥇 Cũ' if old['block_compact'] > opt['block_compact'] else '🤝 Hòa'}")
        
        # Tính điểm tổng thể
        old_score = (old['width_perfect'] + old['height_stacking'] + 
                    (1 if old['depth_from_zero'] else 0) + old['block_compact'])
        opt_score = (opt['width_perfect'] + opt['height_stacking'] + 
                    (1 if opt['depth_from_zero'] else 0) + opt['block_compact'])
        
        print(f"\n📊 ĐIỂM TỔNG THỂ CHIẾN LƯỢC:")
        print(f"Thuật toán cũ: {old_score:.2f}/4.0")
        print(f"Thuật toán mới: {opt_score:.2f}/4.0")
        
        print(f"\n🎯 KẾT LUẬN:")
        if opt_score > old_score:
            print("✅ Thuật toán mới thực hiện tốt hơn 4 chiến lược đã đề ra")
            print("✅ Khuyến nghị: Sử dụng thuật toán mới")
        elif opt_score == old_score:
            print("⚠️ Thuật toán mới thực hiện tương đương thuật toán cũ")
            print("⚠️ Khuyến nghị: Tiếp tục tối ưu hóa")
        else:
            print("❌ Thuật toán mới chưa thực hiện tốt hơn thuật toán cũ")
            print("❌ Khuyến nghị: Cần cải thiện implementation")

if __name__ == "__main__":
    test_strategy_implementation()