from fastapi import APIRouter, HTTPException
from app.api.models.schemas import PackingRequest, PackingResponse
from app.services.packing_service import pack_goods_service
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/pack", response_model=PackingResponse)
async def pack_goods(request: PackingRequest):
    try:
        logger.info(f"Received packing request with {len(request.goods)} goods")
        result = pack_goods_service(request)
        logger.info("Packing completed successfully")
        return result
    except Exception as e:
        # Log the full error with traceback
        error_msg = f"Error in pack_goods: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg) 