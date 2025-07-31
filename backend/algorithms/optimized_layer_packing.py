import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time
from itertools import combinations
from copy import deepcopy

@dataclass
class Box:
    id: str
    width: float
    height: float
    depth: float
    name: str
    label: str
    weight: float
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    placed: bool = False
    orientation: int = 0
    
    def __post_init__(self):
        self.volume = self.width * self.height * self.depth
        self.placed = False
        self.orientation = 0
    
    def get_orientations(self) -> List[Dict]:
        """Chỉ cho phép xoay quanh trục y để tối ưu chiều rộng"""
        orientations = []
        # Orientation 0: (width, height, depth) - gốc
        orientations.append({
            "width": self.width, "height": self.height, "depth": self.depth,
            "volume": self.volume, "orientation": 0
        })
        # Orientation 1: (depth, height, width) - xoay 90° quanh trục y
        orientations.append({
            "width": self.depth, "height": self.height, "depth": self.width,
            "volume": self.volume, "orientation": 1
        })
        return orientations
    
    def clone(self) -> 'Box':
        new_box = Box(self.id, self.width, self.height, self.depth,
                     self.name, self.label, self.weight)
        new_box.position = self.position.copy()
        new_box.rotation = self.rotation.copy()
        new_box.placed = self.placed
        new_box.orientation = self.orientation
        return new_box

@dataclass
class Block:
    """Khối được tạo từ nhiều box nhỏ"""
    boxes: List[Box]
    width: float
    height: float
    depth: float
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    
    def __post_init__(self):
        self.volume = self.width * self.height * self.depth

class Container:
    def __init__(self, width: float, height: float, depth: float):
        self.width = width
        self.height = height
        self.depth = depth
        self.volume = width * height * depth
        self.used_volume = 0
        self.boxes = []
        self.blocks = []  # Các khối đã tạo
        self.layers = []  # Các lớp theo z
        
    def can_place(self, box: Box, x: float, y: float, z: float) -> bool:
        """Kiểm tra có thể đặt box tại vị trí (x,y,z) không"""
        # Kiểm tra biên container
        if (x + box.width > self.width + 1e-6 or
            y + box.height > self.height + 1e-6 or
            z + box.depth > self.depth + 1e-6 or
            x < -1e-6 or y < -1e-6 or z < -1e-6):
            return False
        
        # Kiểm tra va chạm với các box đã đặt
        for other in self.boxes:
            if self._is_overlap(box, x, y, z, other):
                return False
        return True
    
    def _is_overlap(self, box: Box, x: float, y: float, z: float, other: Box) -> bool:
        """Kiểm tra va chạm giữa box và other"""
        return (
            x < other.position['x'] + other.width and x + box.width > other.position['x'] and
            y < other.position['y'] + other.height and y + box.height > other.position['y'] and
            z < other.position['z'] + other.depth and z + box.depth > other.position['z']
        )
    
    def place_box(self, box: Box, x: float, y: float, z: float) -> None:
        """Đặt box tại vị trí (x,y,z)"""
        box.position = {"x": x, "y": y, "z": z}
        box.placed = True
        self.boxes.append(box)
        self.used_volume += box.volume
    
    def get_utilization(self) -> float:
        return self.used_volume / self.volume if self.volume > 0 else 0

class OptimizedLayerPackingAlgorithm:
    """
    Thuật toán đóng gói tối ưu theo chiến lược:
    1. Lấp đầy trục x (chiều rộng) bằng cách kết hợp các box
    2. Lấp đầy chiều cao y bằng cách chồng các box
    3. Lấp đầy từ trong ra ngoài (z=0 ra cửa)
    4. Tạo thành các "khối" box để giảm khoảng trống
    """
    
    def __init__(self):
        self.tolerance = 1e-6
        self.max_width_combinations = 5  # Số lượng box tối đa để kết hợp theo chiều rộng
        
    def pack(self, goods: List[Box], container_dimensions: Dict) -> Tuple[List[Box], float]:
        """Hàm chính thực hiện đóng gói"""
        container = Container(**container_dimensions)
        placed_boxes = []
        
        # Sắp xếp hàng hóa theo thể tích giảm dần
        sorted_goods = sorted(goods, key=lambda x: -x.volume)
        
        # Nhóm hàng hóa theo label để tạo khối
        groups = self._group_boxes_by_label(sorted_goods)
        
        # Thực hiện đóng gói theo từng lớp z
        z = 0.0
        while z < container.depth and groups:
            layer_depth = self._pack_layer(container, groups, z)
            if layer_depth <= 0:
                break
            z += layer_depth
            
        # Thu thập tất cả box đã đặt
        for box in container.boxes:
            placed_boxes.append(box)
            
        return placed_boxes, container.get_utilization()
    
    def _group_boxes_by_label(self, boxes: List[Box]) -> Dict[str, List[Box]]:
        """Nhóm các box theo label"""
        groups = defaultdict(list)
        for box in boxes:
            groups[box.label].append(box)
        return dict(groups)
    
    def _pack_layer(self, container: Container, groups: Dict[str, List[Box]], z: float) -> float:
        """
        Đóng gói một lớp tại độ sâu z
        Trả về độ sâu của lớp đã đóng gói
        """
        max_layer_depth = 0.0
        y = 0.0
        
        while y < container.height:
            # Tìm chiều cao tối đa có thể đặt tại y
            available_height = container.height - y
            
            # Tạo một hàng (row) tại vị trí (y, z)
            row_height = self._pack_row(container, groups, y, z, available_height)
            
            if row_height <= 0:
                break
                
            y += row_height
            
            # Cập nhật độ sâu lớp dựa trên các box đã đặt
            for box in container.boxes:
                if abs(box.position['z'] - z) < self.tolerance:
                    max_layer_depth = max(max_layer_depth, box.depth)
        
        return max_layer_depth
    
    def _pack_row(self, container: Container, groups: Dict[str, List[Box]], 
                  y: float, z: float, available_height: float) -> float:
        """
        Đóng gói một hàng tại vị trí (y, z)
        Chiến lược 1: Lấp đầy trục x bằng cách kết hợp các box
        """
        x = 0.0
        row_height = 0.0
        
        while x < container.width:
            available_width = container.width - x
            
            # Tìm tổ hợp box tối ưu để lấp đầy chiều rộng
            best_combination = self._find_best_width_combination(
                groups, available_width, available_height, z, container.depth
            )
            
            if not best_combination:
                break
            
            # Đặt các box trong tổ hợp tốt nhất
            combination_height = self._place_box_combination(
                container, best_combination, x, y, z
            )
            
            if combination_height <= 0:
                break
                
            # Cập nhật vị trí x và chiều cao hàng
            combination_width = sum(box.width for box in best_combination)
            x += combination_width
            row_height = max(row_height, combination_height)
            
            # Xóa các box đã sử dụng khỏi groups
            self._remove_used_boxes(groups, best_combination)
        
        return row_height
    
    def _find_best_width_combination(self, groups: Dict[str, List[Box]], 
                                   available_width: float, available_height: float,
                                   z: float, available_depth: float) -> List[Box]:
        """
        Tìm tổ hợp box tối ưu để lấp đầy chiều rộng
        Ưu tiên: 1) Lấp đầy hoàn toàn chiều rộng, 2) Cùng nhóm, 3) Thể tích lớn
        """
        best_combination = []
        best_score = -1
        
        # Thu thập tất cả box có thể sử dụng
        available_boxes = []
        for group_label, boxes in groups.items():
            for box in boxes:
                if not box.placed:
                    # Thử cả 2 orientation
                    for orientation in box.get_orientations():
                        if (orientation['width'] <= available_width + self.tolerance and
                            orientation['height'] <= available_height + self.tolerance and
                            orientation['depth'] <= available_depth + self.tolerance):
                            
                            temp_box = box.clone()
                            temp_box.width = orientation['width']
                            temp_box.height = orientation['height'] 
                            temp_box.depth = orientation['depth']
                            temp_box.orientation = orientation['orientation']
                            available_boxes.append(temp_box)
        
        if not available_boxes:
            return []
        
        # Thử các tổ hợp từ 1 đến max_width_combinations box
        for combo_size in range(1, min(len(available_boxes) + 1, self.max_width_combinations + 1)):
            for combination in combinations(available_boxes, combo_size):
                # Kiểm tra tổng chiều rộng
                total_width = sum(box.width for box in combination)
                if total_width > available_width + self.tolerance:
                    continue
                
                # Kiểm tra chiều cao và độ sâu đồng nhất
                max_height = max(box.height for box in combination)
                max_depth = max(box.depth for box in combination)
                
                if (max_height > available_height + self.tolerance or
                    max_depth > available_depth + self.tolerance):
                    continue
                
                # Tính điểm cho tổ hợp này
                score = self._calculate_combination_score(
                    combination, available_width, total_width
                )
                
                if score > best_score:
                    best_score = score
                    best_combination = list(combination)
        
        return best_combination
    
    def _calculate_combination_score(self, combination: Tuple[Box, ...], 
                                   available_width: float, total_width: float) -> float:
        """Tính điểm cho một tổ hợp box"""
        score = 0
        
        # 1. Điểm cao nhất: Lấp đầy hoàn toàn chiều rộng
        width_utilization = total_width / available_width
        score += width_utilization * 1000
        
        # 2. Thưởng lớn nếu lấp đầy chính xác 100%
        if abs(total_width - available_width) < self.tolerance:
            score += 500
        
        # 3. Điểm cho box cùng nhóm
        labels = [box.label for box in combination]
        if len(set(labels)) == 1:  # Tất cả cùng nhóm
            score += 300
        
        # 4. Điểm cho thể tích lớn
        total_volume = sum(box.volume for box in combination)
        score += total_volume / 1000000  # Normalize
        
        # 5. Ưu tiên ít box hơn (tạo khối lớn)
        score += (self.max_width_combinations - len(combination)) * 50
        
        return score
    
    def _place_box_combination(self, container: Container, combination: List[Box],
                             x: float, y: float, z: float) -> float:
        """
        Đặt một tổ hợp box tại vị trí (x, y, z)
        Chiến lược 2: Lấp đầy chiều cao bằng cách chồng các box
        """
        if not combination:
            return 0
        
        current_x = x
        max_combination_height = 0
        
        # Đặt các box theo chiều ngang trước
        for box in combination:
            if not container.can_place(box, current_x, y, z):
                return 0
            
            # Đặt box tại vị trí hiện tại
            container.place_box(box, current_x, y, z)
            current_x += box.width
            max_combination_height = max(max_combination_height, box.height)
        
        return max_combination_height
    
    def _stack_same_type_boxes(self, container: Container, base_combination: List[Box],
                              x: float, y: float, z: float) -> None:
        """
        Chồng các box cùng loại lên trên hàng đã đặt
        Chiến lược 2: Lấp đầy chiều cao
        """
        # Hiện tại bỏ qua stacking để tránh lỗi logic
        # Sẽ được implement trong phiên bản sau
        pass
    
    def _find_stacking_box(self, base_box: Box, available_height: float) -> Optional[Box]:
        """Tìm box phù hợp để chồng lên base_box"""
        # Hiện tại trả về None để tránh lỗi logic
        # Sẽ được implement trong phiên bản sau với access đến remaining boxes
        return None
    
    def _remove_used_boxes(self, groups: Dict[str, List[Box]], used_boxes: List[Box]) -> None:
        """Xóa các box đã sử dụng khỏi groups"""
        used_ids = {box.id for box in used_boxes}
        
        for group_label in groups:
            groups[group_label] = [
                box for box in groups[group_label] 
                if box.id not in used_ids
            ]
        
        # Xóa các nhóm rỗng
        empty_groups = [label for label, boxes in groups.items() if not boxes]
        for label in empty_groups:
            del groups[label]
    
    def optimize_packing(self, goods: List[Box], container_dimensions: Dict,
                        respect_groups: bool = True, time_limit: int = 30) -> Tuple[List[Box], float]:
        """
        Tối ưu hóa đóng gói với nhiều chiến lược
        """
        best_result = []
        best_utilization = 0
        start_time = time.time()
        
        strategies = [
            ("Thể tích giảm dần", lambda boxes: sorted(boxes, key=lambda x: -x.volume)),
            ("Chiều rộng giảm dần", lambda boxes: sorted(boxes, key=lambda x: -x.width)),
            ("Chiều cao giảm dần", lambda boxes: sorted(boxes, key=lambda x: -x.height)),
            ("Footprint giảm dần", lambda boxes: sorted(boxes, key=lambda x: -(x.width * x.depth))),
        ]
        
        for strategy_name, sort_func in strategies:
            if time.time() - start_time > time_limit:
                break
                
            print(f"Thử chiến lược: {strategy_name}")
            sorted_goods = sort_func([box.clone() for box in goods])
            
            result, utilization = self.pack(sorted_goods, container_dimensions)
            
            if utilization > best_utilization:
                best_utilization = utilization
                best_result = result
                print(f"  → Cải thiện: {utilization:.2%}")
            else:
                print(f"  → Kết quả: {utilization:.2%}")
        
        print(f"Kết quả tối ưu: {best_utilization:.2%}")
        return best_result, best_utilization

# Hàm tiện ích để test
def create_test_boxes() -> List[Box]:
    """Tạo dữ liệu test"""
    boxes = [
        Box("1", 700, 960, 690, "Box 1", "A", 10),
        Box("2", 700, 960, 690, "Box 2", "A", 10),
        Box("3", 500, 500, 500, "Box 3", "B", 8),
        Box("4", 500, 500, 500, "Box 4", "B", 8),
        Box("5", 800, 400, 600, "Box 5", "C", 12),
    ]
    return boxes

def test_algorithm():
    """Test thuật toán"""
    boxes = create_test_boxes()
    container_dims = {"width": 2340, "height": 2694, "depth": 12117}
    
    algo = OptimizedLayerPackingAlgorithm()
    result, utilization = algo.pack(boxes, container_dims)
    
    print(f"Đặt được {len(result)}/{len(boxes)} box")
    print(f"Tỷ lệ sử dụng: {utilization:.2%}")
    
    for box in result:
        print(f"Box {box.id}: ({box.position['x']:.1f}, {box.position['y']:.1f}, {box.position['z']:.1f})")

if __name__ == "__main__":
    test_algorithm()