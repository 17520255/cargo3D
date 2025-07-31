import pandas as pd
import time
from algorithms.enhanced_packing_algorithm import Box, EnhancedPackingAlgorithm

def test_configuration(goods, container_dimensions, support_threshold, time_limit, respect_groups=True):
    """Kiểm tra một cấu hình cụ thể và trả về kết quả"""
    print(f"\n=== Kiểm tra cấu hình: support_threshold={support_threshold}, time_limit={time_limit}s, respect_groups={respect_groups} ===")
    
    start_time = time.time()
    
    # Khởi tạo thuật toán với ngưỡng hỗ trợ cụ thể
    algo = EnhancedPackingAlgorithm()
    algo.support_threshold = support_threshold
    
    # Chạy thuật toán
    placed_boxes, utilization = algo.optimize_packing(
        goods, 
        container_dimensions,
        respect_groups=respect_groups,
        time_limit=time_limit
    )
    
    execution_time = time.time() - start_time
    
    # Kiểm tra va chạm và vượt biên
    collision_count = 0
    out_of_bounds_count = 0
    
    # Tạo hàm kiểm tra va chạm
    def check_collision(box1, box2):
        return (
            box1.position['x'] < box2.position['x'] + box2.width and
            box1.position['x'] + box1.width > box2.position['x'] and
            box1.position['y'] < box2.position['y'] + box2.height and
            box1.position['y'] + box1.height > box2.position['y'] and
            box1.position['z'] < box2.position['z'] + box2.depth and
            box1.position['z'] + box1.depth > box2.position['z']
        )
    
    # Kiểm tra va chạm giữa các box
    for i, box1 in enumerate(placed_boxes):
        # Kiểm tra vượt biên
        if (box1.position['x'] < 0 or
            box1.position['y'] < 0 or
            box1.position['z'] < 0 or
            box1.position['x'] + box1.width > container_dimensions['width'] or
            box1.position['y'] + box1.height > container_dimensions['height'] or
            box1.position['z'] + box1.depth > container_dimensions['depth']):
            out_of_bounds_count += 1
        
        # Kiểm tra va chạm
        for j, box2 in enumerate(placed_boxes):
            if i != j and check_collision(box1, box2):
                collision_count += 1
                break
    
    # Kiểm tra box lơ lửng
    floating_count = 0
    from algorithms.enhanced_packing_algorithm import Container
    test_container = Container(**container_dimensions)
    for box in placed_boxes:
        test_container.place_box(box, box.position['x'], box.position['y'], box.position['z'])
    
    for box in placed_boxes:
        if box.position['y'] > 1e-3:  # Box không nằm trên mặt đất
            if not test_container.has_support(box, box.position['x'], box.position['y'], box.position['z'], support_threshold):
                floating_count += 1
    
    # In kết quả
    print(f"Thời gian thực thi: {execution_time:.2f} giây")
    print(f"Đã đặt được {len(placed_boxes)}/{len(goods)} box ({len(placed_boxes)/len(goods)*100:.1f}%)")
    print(f"Tỷ lệ sử dụng không gian: {utilization:.2%}")
    print(f"Kiểm tra va chạm: {'❌ Có' if collision_count > 0 else '✅ Không'} ({collision_count} va chạm)")
    print(f"Kiểm tra vượt biên: {'❌ Có' if out_of_bounds_count > 0 else '✅ Không'} ({out_of_bounds_count} vượt biên)")
    print(f"Kiểm tra box lơ lửng: {'❌ Có' if floating_count > 0 else '✅ Không'} ({floating_count} box lơ lửng)")
    
    return {
        'support_threshold': support_threshold,
        'time_limit': time_limit,
        'respect_groups': respect_groups,
        'execution_time': execution_time,
        'placed_boxes': len(placed_boxes),
        'total_boxes': len(goods),
        'utilization': utilization,
        'collisions': collision_count,
        'out_of_bounds': out_of_bounds_count,
        'floating': floating_count,
        'valid': collision_count == 0 and out_of_bounds_count == 0 and floating_count == 0,
        'target_achieved': utilization >= 0.8  # Mục tiêu 80%
    }

