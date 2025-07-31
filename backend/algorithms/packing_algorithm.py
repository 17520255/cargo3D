import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from copy import deepcopy
import random
from collections import defaultdict
import time
from functools import lru_cache
import heapq

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
        self.orientation = 0  # 0: original, 1: rotated
    
    def get_orientations(self) -> List[Dict]:
        orientations = []
        # Thêm tất cả 6 hướng xoay có thể
        dimensions = [
            (self.width, self.height, self.depth),
            (self.depth, self.height, self.width),
            (self.width, self.depth, self.height),
            (self.height, self.width, self.depth),
            (self.depth, self.width, self.height),
            (self.height, self.depth, self.width)
        ]
        
        for w, h, d in dimensions:
            orientations.append({
                "width": w, "height": h, "depth": d,
                "volume": w * h * d
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
    def __init__(self, container_width: float, container_height: float,
                 container_depth: float, cell_size: float = 5):
        self.cell_size = cell_size
        self.width = int(np.ceil(container_width / cell_size))
        self.height = int(np.ceil(container_height / cell_size))
        self.depth = int(np.ceil(container_depth / cell_size))
        self.grid = defaultdict(set)  # Sử dụng set thay vì list để tìm kiếm nhanh hơn
    
    def add_box(self, box: 'Box') -> None:
        cells = self.get_box_cells(box)
        for cell in cells:
            self.grid[cell].add(box.id)
    
    def get_box_cells(self, box: 'Box') -> List[str]:
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
    
    @lru_cache(maxsize=1000)
    def check_collision_fast(self, box_width: float, box_height: float, box_depth: float,
                           x: float, y: float, z: float) -> bool:
        """Tối ưu hóa kiểm tra va chạm với caching"""
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
                        return True
        return False

class Container:
    def __init__(self, width: float, height: float, depth: float):
        self.width = width
        self.height = height
        self.depth = depth
        self.volume = width * height * depth
        self.used_volume = 0
        self.boxes = []
        self.spatial_index = OptimizedSpatialIndex(width, height, depth)
        self.space_heap = []  # Sử dụng heap để tối ưu tìm kiếm không gian
        self._initialize_space_heap()
    
    def _initialize_space_heap(self):
        """Khởi tạo heap với không gian ban đầu"""
        initial_space = {
            "x": 0, "y": 0, "z": 0,
            "width": self.width, "height": self.height, "depth": self.depth,
            "volume": self.volume
        }
        heapq.heappush(self.space_heap, (-self.volume, 0, initial_space))
    
    def can_place(self, box: 'Box', x: float, y: float, z: float) -> bool:
        # Kiểm tra biên container
        if (x + box.width > self.width or
            y + box.height > self.height or
            z + box.depth > self.depth):
            return False
        
        # Sử dụng spatial index tối ưu để kiểm tra va chạm
        return not self.spatial_index.check_collision_fast(
            box.width, box.height, box.depth, x, y, z
        )
    
    def place_box(self, box: 'Box', x: float, y: float, z: float) -> None:
        box.position = {"x": x, "y": y, "z": z}
        box.placed = True
        self.boxes.append(box)
        self.used_volume += box.volume
        self.spatial_index.add_box(box)
        self._update_space_heap(box, x, y, z)
    
    def _update_space_heap(self, box: 'Box', x: float, y: float, z: float):
        """Cập nhật heap không gian sau khi đặt box"""
        new_spaces = []
        
        # Tạo không gian mới từ việc chia không gian hiện tại
        for _, _, space in self.space_heap:
            if self._space_contains_box(space, box, x, y, z):
                # Chia không gian thành các phần nhỏ hơn
                divided_spaces = self._divide_space(space, box, x, y, z)
                new_spaces.extend(divided_spaces)
            else:
                new_spaces.append(space)
        
        # Cập nhật heap
        self.space_heap = []
        for i, space in enumerate(new_spaces):
            if space['volume'] > 0:
                heapq.heappush(self.space_heap, (-space['volume'], i, space))
    
    def _space_contains_box(self, space: Dict, box: 'Box', x: float, y: float, z: float) -> bool:
        """Kiểm tra xem không gian có chứa box không"""
        return (space['x'] <= x and x + box.width <= space['x'] + space['width'] and
                space['y'] <= y and y + box.height <= space['y'] + space['height'] and
                space['z'] <= z and z + box.depth <= space['z'] + space['depth'])
    
    def _divide_space(self, space: Dict, box: 'Box', x: float, y: float, z: float) -> List[Dict]:
        """Chia không gian thành các phần nhỏ hơn"""
        spaces = []
        min_size = 1
        
        # Không gian phía trên
        if y + box.height < space['y'] + space['height']:
            top_space = {
                "x": space['x'], "y": y + box.height, "z": space['z'],
                "width": space['width'], "height": space['y'] + space['height'] - (y + box.height),
                "depth": space['depth'], "volume": space['width'] * (space['y'] + space['height'] - (y + box.height)) * space['depth']
            }
            if top_space['volume'] > min_size:
                spaces.append(top_space)
        
        # Không gian phía dưới
        if y > space['y']:
            bottom_space = {
                "x": space['x'], "y": space['y'], "z": space['z'],
                "width": space['width'], "height": y - space['y'],
                "depth": space['depth'], "volume": space['width'] * (y - space['y']) * space['depth']
            }
            if bottom_space['volume'] > min_size:
                spaces.append(bottom_space)
        
        # Không gian bên trái
        if x > space['x']:
            left_space = {
                "x": space['x'], "y": y, "z": space['z'],
                "width": x - space['x'], "height": box.height,
                "depth": space['depth'], "volume": (x - space['x']) * box.height * space['depth']
            }
            if left_space['volume'] > min_size:
                spaces.append(left_space)
        
        # Không gian bên phải
        if x + box.width < space['x'] + space['width']:
            right_space = {
                "x": x + box.width, "y": y, "z": space['z'],
                "width": space['x'] + space['width'] - (x + box.width), "height": box.height,
                "depth": space['depth'], "volume": (space['x'] + space['width'] - (x + box.width)) * box.height * space['depth']
            }
            if right_space['volume'] > min_size:
                spaces.append(right_space)
        
        # Không gian phía trước
        if z > space['z']:
            front_space = {
                "x": x, "y": y, "z": space['z'],
                "width": box.width, "height": box.height,
                "depth": z - space['z'], "volume": box.width * box.height * (z - space['z'])
            }
            if front_space['volume'] > min_size:
                spaces.append(front_space)
        
        # Không gian phía sau
        if z + box.depth < space['z'] + space['depth']:
            back_space = {
                "x": x, "y": y, "z": z + box.depth,
                "width": box.width, "height": box.height,
                "depth": space['z'] + space['depth'] - (z + box.depth),
                "volume": box.width * box.height * (space['z'] + space['depth'] - (z + box.depth))
            }
            if back_space['volume'] > min_size:
                spaces.append(back_space)
        
        return spaces
    
    def get_utilization(self) -> float:
        return self.used_volume / self.volume if self.volume > 0 else 0
    
    def clone(self) -> 'Container':
        new_container = Container(self.width, self.height, self.depth)
        new_container.used_volume = self.used_volume
        new_container.boxes = [box.clone() for box in self.boxes]
        new_container.spatial_index = deepcopy(self.spatial_index)
        new_container.space_heap = deepcopy(self.space_heap)
        return new_container

class BestFitPackingOptimizer:
    """Thuật toán Best Fit tối ưu hóa"""
    
    def __init__(self):
        self.placement_strategies = [
            self._corner_placement,
            self._wall_placement,
            self._center_placement
        ]
    
    def pack(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        container = Container(**container_dimensions)
        placed_boxes = []
        
        # Sắp xếp theo thể tích giảm dần và ưu tiên box lớn
        sorted_goods = sorted(goods, key=lambda x: (-x.volume, -x.width, -x.height, -x.depth))
        
        for box in sorted_goods:
            best_position = self._find_best_fit_position(container, box)
            if best_position:
                x, y, z = best_position
                container.place_box(box, x, y, z)
                placed_boxes.append(box)
        
        return placed_boxes, container.get_utilization()
    
    def _find_best_fit_position(self, container: Container, box: 'Box') -> Optional[Tuple[float, float, float]]:
        best_score = -1
        best_position = None
        
        for orientation in box.get_orientations():
            box.width, box.height, box.depth = orientation['width'], orientation['height'], orientation['depth']
            
            for _, _, space in container.space_heap:
                if (space['width'] >= box.width and
                    space['height'] >= box.height and
                    space['depth'] >= box.depth):
                    
                    for strategy in self.placement_strategies:
                        x, y, z = strategy(space, box)
                        if container.can_place(box, x, y, z):
                            score = self._calculate_fit_score(space, box, x, y, z)
                            if score > best_score:
                                best_score = score
                                best_position = (x, y, z)
        
        return best_position
    
    def _corner_placement(self, space: Dict, box: 'Box') -> Tuple[float, float, float]:
        """Đặt ở góc không gian"""
        return space['x'], space['y'], space['z']
    
    def _wall_placement(self, space: Dict, box: 'Box') -> Tuple[float, float, float]:
        """Đặt sát tường"""
        x = space['x'] if box.width <= space['width'] / 2 else space['x'] + space['width'] - box.width
        y = space['y'] if box.height <= space['height'] / 2 else space['y'] + space['height'] - box.height
        z = space['z'] if box.depth <= space['depth'] / 2 else space['z'] + space['depth'] - box.depth
        return x, y, z
    
    def _center_placement(self, space: Dict, box: 'Box') -> Tuple[float, float, float]:
        """Đặt ở giữa không gian"""
        x = space['x'] + (space['width'] - box.width) / 2
        y = space['y'] + (space['height'] - box.height) / 2
        z = space['z'] + (space['depth'] - box.depth) / 2
        return x, y, z
    
    def _calculate_fit_score(self, space: Dict, box: 'Box', x: float, y: float, z: float) -> float:
        """Tính điểm phù hợp của vị trí đặt"""
        # Điểm cho việc sử dụng không gian hiệu quả
        space_utilization = (box.volume / space['volume']) * 100
        
        # Điểm cho việc đặt ở góc
        corner_bonus = 0
        if x == space['x'] or x + box.width == space['x'] + space['width']:
            corner_bonus += 10
        if y == space['y'] or y + box.height == space['y'] + space['height']:
            corner_bonus += 10
        if z == space['z'] or z + box.depth == space['z'] + space['depth']:
            corner_bonus += 10
        
        return space_utilization + corner_bonus

class ImprovedGeneticPackingOptimizer:
    """Genetic Algorithm cải tiến với adaptive parameters"""
    
    def __init__(self, population_size: int = 100, generations: int = 200):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
    
    def create_chromosome(self, goods: List['Box']) -> List['Box']:
        chromosome = [box.clone() for box in goods]
        random.shuffle(chromosome)
        return chromosome
    
    def evaluate_fitness(self, chromosome: List['Box'], container_dimensions: Dict) -> float:
        container = Container(**container_dimensions)
        placed_boxes = self.pack_chromosome(chromosome, container)
        utilization = container.get_utilization()
        
        # Thêm penalty cho việc không đặt được box
        penalty = (len(chromosome) - len(placed_boxes)) * 0.1
        return max(0, utilization - penalty)
    
    def pack_chromosome(self, chromosome: List['Box'], container: Container) -> List['Box']:
        placed_boxes = []
        for box in chromosome:
            position = self.find_best_position(container, box)
            if position:
                x, y, z = position
                container.place_box(box, x, y, z)
                placed_boxes.append(box)
        return placed_boxes
    
    def find_best_position(self, container: Container, box: 'Box') -> Optional[Tuple[float, float, float]]:
        best_score = -1
        best_position = None
        
        for _, _, space in container.space_heap:
            for orientation in box.get_orientations():
                if (space['width'] >= orientation['width'] and
                    space['height'] >= orientation['height'] and
                    space['depth'] >= orientation['depth']):
                    
                    score = self.calculate_placement_score(container, box, space['x'], space['y'], space['z'])
                    if score > best_score:
                        best_score = score
                        best_position = (space['x'], space['y'], space['z'])
        
        return best_position
    
    def calculate_placement_score(self, container: Container, box: 'Box',
                                x: float, y: float, z: float) -> float:
        if not container.can_place(box, x, y, z):
            return -1
        
        score = 0
        
        # Điểm cho việc đặt ở góc
        if x == 0 or x + box.width == container.width:
            score += 20
        if y == 0 or y + box.height == container.height:
            score += 20
        if z == 0 or z + box.depth == container.depth:
            score += 20
        
        # Điểm cho việc sát với box khác
        for other_box in container.boxes:
            if (abs(x - (other_box.position['x'] + other_box.width)) < 1 or
                abs(other_box.position['x'] - (x + box.width)) < 1):
                score += 10
            if (abs(y - (other_box.position['y'] + other_box.height)) < 1 or
                abs(other_box.position['y'] - (y + box.height)) < 1):
                score += 10
            if (abs(z - (other_box.position['z'] + other_box.depth)) < 1 or
                abs(other_box.position['z'] - (z + box.depth)) < 1):
                score += 10
        
        return score
    
    def crossover(self, parent1: List['Box'], parent2: List['Box']) -> List['Box']:
        if len(parent1) != len(parent2):
            return parent1
        
        # Order Crossover (OX) cải tiến
        size = len(parent1)
        if size <= 1:
            return parent1.copy()
        
        start = random.randint(0, max(0, size // 3))
        end = random.randint(start + 1, max(start + 1, size * 2 // 3))
        
        child: List[Optional[Box]] = [None] * size
        child[start:end] = parent1[start:end]
        
        remaining = [box for box in parent2 if box not in child[start:end]]
        j = 0
        for i in range(size):
            if child[i] is None and j < len(remaining):
                child[i] = remaining[j]
                j += 1
        
        return [box for box in child if box is not None]
    
    def mutate(self, chromosome: List['Box']) -> List['Box']:
        if random.random() < self.mutation_rate and len(chromosome) >= 2:
            # Swap mutation
            i, j = random.sample(range(len(chromosome)), 2)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
        
        return chromosome
    
    def optimize(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        # Khởi tạo population
        population = [self.create_chromosome(goods) for _ in range(self.population_size)]
        
        best_fitness = 0
        best_chromosome = None
        stagnation_counter = 0
        
        for generation in range(self.generations):
            # Đánh giá fitness
            fitness_scores = []
            for chromosome in population:
                fitness = self.evaluate_fitness(chromosome, container_dimensions)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_chromosome = chromosome.copy()
                    stagnation_counter = 0
                else:
                    stagnation_counter += 1
            
            # Adaptive parameters
            if stagnation_counter > 20:
                self.mutation_rate = min(0.3, self.mutation_rate * 1.1)
                self.crossover_rate = max(0.5, self.crossover_rate * 0.95)
            else:
                self.mutation_rate = max(0.05, self.mutation_rate * 0.99)
                self.crossover_rate = min(0.9, self.crossover_rate * 1.01)
            
            # Tạo population mới
            new_population = []
            
            # Elitism: giữ lại best chromosomes
            elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:self.elite_size]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Tạo chromosome mới bằng crossover và mutation
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1 = self.tournament_selection(population, fitness_scores)
                    parent2 = self.tournament_selection(population, fitness_scores)
                    child = self.crossover(parent1, parent2)
                else:
                    parent = self.tournament_selection(population, fitness_scores)
                    child = parent.copy()
                
                child = self.mutate(child)
                new_population.append(child)
            
            population = new_population
        
        return best_chromosome or [], best_fitness
    
    def tournament_selection(self, population: List[List['Box']], fitness_scores: List[float],
                           tournament_size: int = 3) -> List['Box']:
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        return population[winner_index]

class ExtremePointPackingOptimizer:
    """Thuật toán Extreme Point Heuristic cho 3D Bin Packing"""
    def __init__(self):
        pass

    def pack(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        container = Container(**container_dimensions)
        placed_boxes = []
        extreme_points = [
            {"x": 0, "y": 0, "z": 0}
        ]
        sorted_goods = sorted(goods, key=lambda x: -x.volume)
        for box in sorted_goods:
            best_point = None
            best_util = -1
            best_orientation = None
            for ep in extreme_points:
                for orientation in box.get_orientations():
                    box.width, box.height, box.depth = orientation['width'], orientation['height'], orientation['depth']
                    if container.can_place(box, ep['x'], ep['y'], ep['z']):
                        # Ưu tiên điểm có utilization cao nhất
                        util = self._estimate_utilization(container, box, ep)
                        if util > best_util:
                            best_util = util
                            best_point = ep
                            best_orientation = orientation
            if best_point and best_orientation:
                box.width, box.height, box.depth = best_orientation['width'], best_orientation['height'], best_orientation['depth']
                container.place_box(box, best_point['x'], best_point['y'], best_point['z'])
                placed_boxes.append(box)
                # Cập nhật extreme points
                new_eps = self._generate_new_extreme_points(box)
                for new_ep in new_eps:
                    if not self._is_point_covered(new_ep, extreme_points):
                        extreme_points.append(new_ep)
        return placed_boxes, container.get_utilization()

    def _estimate_utilization(self, container, box, ep):
        # Đơn giản: tính thể tích box trên tổng thể tích container
        return box.volume / container.volume

    def _generate_new_extreme_points(self, box):
        # Sinh ra các điểm mới dựa trên box vừa đặt
        x, y, z = box.position['x'], box.position['y'], box.position['z']
        w, h, d = box.width, box.height, box.depth
        return [
            {"x": x + w, "y": y, "z": z},
            {"x": x, "y": y + h, "z": z},
            {"x": x, "y": y, "z": z + d}
        ]

    def _is_point_covered(self, point, points):
        # Kiểm tra xem điểm đã tồn tại chưa
        for p in points:
            if abs(p['x'] - point['x']) < 1e-3 and abs(p['y'] - point['y']) < 1e-3 and abs(p['z'] - point['z']) < 1e-3:
                return True
        return False

class SimulatedAnnealingPackingOptimizer:
    """Thuật toán Simulated Annealing cho 3D Bin Packing"""
    def __init__(self, initial_temp=1000, cooling_rate=0.95, min_temp=1):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp

    def pack(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        if not goods:
            return [], 0.0
        
        # Khởi tạo giải pháp ban đầu bằng Best Fit
        best_fit = BestFitPackingOptimizer()
        current_solution, current_utilization = best_fit.pack(goods, container_dimensions)
        best_solution = current_solution.copy()
        best_utilization = current_utilization
        
        temperature = self.initial_temp
        
        while temperature > self.min_temp:
            # Tạo giải pháp mới bằng cách hoán đổi thứ tự
            new_solution = self._generate_neighbor(current_solution, goods)
            new_utilization = self._evaluate_solution(new_solution, container_dimensions)
            
            # Tính delta E
            delta_e = new_utilization - current_utilization
            
            # Chấp nhận giải pháp mới nếu tốt hơn hoặc theo xác suất
            if delta_e > 0 or random.random() < np.exp(delta_e / temperature):
                current_solution = new_solution
                current_utilization = new_utilization
                
                # Cập nhật giải pháp tốt nhất
                if current_utilization > best_utilization:
                    best_solution = current_solution.copy()
                    best_utilization = current_utilization
            
            # Giảm nhiệt độ
            temperature *= self.cooling_rate
        
        return best_solution, best_utilization

    def _generate_neighbor(self, current_solution: List['Box'], original_goods: List['Box']) -> List['Box']:
        """Tạo giải pháp láng giềng bằng cách hoán đổi thứ tự"""
        if len(current_solution) <= 1:
            return current_solution.copy()
        
        # Tạo danh sách box chưa được sử dụng
        used_ids = {box.id for box in current_solution}
        unused_boxes = [box for box in original_goods if box.id not in used_ids]
        
        # Hoán đổi ngẫu nhiên 2 box trong giải pháp hiện tại
        if len(current_solution) >= 2:
            i, j = random.sample(range(len(current_solution)), 2)
            new_solution = current_solution.copy()
            new_solution[i], new_solution[j] = new_solution[j], new_solution[i]
        else:
            new_solution = current_solution.copy()
        
        # Thêm ngẫu nhiên một box chưa sử dụng
        if unused_boxes and random.random() < 0.3:
            new_box = random.choice(unused_boxes).clone()
            new_solution.append(new_box)
        
        return new_solution

    def _evaluate_solution(self, solution: List['Box'], container_dimensions: Dict) -> float:
        """Đánh giá giải pháp bằng cách thực hiện đóng gói"""
        if not solution:
            return 0.0
        
        container = Container(**container_dimensions)
        placed_boxes = []
        
        for box in solution:
            position = self._find_best_position(container, box)
            if position:
                x, y, z = position
                container.place_box(box, x, y, z)
                placed_boxes.append(box)
        
        return container.get_utilization()

    def _find_best_position(self, container: Container, box: 'Box') -> Optional[Tuple[float, float, float]]:
        """Tìm vị trí tốt nhất cho box trong container"""
        best_score = -1
        best_position = None
        
        for _, _, space in container.space_heap:
            for orientation in box.get_orientations():
                if (space['width'] >= orientation['width'] and
                    space['height'] >= orientation['height'] and
                    space['depth'] >= orientation['depth']):
                    
                    if container.can_place(box, space['x'], space['y'], space['z']):
                        score = self._calculate_placement_score(container, box, space['x'], space['y'], space['z'])
                        if score > best_score:
                            best_score = score
                            best_position = (space['x'], space['y'], space['z'])
        
        return best_position

    def _calculate_placement_score(self, container: Container, box: 'Box',
                                 x: float, y: float, z: float) -> float:
        """Tính điểm cho vị trí đặt box"""
        if not container.can_place(box, x, y, z):
            return -1
        
        score = 0
        
        # Điểm cho việc đặt ở góc
        if x == 0 or x + box.width == container.width:
            score += 20
        if y == 0 or y + box.height == container.height:
            score += 20
        if z == 0 or z + box.depth == container.depth:
            score += 20
        
        # Điểm cho việc sát với box khác
        for other_box in container.boxes:
            if (abs(x - (other_box.position['x'] + other_box.width)) < 1 or
                abs(other_box.position['x'] - (x + box.width)) < 1):
                score += 10
            if (abs(y - (other_box.position['y'] + other_box.height)) < 1 or
                abs(other_box.position['y'] - (y + box.height)) < 1):
                score += 10
            if (abs(z - (other_box.position['z'] + other_box.depth)) < 1 or
                abs(other_box.position['z'] - (z + box.depth)) < 1):
                score += 10
        
        return score

class PackingAlgorithm:
    def __init__(self):
        self.algorithm = "best_fit"  # Mặc định sử dụng Best Fit
        self.genetic_optimizer = ImprovedGeneticPackingOptimizer()
        self.best_fit_optimizer = BestFitPackingOptimizer()
        self.extreme_point_optimizer = ExtremePointPackingOptimizer()
        self.simulated_annealing_optimizer = SimulatedAnnealingPackingOptimizer()
    
    def pack(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        if self.algorithm == "genetic":
            return self.pack_with_genetic(goods, container_dimensions)
        elif self.algorithm == "best_fit":
            return self.pack_with_best_fit(goods, container_dimensions)
        elif self.algorithm == "extreme_point":
            return self.pack_with_extreme_point(goods, container_dimensions)
        elif self.algorithm == "simulated_annealing":
            return self.pack_with_simulated_annealing(goods, container_dimensions)
        else:
            return self.pack_simple(goods, container_dimensions)
    
    def pack_with_genetic(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        best_chromosome, best_fitness = self.genetic_optimizer.optimize(goods, container_dimensions)
        
        # Thực hiện đóng gói với chromosome tốt nhất
        container = Container(**container_dimensions)
        placed_boxes = self.genetic_optimizer.pack_chromosome(best_chromosome, container)
        
        return placed_boxes, container.get_utilization()
    
    def pack_with_best_fit(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        return self.best_fit_optimizer.pack(goods, container_dimensions)
    
    def pack_with_extreme_point(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        return self.extreme_point_optimizer.pack(goods, container_dimensions)
    
    def pack_with_simulated_annealing(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        return self.simulated_annealing_optimizer.pack(goods, container_dimensions)
    
    def pack_simple(self, goods: List['Box'], container_dimensions: Dict) -> Tuple[List['Box'], float]:
        container = Container(**container_dimensions)
        placed_boxes = []
        
        # Sắp xếp theo thể tích giảm dần
        sorted_goods = sorted(goods, key=lambda x: x.volume, reverse=True)
        
        for box in sorted_goods:
            position = self.find_best_position_simple(container, box)
            if position:
                x, y, z = position
                container.place_box(box, x, y, z)
                placed_boxes.append(box)
        
        return placed_boxes, container.get_utilization()
    
    def find_best_position_simple(self, container: Container, box: 'Box') -> Optional[Tuple[float, float, float]]:
        for _, _, space in container.space_heap:
            for orientation in box.get_orientations():
                if (space['width'] >= orientation['width'] and
                    space['height'] >= orientation['height'] and
                    space['depth'] >= orientation['depth']):
                    
                    if container.can_place(box, space['x'], space['y'], space['z']):
                        return (space['x'], space['y'], space['z'])
        
        return None
    
    def set_algorithm(self, algorithm: str) -> None:
        self.algorithm = algorithm
    
    def optimize_packing(self, goods: List['Box'], container_dimensions: Dict,
                        iterations: int = 10) -> Tuple[List['Box'], float]:
        best_result = None
        best_utilization = 0
        for i in range(iterations):
            result, utilization = self.pack(goods, container_dimensions)
            if utilization > best_utilization:
                best_utilization = utilization
                best_result = result
        return best_result or [], best_utilization

# Hàm tiện ích để tạo dữ liệu mẫu
def create_sample_goods() -> List['Box']:
    goods = [
        Box("1", 50, 30, 20, "Box A", "A", 10),
        Box("2", 40, 25, 15, "Box B", "B", 20),
        Box("3", 60, 40, 30, "Box C", "C", 5),
        Box("4", 35, 25, 20, "Box D", "D", 15),
        Box("5", 45, 35, 25, "Box E", "E", 12),
    ]
    return goods

def create_sample_container() -> Dict:
    return {"width": 200, "height": 150, "depth": 100}

# Ví dụ sử dụng
if __name__ == "__main__":
    # Tạo dữ liệu mẫu
    goods = create_sample_goods()
    container_dimensions = create_sample_container()
    
    # Khởi tạo thuật toán
    algorithm = PackingAlgorithm()
    
    # Test Best Fit Algorithm
    algorithm.set_algorithm("best_fit")
    start_time = time.time()
    placed_boxes, utilization = algorithm.pack(goods, container_dimensions)
    best_fit_time = time.time() - start_time
    
    print("Best Fit Algorithm Results:")
    print(f"Utilization: {utilization:.2f}")
    print(f"Time: {best_fit_time:.4f} seconds")
    print(f"Placed boxes: {len(placed_boxes)}/{len(goods)}")
    
    # Test Genetic Algorithm
    algorithm.set_algorithm("genetic")
    start_time = time.time()
    placed_boxes_genetic, utilization_genetic = algorithm.pack(goods, container_dimensions)
    genetic_time = time.time() - start_time
    
    print(f"\nGenetic Algorithm Results:")
    print(f"Utilization: {utilization_genetic:.2f}")
    print(f"Time: {genetic_time:.4f} seconds")
    print(f"Placed boxes: {len(placed_boxes_genetic)}/{len(goods)}") 