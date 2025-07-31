import pandas as pd
import time
from algorithms.enhanced_packing_algorithm import Box, EnhancedPackingAlgorithm
import numpy as np
from collections import defaultdict

def check_group_packing():
    print("\n===== KIỂM TRA ĐÓNG GÓI THEO NHÓM =====")
    
    # Đọc dữ liệu từ Excel
    print('\nĐọc dữ liệu từ file Excel...')
    df = pd.read_excel('demotest.xlsx')
    print(f'Đọc được {len(df)} dòng dữ liệu từ Excel')
    
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
    
    # Thống kê số lượng box theo nhóm
    group_counts = defaultdict(int)
    for box in goods:
        group_counts[box.label] += 1
    
    print("\nSố lượng box theo nhóm:")
    for group, count in group_counts.items():
        print(f"Nhóm {group}: {count} box")
    
    # Thông tin container
    container_dimensions = {
        "width": 2340,
        "height": 2694,
        "depth": 12117
    }
    
    # Chạy thuật toán đóng gói với respect_groups=True
    print('\nChạy thuật toán với respect_groups=True...')
    start_time = time.time()
    
    algo = EnhancedPackingAlgorithm()
    algo.support_threshold = 0.7  # Sử dụng ngưỡng hỗ trợ tối ưu
    
    placed_boxes, utilization = algo.optimize_packing(
        goods, 
        container_dimensions,
        respect_groups=True,
        time_limit=60
    )
    
    execution_time = time.time() - start_time
    print(f'Thời gian thực thi: {execution_time:.2f} giây')
    print(f'Đã đặt được {len(placed_boxes)}/{len(goods)} box ({len(placed_boxes)/len(goods)*100:.1f}%)')
    print(f'Tỷ lệ sử dụng không gian: {utilization:.2%}')
    
    # Phân tích kết quả theo nhóm
    placed_by_group = defaultdict(list)
    for box in placed_boxes:
        placed_by_group[box.label].append(box)
    
    print("\nSố lượng box đặt được theo nhóm:")
    for group, boxes in placed_by_group.items():
        print(f"Nhóm {group}: {len(boxes)}/{group_counts[group]} box ({len(boxes)/group_counts[group]*100:.1f}%)")
    
    # Phân tích tính gần nhau của các box cùng nhóm
    print("\nPhân tích tính gần nhau của các box cùng nhóm:")
    for group, boxes in placed_by_group.items():
        if len(boxes) <= 1:
            continue
        
        # Tính khoảng cách trung bình giữa các box cùng nhóm
        distances = []
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                box1, box2 = boxes[i], boxes[j]
                distance = np.sqrt(
                    (box1.position['x'] - box2.position['x'])**2 +
                    (box1.position['y'] - box2.position['y'])**2 +
                    (box1.position['z'] - box2.position['z'])**2
                )
                distances.append(distance)
        
        avg_distance = sum(distances) / len(distances) if distances else 0
        max_distance = max(distances) if distances else 0
        
        # Tính tâm của nhóm
        center_x = sum(box.position['x'] + box.width/2 for box in boxes) / len(boxes)
        center_y = sum(box.position['y'] + box.height/2 for box in boxes) / len(boxes)
        center_z = sum(box.position['z'] + box.depth/2 for box in boxes) / len(boxes)
        
        # Tính độ phân tán (khoảng cách trung bình từ tâm)
        dispersion = sum(
            np.sqrt(
                (box.position['x'] + box.width/2 - center_x)**2 +
                (box.position['y'] + box.height/2 - center_y)**2 +
                (box.position['z'] + box.depth/2 - center_z)**2
            ) for box in boxes
        ) / len(boxes)
        
        print(f"Nhóm {group} ({len(boxes)} box):")
        print(f"  - Khoảng cách trung bình giữa các box: {avg_distance:.1f} mm")
        print(f"  - Khoảng cách lớn nhất giữa các box: {max_distance:.1f} mm")
        print(f"  - Độ phân tán từ tâm: {dispersion:.1f} mm")
        
        # Kiểm tra xem các box có được đặt gần nhau không
        container_diagonal = np.sqrt(
            container_dimensions['width']**2 +
            container_dimensions['height']**2 +
            container_dimensions['depth']**2
        )
        
        dispersion_ratio = dispersion / container_diagonal
        print(f"  - Tỷ lệ phân tán: {dispersion_ratio:.2%}")
        
        if dispersion_ratio < 0.2:
            print("  ✅ Các box cùng nhóm được đặt gần nhau")
        elif dispersion_ratio < 0.4:
            print("  ⚠️ Các box cùng nhóm được đặt tương đối gần nhau")
        else:
            print("  ❌ Các box cùng nhóm bị phân tán")
    
    # Phân tích các box theo tầng (layer)
    print("\nPhân tích các box theo tầng (y):")
    from algorithms.enhanced_packing_algorithm import Container
    container = Container(**container_dimensions)
    for box in placed_boxes:
        container.place_box(box, box.position['x'], box.position['y'], box.position['z'])
    
    for i, layer in enumerate(container.layers):
        layer_boxes = container.get_layer_boxes(i)
        layer_groups = defaultdict(int)
        for box in layer_boxes:
            layer_groups[box.label] += 1
        
        print(f"Tầng {i+1} (y={layer['y']:.1f}, height={layer['height']:.1f}):")
        for group, count in layer_groups.items():
            print(f"  - Nhóm {group}: {count} box")
    
    # Kết luận
    print("\n===== KẾT LUẬN =====")
    all_groups_close = all(dispersion / np.sqrt(
        container_dimensions['width']**2 +
        container_dimensions['height']**2 +
        container_dimensions['depth']**2
    ) < 0.4 for group, boxes in placed_by_group.items() if len(boxes) > 1)
    
    if all_groups_close:
        print("✅ Các kiện hàng cùng loại được đặt gần nhau, không bị chia nhỏ ra khi sắp xếp")
    else:
        print("⚠️ Một số nhóm kiện hàng bị phân tán khi sắp xếp")

if __name__ == "__main__":
    check_group_packing() 