def main():
    print("\n===== KIỂM TRA TỶ LỆ SỬ DỤNG KHÔNG GIAN =====")
    
    # Đọc dữ liệu từ Excel
    print('\nĐọc dữ liệu từ file Excel...')
    try:
        df = pd.read_excel('demotest.xlsx')
        print(f'Đọc được {len(df)} dòng dữ liệu từ Excel')
    except Exception as e:
        print(f'Lỗi khi đọc file Excel: {str(e)}')
        return
    
    # Tạo danh sách hàng hóa
    print('\nTạo danh sách hàng hóa...')
    goods = []
    for i, row in df.iterrows():
        for j in range(int(row['quantity'])):
            box = Box(
                id=f"{row['name']}-{j+1}",
                width=row['width'],
                height=row['height'],
                depth=row['depth'],
                weight=row['weight'],
                name=row['name'],
                label=row['group']
            )
            goods.append(box)
    
    print(f'Đã tạo {len(goods)} kiện hàng từ {len(df)} loại')
    
    # Thông tin container
    container_dimensions = {
        "width": 2340,
        "height": 2694,
        "depth": 12117
    }
    
    container_volume = container_dimensions["width"] * container_dimensions["height"] * container_dimensions["depth"]
    total_box_volume = sum(box.volume for box in goods)
    min_utilization = total_box_volume / container_volume
    
    print('\nThông tin container:')
    print(f'Kích thước: {container_dimensions["width"]}×{container_dimensions["height"]}×{container_dimensions["depth"]} mm')
    print(f'Thể tích: {container_volume:,.0f} mm³')
    print(f'Tỷ lệ sử dụng tối thiểu cần thiết: {min_utilization:.2%}')
    print(f'Mục tiêu tỷ lệ sử dụng: 80%')
    
    # Các cấu hình cần kiểm tra
    configs = [
        # support_threshold, time_limit, respect_groups
        (0.6, 60, True),
        (0.7, 60, True),
        (0.7, 90, True),
        (0.7, 120, True),
        (0.8, 60, True),
        (0.7, 90, False),  # Không tôn trọng nhóm
        (0.65, 120, True)  # Thử ngưỡng hỗ trợ trung gian
    ]
    
    results = []
    
    # Chạy kiểm tra với các cấu hình khác nhau
    for support_threshold, time_limit, respect_groups in configs:
        result = test_configuration(
            goods.copy(),  # Tạo bản sao để tránh ảnh hưởng giữa các lần chạy
            container_dimensions,
            support_threshold,
            time_limit,
            respect_groups
        )
        results.append(result)
    
    # Tìm cấu hình tốt nhất
    valid_results = [r for r in results if r['valid']]
    if valid_results:
        # Sắp xếp theo tỷ lệ sử dụng giảm dần
        best_configs = sorted(valid_results, key=lambda x: x['utilization'], reverse=True)
        best = best_configs[0]
        
        print("\n===== CẤU HÌNH TỐT NHẤT =====")
        print(f"Support threshold: {best['support_threshold']}")
        print(f"Time limit: {best['time_limit']}s")
        print(f"Respect groups: {best['respect_groups']}")
        print(f"Tỷ lệ sử dụng: {best['utilization']:.2%}")
        print(f"Thời gian thực thi: {best['execution_time']:.2f}s")
        print(f"Đã đặt được: {best['placed_boxes']}/{best['total_boxes']} box")
        print(f"Mục tiêu 80%: {'✅ ĐẠT' if best['target_achieved'] else '❌ CHƯA ĐẠT'}")
    else:
        print("\n❌ Không tìm thấy cấu hình hợp lệ (không va chạm, không vượt biên, không box lơ lửng)")
    
    # In tổng kết
    print("\n===== TỔNG KẾT =====")
    print(f"{'Support':<8} {'Time':<5} {'Groups':<8} {'Util':<8} {'Boxes':<10} {'Valid':<6} {'Target':<6}")
    print("-" * 60)
    for r in results:
        print(f"{r['support_threshold']:<8.2f} {r['time_limit']:<5d} {str(r['respect_groups']):<8s} {r['utilization']:<8.2%} {r['placed_boxes']}/{r['total_boxes']:<6} {'✓' if r['valid'] else '✗':<6} {'✓' if r['target_achieved'] else '✗':<6}")

if __name__ == "__main__":
    main() 