import { useState, useEffect } from "react";
import { packGoods } from "../../services/api";

function PackingOptimizer({ goods, containerType, containerDimensions, onOptimizedPacking }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasOptimized, setHasOptimized] = useState(false);
  const [lastInputHash, setLastInputHash] = useState("");

  useEffect(() => {
    // Tạo hash từ input để so sánh
    const createInputHash = () => {
      const goodsStr = goods ? JSON.stringify(goods.map(g => g.id + g.width + g.height + g.depth)) : "";
      const containerStr = containerDimensions ? JSON.stringify(containerDimensions) : "";
      return goodsStr + containerStr;
    };

    const currentHash = createInputHash();
    
    // Chỉ tối ưu khi dữ liệu đầu vào thay đổi
    if (!goods || goods.length === 0 || !containerDimensions) return;
    if (hasOptimized && currentHash === lastInputHash) return;

    console.log('PackingOptimizer useEffect - Dữ liệu đầu vào đã thay đổi, tối ưu lại');
    
    const autoOptimize = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log('PackingOptimizer gọi packGoods', { goods, containerDimensions });
        const result = await packGoods(goods, containerDimensions);
        console.log('PackingOptimizer: API result', result);
        if (onOptimizedPacking) {
          onOptimizedPacking(result.placed_boxes);
        }
        setHasOptimized(true);
        setLastInputHash(currentHash);
      } catch (err) {
        setError("Lỗi khi tối ưu đóng gói: " + err.message);
        console.error('PackingOptimizer: API error', err);
        if (onOptimizedPacking) onOptimizedPacking([]); // Đảm bảo callback luôn được gọi
      } finally {
        setLoading(false);
      }
    };
    autoOptimize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [goods, containerDimensions]);

  return (
    <div>
      {loading && <div>Đang tối ưu đóng gói (Backend)...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
}

export default PackingOptimizer; 