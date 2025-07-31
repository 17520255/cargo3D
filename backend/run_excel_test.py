import pandas as pd # type: ignore
import time
from algorithms.enhanced_packing_algorithm import Box, EnhancedPackingAlgorithm

def main():
    print("\n===== KIỂM TRA THUẬT TOÁN ĐÓNG GÓI NÂNG CAO =====")
    
    # Đọc dữ liệu từ Excel
    print('\nĐọc dữ liệu từ file Excel...')
    try:
        df = pd.read_excel('backend/demotest.xlsx')
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
    
    # In thông tin chi tiết về các kiện hàng
    print('\nThông tin chi tiết về các kiện hàng:')
    print(f'{"ID":<15} {"Kích thước (W×H×D)":<25} {"Thể tích":<15} {"Nhóm":<10}')
    print('-' * 65)
    for box in goods[:10]:  # Chỉ hiển thị 10 box đầu tiên
        print(f'{box.id:<15} {box.width:.1f}×{box.height:.1f}×{box.depth:.1f} mm{"":<10} {box.volume:.1f} mm³{"":<5} {box.label:<10}')
    if len(goods) > 10:
        print(f'... và {len(goods) - 10} kiện hàng khác')
    
    # Tính tổng thể tích
    total_box_volume = sum(box.volume for box in goods)
    print(f'\nTổng số kiện hàng: {len(goods)}')
    print(f'Tổng thể tích hàng hóa: {total_box_volume:,.0f} mm³')
    
    # Thông tin container
    container_dimensions = {
        "width": 2340,
        "height": 2694,
        "depth": 12117
    }
    
    container_volume = container_dimensions["width"] * container_dimensions["height"] * container_dimensions["depth"]
    min_utilization = total_box_volume / container_volume
    
    print('\nThông tin container:')
    print(f'Kích thước: {container_dimensions["width"]}×{container_dimensions["height"]}×{container_dimensions["depth"]} mm')
    print(f'Thể tích: {container_volume:,.0f} mm³')
    print(f'Tỷ lệ sử dụng tối thiểu cần thiết: {min_utilization:.2%}')
    
    # Chạy thuật toán đóng gói
    print('\nKhởi tạo và chạy thuật toán đóng gói nâng cao...')
    start_time = time.time()
    
    algo = EnhancedPackingAlgorithm()
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
    
    # In thông tin chi tiết về các box đã đặt
    print('\nThông tin chi tiết về các box đã đặt:')
    print(f'{"ID":<15} {"Kích thước (W×H×D)":<25} {"Vị trí (X,Y,Z)":<25} {"Nhóm":<10}')
    print('-' * 75)
    for box in placed_boxes[:20]:  # Chỉ hiển thị 20 box đầu tiên
        pos = box.position
        print(f'{box.id:<15} {box.width:.1f}×{box.height:.1f}×{box.depth:.1f} mm{"":<5} ({pos["x"]:.1f}, {pos["y"]:.1f}, {pos["z"]:.1f}){"":<5} {box.label:<10}')
    if len(placed_boxes) > 20:
        print(f'... và {len(placed_boxes) - 20} box khác')
    
    # Thống kê theo nhóm
    print('\nThống kê theo nhóm:')
    groups = {}
    for box in placed_boxes:
        if box.label not in groups:
            groups[box.label] = 0
        groups[box.label] += 1
    
    for group, count in groups.items():
        total_in_group = sum(1 for box in goods if box.label == group)
        print(f'Nhóm {group}: {count}/{total_in_group} ({count/total_in_group*100:.1f}%)')
    
    # Liệt kê các box chưa đặt được
    unplaced_boxes = [box for box in goods if box.id not in [b.id for b in placed_boxes]]
    if unplaced_boxes:
        print(f'\nCó {len(unplaced_boxes)} box chưa đặt được:')
        groups_unplaced = {}
        for box in unplaced_boxes:
            if box.label not in groups_unplaced:
                groups_unplaced[box.label] = 0
            groups_unplaced[box.label] += 1
        
        for group, count in groups_unplaced.items():
            print(f'Nhóm {group}: {count} box')
    
    # Kiểm tra va chạm giữa các box
    print("\n⚠️ Kiểm tra va chạm giữa các box...")
    def check_collision(box1, box2):
        x_overlap = (box1.position['x'] < box2.position['x'] + box2.width and
                    box1.position['x'] + box1.width > box2.position['x'])
        y_overlap = (box1.position['y'] < box2.position['y'] + box2.height and
                    box1.position['y'] + box1.height > box2.position['y'])
        z_overlap = (box1.position['z'] < box2.position['z'] + box2.depth and
                    box1.position['z'] + box1.depth > box2.position['z'])
        return x_overlap and y_overlap and z_overlap
    
    collision_found = False
    collision_count = 0
    for i in range(len(placed_boxes)):
        for j in range(i+1, len(placed_boxes)):
            if check_collision(placed_boxes[i], placed_boxes[j]):
                collision_found = True
                collision_count += 1
                print(f"❌ Va chạm giữa box {placed_boxes[i].id} và {placed_boxes[j].id}")
                print(f"   Box 1: {placed_boxes[i].id} tại ({placed_boxes[i].position['x']}, {placed_boxes[i].position['y']}, {placed_boxes[i].position['z']}), kích thước: {placed_boxes[i].width}×{placed_boxes[i].height}×{placed_boxes[i].depth}")
                print(f"   Box 2: {placed_boxes[j].id} tại ({placed_boxes[j].position['x']}, {placed_boxes[j].position['y']}, {placed_boxes[j].position['z']}), kích thước: {placed_boxes[j].width}×{placed_boxes[j].height}×{placed_boxes[j].depth}")
    
    if collision_found:
        print(f"\n❌ Phát hiện {collision_count} va chạm giữa các box!")
    else:
        print("✅ Không phát hiện va chạm giữa các box!")
    
    # Kiểm tra box nằm ngoài container
    print("\n⚠️ Kiểm tra box nằm ngoài container...")
    outside_container = False
    outside_count = 0
    for box in placed_boxes:
        if (box.position['x'] < 0 or 
            box.position['y'] < 0 or 
            box.position['z'] < 0 or
            box.position['x'] + box.width > container_dimensions['width'] or
            box.position['y'] + box.height > container_dimensions['height'] or
            box.position['z'] + box.depth > container_dimensions['depth']):
            outside_container = True
            outside_count += 1
            print(f"❌ Box {box.id} nằm ngoài container:")
            print(f"   Vị trí: ({box.position['x']}, {box.position['y']}, {box.position['z']}), kích thước: {box.width}×{box.height}×{box.depth}")
            print(f"   Container: {container_dimensions['width']}×{container_dimensions['height']}×{container_dimensions['depth']}")
    
    if outside_container:
        print(f"\n❌ Phát hiện {outside_count} box nằm ngoài container!")
    else:
        print("✅ Không phát hiện box nằm ngoài container!")
    
    # Kiểm tra tính ổn định (box lơ lửng)
    print("\n⚠️ Kiểm tra box lơ lửng...")
    floating_count = 0
    
    # Tạo container để kiểm tra
    from algorithms.enhanced_packing_algorithm import Container
    test_container = Container(**container_dimensions)
    for box in placed_boxes:
        test_container.place_box(box, box.position['x'], box.position['y'], box.position['z'])
    
    for box in placed_boxes:
        if box.position['y'] > 1e-3:  # Box không nằm trên mặt đất
            if not test_container.has_support(box, box.position['x'], box.position['y'], box.position['z']):
                floating_count += 1
                print(f"❌ Box {box.id} bị lơ lửng:")
                print(f"   Vị trí: ({box.position['x']}, {box.position['y']}, {box.position['z']}), kích thước: {box.width}×{box.height}×{box.depth}")
    
    if floating_count > 0:
        print(f"\n❌ Phát hiện {floating_count} box bị lơ lửng!")
    else:
        print("✅ Không phát hiện box lơ lửng!")

if __name__ == "__main__":
    main() 