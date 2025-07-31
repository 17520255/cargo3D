import numpy as np  # type: ignore
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time
import heapq
from functools import lru_cache
from itertools import groupby

@dataclass
class Box:
    id: str
    width: float
    height: float
    depth: float
    name: str
    label: str  # Dùng để nhóm các box
    weight: float
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    placed: bool = False
    orientation: int = 0
    
    def __post_init__(self):
        self.volume = self.width * self.height * self.depth
        self.placed = False
        self.orientation = 0  # 0: original, 1: rotated
    
    def get_orientations(self) -> List[Dict]:
        """Chỉ cho phép xoay quanh trục y (giới hạn orientation)"""
        orientations = []
        # Chỉ cho phép xoay quanh trục y: (width, height, depth) và (depth, height, width)
        dimensions = [
            (self.width, self.height, self.depth),
            (self.depth, self.height, self.width)
        ]
        for i, (w, h, d) in enumerate(dimensions):
            orientations.append({
                "width": w, "height": h, "depth": d,
                "volume": w * h * d,
                "orientation": i
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

class OptimizedSpatialIndex:
    """Cấu trúc dữ liệu spatial index tối ưu để kiểm tra va chạm nhanh"""
    def __init__(self, container_width: float, container_height: float,
                 container_depth: float, cell_size: float = 50):  # Tăng cell_size để giảm số lượng cell
        self.cell_size = cell_size
        self.width = max(1, int(np.ceil(container_width / cell_size)))
        self.height = max(1, int(np.ceil(container_height / cell_size)))
        self.depth = max(1, int(np.ceil(container_depth / cell_size)))
        self.grid = defaultdict(set)  # Sử dụng set thay vì list để tìm kiếm nhanh hơn
        # Cache cho các phép kiểm tra va chạm
        self.collision_cache = {}
    
    def add_box(self, box: 'Box') -> None:
        """Thêm box vào spatial index"""
        cells = self._get_box_cells(box)
        for cell in cells:
            self.grid[cell].add(box.id)
    
    def _get_box_cells(self, box: 'Box') -> List[str]:
        """Lấy danh sách các cell mà box chiếm"""
        cells = []
        start_x = max(0, int(box.position['x'] / self.cell_size))
        end_x = min(self.width - 1, int((box.position['x'] + box.width) / self.cell_size))
        start_y = max(0, int(box.position['y'] / self.cell_size))
        end_y = min(self.height - 1, int((box.position['y'] + box.height) / self.cell_size))
        start_z = max(0, int(box.position['z'] / self.cell_size))
        end_z = min(self.depth - 1, int((box.position['z'] + box.depth) / self.cell_size))
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                for z in range(start_z, end_z + 1):
                    cells.append(f"{x},{y},{z}")
        return cells
    
    def check_collision(self, box_width: float, box_height: float, box_depth: float,
                       x: float, y: float, z: float) -> bool:
        """Kiểm tra va chạm với caching"""
        # Tạo key cho cache
        cache_key = (box_width, box_height, box_depth, x, y, z)
        if cache_key in self.collision_cache:
            return self.collision_cache[cache_key]
        
        # Kiểm tra va chạm
        start_x = max(0, int(x / self.cell_size))
        end_x = min(self.width - 1, int((x + box_width) / self.cell_size))
        start_y = max(0, int(y / self.cell_size))
        end_y = min(self.height - 1, int((y + box_height) / self.cell_size))
        start_z = max(0, int(z / self.cell_size))
        end_z = min(self.depth - 1, int((z + box_depth) / self.cell_size))
        
        for x_cell in range(start_x, end_x + 1):
            for y_cell in range(start_y, end_y + 1):
                for z_cell in range(start_z, end_z + 1):
                    cell = f"{x_cell},{y_cell},{z_cell}"
                    if cell in self.grid and len(self.grid[cell]) > 0:
                        self.collision_cache[cache_key] = True
                        return True
        
        self.collision_cache[cache_key] = False
        return False

class Container:
    """Container để đặt các box"""
    def __init__(self, width: float, height: float, depth: float):
        self.width = width
        self.height = height
        self.depth = depth
        self.volume = width * height * depth
        self.used_volume = 0
        self.boxes = []
        self.box_dict = {}  # Lưu trữ box theo id để tìm kiếm nhanh
        self.spatial_index = OptimizedSpatialIndex(width, height, depth)
        self.extreme_points = [{"x": 0, "y": 0, "z": 0}]  # Khởi tạo với điểm gốc
        self.layers = []  # Các lớp theo chiều z (song song mặt trong container)
    
    def can_place(self, box: 'Box', x: float, y: float, z: float) -> bool:
        # Kiểm tra biên container
        if (x + box.width > self.width or
            y + box.height > self.height or
            z + box.depth > self.depth or
            x < 0 or y < 0 or z < 0):
            return False
        # Kiểm tra va chạm với các box đã đặt
        for other in self.boxes:
            if self._is_overlap(box, x, y, z, other):
                return False
        return True
    
    def _is_overlap(self, box: 'Box', x: float, y: float, z: float, other: 'Box') -> bool:
        # Kiểm tra va chạm giữa box (tại x,y,z) và other
        return (
            x < other.position['x'] + other.width and x + box.width > other.position['x'] and
            y < other.position['y'] + other.height and y + box.height > other.position['y'] and
            z < other.position['z'] + other.depth and z + box.depth > other.position['z']
        )
    
    def place_box(self, box: 'Box', x: float, y: float, z: float) -> None:
        box.position = {"x": x, "y": y, "z": z}
        box.placed = True
        self.boxes.append(box)
        self.box_dict[box.id] = box
        self.used_volume += box.volume
        self.spatial_index.add_box(box)
        self._update_extreme_points(box)
        self._update_layers(box)
    
    def _update_extreme_points(self, box: 'Box') -> None:
        # Sinh các extreme point mới dựa trên box vừa đặt
        new_points = [
            {"x": box.position["x"] + box.width, "y": box.position["y"], "z": box.position["z"]},
            {"x": box.position["x"], "y": box.position["y"] + box.height, "z": box.position["z"]},
            {"x": box.position["x"], "y": box.position["y"], "z": box.position["z"] + box.depth},
            # Bổ sung: điểm cực ở cạnh bên (theo trục z) của box vừa đặt
            {"x": box.position["x"], "y": box.position["y"], "z": box.position["z"] + box.depth}
        ]
        # Loại bỏ các điểm bị che phủ bởi box vừa đặt
        self.extreme_points = [p for p in self.extreme_points if not self._is_point_inside_box(p, box)]
        # Thêm các điểm mới nếu hợp lệ
        for p in new_points:
            if self._is_point_valid(p):
                self.extreme_points.append(p)
        
        # Đảm bảo luôn sinh điểm cực phía trên (cùng x, z) cho mọi box đã đặt
        for b in self.boxes:
            top_point = {"x": b.position["x"], "y": b.position["y"] + b.height, "z": b.position["z"]}
            if self._is_point_valid(top_point):
                self.extreme_points.append(top_point)
        # --- BỔ SUNG: Sinh điểm cực ở các giao điểm giữa các box đã đặt (ở y=0) ---
        for other in self.boxes:
            if other is not box:
                # Giao điểm cạnh phải box này với cạnh trước box kia (ở y=0)
                new_point1 = {"x": box.position["x"] + box.width, "y": 0, "z": other.position["z"] + other.depth}
                if self._is_point_valid(new_point1):
                    self.extreme_points.append(new_point1)
                # Giao điểm cạnh trước box này với cạnh phải box kia (ở y=0)
                new_point2 = {"x": other.position["x"] + other.width, "y": 0, "z": box.position["z"] + box.depth}
                if self._is_point_valid(new_point2):
                    self.extreme_points.append(new_point2)
        # --- HẾT BỔ SUNG ---
        # Sinh điểm cực ở cạnh phải và cạnh sau của mọi box đã đặt trên cùng lớp (cùng y)
        for b in self.boxes:
            if abs(b.position["y"] - box.position["y"]) < 1e-3:
                right_point = {"x": b.position["x"] + b.width, "y": b.position["y"], "z": b.position["z"]}
                if self._is_point_valid(right_point):
                    self.extreme_points.append(right_point)
                back_point = {"x": b.position["x"], "y": b.position["y"], "z": b.position["z"] + b.depth}
                if self._is_point_valid(back_point):
                    self.extreme_points.append(back_point)
    
    def _is_point_inside_box(self, point: Dict, box: 'Box') -> bool:
        return (
            box.position["x"] <= point["x"] < box.position["x"] + box.width and
            box.position["y"] <= point["y"] < box.position["y"] + box.height and
            box.position["z"] <= point["z"] < box.position["z"] + box.depth
        )
    
    def _is_point_valid(self, point: Dict) -> bool:
        # Điểm phải nằm trong container và không bị che phủ bởi box nào
        if not (0 <= point["x"] <= self.width and 0 <= point["y"] <= self.height and 0 <= point["z"] <= self.depth):
            return False
        for box in self.boxes:
            if self._is_point_inside_box(point, box):
                return False
        return True
    
    def _update_layers(self, box: 'Box') -> None:
        z = box.position["z"]
        found = False
        for layer in self.layers:
            if abs(layer["z"] - z) < 1e-3:
                found = True
                layer["boxes"].append(box.id)
                layer["depth"] = max(layer["depth"], box.depth)
                break
        if not found:
            self.layers.append({
                "z": z,
                "depth": box.depth,
                "boxes": [box.id]
            })
            self.layers.sort(key=lambda l: l["z"])
    
    def get_utilization(self) -> float:
        return self.used_volume / self.volume if self.volume > 0 else 0
    
    def get_layer_boxes(self, layer_index: int) -> List['Box']:
        if 0 <= layer_index < len(self.layers):
            layer = self.layers[layer_index]
            return [self.box_dict[box_id] for box_id in layer["boxes"]]
        return []
    
    def has_support(self, box: 'Box', x: float, y: float, z: float, support_threshold: float = 0.7) -> bool:
        """Kiểm tra xem box có được hỗ trợ đủ từ bên dưới không"""
        # Nếu box nằm trên mặt đất, luôn có hỗ trợ
        if abs(y) < 1e-3:
            return True
        
        # Tính diện tích đáy của box
        box_base_area = box.width * box.depth
        
        # Tính diện tích được hỗ trợ bởi các box khác
        supported_area = 0
        
        # Tính tọa độ đáy của box
        box_bottom_y = y
        box_min_x, box_max_x = x, x + box.width
        box_min_z, box_max_z = z, z + box.depth
        
        # Kiểm tra từng box đã đặt
        for other in self.boxes:
            other_top_y = other.position["y"] + other.height
            
            # Nếu box nằm ngay trên other (chênh lệch y nhỏ)
            if abs(box_bottom_y - other_top_y) < 1e-3:
                # Tính phần giao nhau theo x và z
                overlap_min_x = max(box_min_x, other.position["x"])
                overlap_max_x = min(box_max_x, other.position["x"] + other.width)
                
                overlap_min_z = max(box_min_z, other.position["z"])
                overlap_max_z = min(box_max_z, other.position["z"] + other.depth)
                
                # Nếu có phần giao nhau
                if overlap_min_x < overlap_max_x and overlap_min_z < overlap_max_z:
                    overlap_area = (overlap_max_x - overlap_min_x) * (overlap_max_z - overlap_min_z)
                    supported_area += overlap_area
        
        # Box được coi là có hỗ trợ nếu tỷ lệ diện tích được hỗ trợ đạt ngưỡng
        support_ratio = supported_area / box_base_area if box_base_area > 0 else 0
        return support_ratio >= support_threshold
    
    def check_stability(self, placed_boxes: List['Box']) -> bool:
        """Kiểm tra tính ổn định của toàn bộ cấu trúc đã đặt"""
        # Sắp xếp box theo chiều cao y tăng dần
        sorted_boxes = sorted(placed_boxes, key=lambda b: b.position["y"])
        
        # Kiểm tra từng box trừ những box nằm trên mặt đất
        for box in sorted_boxes:
            if box.position["y"] > 1e-3:  # Box không nằm trên mặt đất
                if not self.has_support(box, box.position["x"], box.position["y"], box.position["z"]):
                    return False
        
        return True

class EnhancedPackingAlgorithm:
    """Thuật toán đóng gói nâng cao: First Fit Decreasing + Extreme Point, kiểm tra va chạm và biên container chặt chẽ"""
    def __init__(self):
        self.start_time = 0
        self.time_limit = 30
        self.support_threshold = 0.6  # Ngưỡng tỷ lệ diện tích hỗ trợ tối thiểu
    
    def pack(self, goods: List['Box'], container_dimensions: Dict, respect_groups: bool = True, time_limit: int = 30) -> Tuple[List['Box'], float]:
        self.start_time = time.time()
        self.time_limit = time_limit
        container = Container(**container_dimensions)
        sorted_goods = sorted(goods, key=lambda x: -x.volume)
        if respect_groups:
            groups = defaultdict(list)
            for box in sorted_goods:
                groups[box.label].append(box)
            sorted_groups = sorted(groups.items(), key=lambda x: -sum(box.volume for box in x[1]))
            sorted_goods = []
            for _, group_boxes in sorted_groups:
                group_boxes.sort(key=lambda x: -x.volume)
                sorted_goods.extend(group_boxes)
        placed_boxes = self._pack_with_extreme_points(sorted_goods, container)
        return placed_boxes, container.get_utilization()
    
    def _find_lowest_y(self, box: 'Box', x: float, z: float, container: Container) -> float:
        """Tìm y thấp nhất có thể đặt box tại (x, z) mà không bị treo lơ lửng"""
        max_y = 0.0
        for other in container.boxes:
            # Kiểm tra nếu box nằm ngay trên other (theo x, z)
            if (x + box.width > other.position["x"] and x < other.position["x"] + other.width and
                z + box.depth > other.position["z"] and z < other.position["z"] + other.depth):
                top_y = other.position["y"] + other.height
                if top_y > max_y and top_y + box.height <= container.height + 1e-3:
                    max_y = top_y
        return max_y

    def _find_lowest_z(self, box: 'Box', x: float, y: float, container: Container) -> float:
        """Tìm z thấp nhất có thể đặt box tại (x, y) mà không bị treo lơ lửng"""
        max_z = 0.0
        for other in container.boxes:
            # Kiểm tra nếu box nằm ngay trên other (theo x, y)
            if (x + box.width > other.position["x"] and x < other.position["x"] + other.width and
                y + box.height > other.position["y"] and y < other.position["y"] + other.height):
                front_z = other.position["z"] + other.depth
                if front_z > max_z and front_z + box.depth <= container.depth + 1e-3:
                    max_z = front_z
        return max_z
    
    def _pack_with_extreme_points(self, sorted_goods: List['Box'], container: Container) -> List['Box']:
        placed_boxes = []
        remaining_goods = sorted_goods.copy()
        z = 0.0
        while z < container.depth - 1e-3 and remaining_goods:
            max_layer_depth = 0.0
            y = 0.0
            while y < container.height - 1e-3 and remaining_goods:
                row_boxes = []
                used_indices = set()
                x = 0.0
                max_row_height = 0.0
                min_x_gap = float('inf')
                while x < container.width - 1e-3 and remaining_goods:
                    best_box = None
                    best_orientation = None
                    best_idx = -1
                    min_x_gap = float('inf')
                    best_y = None
                    best_z = None
                    # Tìm box phù hợp nhất để đặt tại vị trí (x, y, z)
                    for idx, box in enumerate(remaining_goods):
                        for orientation in box.get_orientations():
                            w, h, d = orientation["width"], orientation["height"], orientation["depth"]
                            # Tìm y thấp nhất có thể đặt box tại (x, z)
                            y_pos = self._find_lowest_y(box, x, z, container)
                            # Tìm z thấp nhất có thể đặt box tại (x, y)
                            z_pos = self._find_lowest_z(box, x, y_pos, container)
                            if x + w <= container.width + 1e-3 and y_pos + h <= container.height + 1e-3 and z_pos + d <= container.depth + 1e-3:
                                # Kiểm tra va chạm với các box đã đặt trong hàng này
                                collision = False
                                for b in row_boxes:
                                    if not (x + w <= b.position["x"] or x >= b.position["x"] + b.width or
                                            y_pos + h <= b.position["y"] or y_pos >= b.position["y"] + b.height or
                                            z_pos + d <= b.position["z"] or z_pos >= b.position["z"] + b.depth):
                                        collision = True
                                        break
                                if not collision:
                                    x_gap = abs(container.width - (x + w))
                                    if x_gap < min_x_gap:
                                        min_x_gap = x_gap
                                        best_box = box
                                        best_orientation = orientation
                                        best_idx = idx
                                        best_y = y_pos
                                        best_z = z_pos
                    if best_box is not None:
                        # Đặt box vào vị trí (x, best_y, best_z) với orientation tốt nhất
                        best_box.width = best_orientation["width"]
                        best_box.height = best_orientation["height"]
                        best_box.depth = best_orientation["depth"]
                        best_box.orientation = best_orientation["orientation"]
                        best_box.position = {"x": x, "y": best_y, "z": best_z}
                        best_box.placed = True
                        row_boxes.append(best_box)
                        placed_boxes.append(best_box)
                        container.place_box(best_box, x, best_y, best_z)
                        max_row_height = max(max_row_height, best_box.height + (best_y - y))
                        max_layer_depth = max(max_layer_depth, best_box.depth + (best_z - z))
                        x += best_box.width
                        used_indices.add(best_idx)
                    else:
                        # Không còn box nào phù hợp để lấp đầy x, kết thúc hàng này
                        break
                # Xóa các box đã dùng khỏi remaining_goods
                for idx in sorted(used_indices, reverse=True):
                    del remaining_goods[idx]
                if max_row_height < 1e-3:
                    # Không đặt được box nào ở hàng này, dừng lấp y
                    break
                y += max_row_height
            if max_layer_depth < 1e-3:
                # Không đặt được box nào ở lớp này, dừng lấp z
                break
            z += max_layer_depth
        return placed_boxes
    
    def _calculate_position_score(self, box: 'Box', x: float, y: float, z: float, container: Container) -> float:
        """Tính điểm cho vị trí đặt box"""
        score = 0
        # Ưu tiên cao nhất: đặt sát mặt trong (z=0)
        if abs(z) < 1e-3:
            score += 300  # Tăng điểm cho việc đặt sát mặt trong
        # Ưu tiên đặt sát với các mặt của container
        is_x0 = abs(x) < 1e-3
        is_xw = abs(x + box.width - container.width) < 1e-3
        is_y0 = abs(y) < 1e-3
        is_zw = abs(z + box.depth - container.depth) < 1e-3
        is_z0 = abs(z) < 1e-3
        if is_x0 or is_xw:
            score += 150  # Tăng điểm cho việc đặt sát tường
        if is_y0 or is_zw:
            score += 150  # Tăng điểm cho việc đặt sát tường (y=0 hoặc sát cửa)
        # Tăng điểm lớn nếu box nằm sát cả 3 mặt (góc sâu nhất)
        if (is_x0 or is_xw) and is_y0 and (is_z0 or is_zw):
            score += 400  # Điểm thưởng lớn cho góc container
        # Ưu tiên đặt sát với box khác
        for other_box in container.boxes:
            if (abs(x - (other_box.position['x'] + other_box.width)) < 1e-3 or
                abs(other_box.position['x'] - (x + box.width)) < 1e-3 or
                abs(z - (other_box.position['z'] + other_box.depth)) < 1e-3 or
                abs(other_box.position['z'] - (z + box.depth)) < 1e-3 or
                abs(y - (other_box.position['y'] + other_box.height)) < 1e-3 or
                abs(other_box.position['y'] - (y + box.height)) < 1e-3):
                score += 80  # Tăng điểm cho việc đặt sát với box khác
            # Ưu tiên đặt box cùng nhóm gần nhau
            if box.label == other_box.label:
                distance = ((x - other_box.position['x'])**2 + 
                           (y - other_box.position['y'])**2 + 
                           (z - other_box.position['z'])**2)**0.5
                if distance < box.width + box.depth:
                    score += 50
        # Ưu tiên đặt trên cùng một lớp (theo z)
        for layer in container.layers:
            if abs(z - layer["z"]) < 1e-3:
                score += 100
                layer_boxes = container.get_layer_boxes(container.layers.index(layer))
                if any(b.label == box.label for b in layer_boxes):
                    score += 70
                break
        # Ưu tiên cao: đặt box trên một box khác (có đế chịu lực)
        support_ratio = 0
        box_base_area = box.width * box.depth
        supported_area = 0
        for other_box in container.boxes:
            if abs(y - (other_box.position['y'] + other_box.height)) < 1e-3:
                # Tính phần giao nhau theo x và z
                overlap_min_x = max(x, other_box.position["x"])
                overlap_max_x = min(x + box.width, other_box.position["x"] + other_box.width)
                overlap_min_z = max(z, other_box.position["z"])
                overlap_max_z = min(z + box.depth, other_box.position["z"] + other_box.depth)
                # Nếu có phần giao nhau
                if overlap_min_x < overlap_max_x and overlap_min_z < overlap_max_z:
                    overlap_area = (overlap_max_x - overlap_min_x) * (overlap_max_z - overlap_min_z)
                    supported_area += overlap_area
        support_ratio = supported_area / box_base_area if box_base_area > 0 else 0
        # Điểm cho tỷ lệ hỗ trợ
        if support_ratio >= self.support_threshold:
            score += 250 + (support_ratio - self.support_threshold) * 200  # Tăng điểm cho hỗ trợ tốt
        elif y > 1e-3:  # Nếu box không nằm trên mặt đất và không có đủ hỗ trợ
            score -= 800  # Phạt nặng hơn
        # Thêm điểm cho việc tối ưu không gian
        # Ưu tiên các vị trí tạo ra ít không gian thừa
        empty_space_behind = 0
        if z + box.depth < container.depth:
            # Tính không gian trống phía sau box
            empty_space_behind = (container.depth - (z + box.depth)) * box.width * box.height
        # Phạt điểm cho không gian trống phía sau
        if empty_space_behind > 0:
            empty_ratio = empty_space_behind / (container.width * container.height * container.depth)
            score -= empty_ratio * 100  # Phạt nhẹ cho không gian trống
        # Thưởng điểm cho việc tối ưu thể tích
        volume_ratio = box.volume / (container.width * container.height * container.depth)
        score += volume_ratio * 500  # Thưởng lớn cho box có thể tích lớn
        # Ưu tiên đặt sát phía trong container (z nhỏ nhất)
        if abs(z) < 1e-3:
            score += 250  # Tăng điểm cho vị trí sát phía trong container
        # Ưu tiên đặt sát bên cạnh box cùng lớp (x hoặc y liền kề, cùng z)
        for other_box in container.boxes:
            if abs(z - other_box.position['z']) < 1e-3:
                if abs(x - (other_box.position['x'] + other_box.width)) < 1e-3 or abs(y - (other_box.position['y'] + other_box.height)) < 1e-3:
                    score += 200  # Tăng điểm cho việc đặt sát bên cạnh box cùng lớp
        return score
    
    def optimize_packing(self, goods: List['Box'], container_dimensions: Dict, respect_groups: bool = True, time_limit: int = 30) -> Tuple[List['Box'], float]:
        best_result = None
        best_utilization = 0
        target_utilization = 0.8  # Mục tiêu tỷ lệ sử dụng > 80%
        
        print("Chiến lược 1: Sắp xếp theo thể tích giảm dần")
        result1, util1 = self.pack(goods, container_dimensions, respect_groups, time_limit)
        if util1 > best_utilization:
            best_utilization = util1
            best_result = result1
            
        print("Chiến lược 2: Sắp xếp theo kích thước lớn nhất giảm dần")
        sorted_goods = sorted(goods, key=lambda x: -max(x.width, x.height, x.depth))
        result2, util2 = self.pack(sorted_goods, container_dimensions, respect_groups, time_limit)
        if util2 > best_utilization:
            best_utilization = util2
            best_result = result2
            
        print("Chiến lược 3: Sắp xếp theo footprint giảm dần")
        sorted_goods = sorted(goods, key=lambda x: -(x.width * x.depth))
        result3, util3 = self.pack(sorted_goods, container_dimensions, respect_groups, time_limit)
        if util3 > best_utilization:
            best_utilization = util3
            best_result = result3
            
        print("Chiến lược 4: Sắp xếp theo chiều cao giảm dần")
        sorted_goods = sorted(goods, key=lambda x: -x.height)
        result4, util4 = self.pack(sorted_goods, container_dimensions, respect_groups, time_limit)
        if util4 > best_utilization:
            best_utilization = util4
            best_result = result4
        
        # Nếu tỷ lệ sử dụng chưa đạt mục tiêu, thử thêm các chiến lược khác
        if best_utilization < target_utilization:
            print(f"Tỷ lệ sử dụng {best_utilization:.2%} chưa đạt mục tiêu {target_utilization:.2%}, thử chiến lược bổ sung")
            
            # Chiến lược 5: Kết hợp sắp xếp theo thể tích và nhóm
            print("Chiến lược 5: Kết hợp sắp xếp theo thể tích và nhóm")
            # Sắp xếp theo nhóm trước, sau đó theo thể tích trong mỗi nhóm
            sorted_by_label = sorted(goods, key=lambda x: x.label)
            grouped_goods = []
            
            for _, group in groupby(sorted_by_label, key=lambda x: x.label):
                # Sắp xếp theo thể tích giảm dần trong mỗi nhóm
                sorted_group = sorted(list(group), key=lambda x: -x.volume)
                grouped_goods.extend(sorted_group)
                
            result5, util5 = self.pack(grouped_goods, container_dimensions, respect_groups=True, time_limit=time_limit)
            if util5 > best_utilization:
                best_utilization = util5
                best_result = result5
            
            # Chiến lược 6: Tăng thời gian tìm kiếm nếu vẫn chưa đạt mục tiêu
            if best_utilization < target_utilization and time_limit < 120:
                extended_time = min(120, time_limit * 2)  # Tối đa 120 giây
                print(f"Chiến lược 6: Tăng thời gian tìm kiếm lên {extended_time}s")
                result6, util6 = self.pack(goods, container_dimensions, respect_groups, extended_time)
                if util6 > best_utilization:
                    best_utilization = util6
                    best_result = result6
        
        # Kiểm tra tính ổn định của kết quả tốt nhất
        container = Container(**container_dimensions)
        for box in best_result:
            container.place_box(box, box.position["x"], box.position["y"], box.position["z"])
        
        if not container.check_stability(best_result):
            print("Cảnh báo: Kết quả tốt nhất có box không ổn định, thử lại với ngưỡng hỗ trợ cao hơn")
            # Tăng ngưỡng hỗ trợ và thử lại
            self.support_threshold = 0.8
            result_stable, util_stable = self.pack(goods, container_dimensions, respect_groups, time_limit)
            if container.check_stability(result_stable):
                print("Đã tìm được kết quả ổn định với ngưỡng hỗ trợ cao hơn")
                best_result = result_stable
                best_utilization = util_stable
                
        print(f"Kết quả tối ưu: Tỷ lệ sử dụng {best_utilization:.2%}" + 
              (", ĐẠT MỤC TIÊU ✓" if best_utilization >= target_utilization else ", CHƯA ĐẠT MỤC TIÊU ✗"))
        
        return best_result, best_utilization 