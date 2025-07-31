from app.api.models.schemas import PackingRequest, PackingResponse
from algorithms.enhanced_packing_algorithm import Box, EnhancedPackingAlgorithm
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

def pack_goods_service(request: PackingRequest):
    try:
        logger.info("Starting packing service...")
        goods = [Box(**box.model_dump()) for box in request.goods]
        logger.info(f"Created {len(goods)} boxes from request")
        
        container = request.container.model_dump()
        logger.info(f"Container dimensions: {container}")
        
        # Lấy thông số từ request
        time_limit = getattr(request, 'time_limit', 90)  # Tăng thời gian mặc định lên 90 giây
        respect_groups = getattr(request, 'respect_groups', True)  # Mặc định tôn trọng nhóm
        
        logger.info(f"Using time limit: {time_limit}s, respect_groups: {respect_groups}")

        # Sử dụng thuật toán đóng gói nâng cao
        start_time = time.time()
        
        logger.info("Starting Enhanced Packing Algorithm...")
        packing_algo = EnhancedPackingAlgorithm()
        
        # Sử dụng ngưỡng hỗ trợ tối ưu từ kết quả kiểm tra
        packing_algo.support_threshold = 0.7  # Ngưỡng hỗ trợ tối ưu
        logger.info(f"Using support threshold: {packing_algo.support_threshold}")
        
        placed_boxes, utilization = packing_algo.optimize_packing(
            goods, 
            container, 
            respect_groups=respect_groups,
            time_limit=time_limit
        )
        
        logger.info(f"Packing completed with {len(placed_boxes)}/{len(goods)} boxes placed")
        logger.info(f"Utilization: {utilization:.2%}")
        
        total_volume = container["width"] * container["height"] * container["depth"]
        used_volume = sum([b.volume for b in placed_boxes])
        exec_time = time.time() - start_time
        
        logger.info(f"Packing completed in {exec_time:.2f} seconds")
        logger.info(f"Total volume: {total_volume}, Used volume: {used_volume}")
        
        # Kiểm tra xem đã đạt mục tiêu 80% chưa
        target_utilization = 0.8
        if utilization < target_utilization:
            logger.warning(f"Utilization {utilization:.2%} is below target {target_utilization:.2%}")
        else:
            logger.info(f"Target utilization of {target_utilization:.2%} achieved ✓")
        
        return PackingResponse(
            placed_boxes=[b.__dict__ for b in placed_boxes],
            utilization=utilization,
            total_volume=total_volume,
            used_volume=used_volume,
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"Error in pack_goods_service: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise 