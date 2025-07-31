import './styles/App.css';
import { useState, useCallback, useEffect, useMemo } from 'react';
import GoodsList from './components/ui/GoodsList';
import Container3D from './components/3d/Container3D';
import ContainerSelector from './components/ui/ContainerSelector';
import PackingOptimizer from './components/ui/PackingOptimizer';
import { useRef } from 'react';
import GoodsSummaryPanel from './components/ui/GoodsSummaryPanel';

// Dữ liệu các loại container (đồng bộ với ContainerSelector)
const CONTAINER_TYPES = {
  '20ft-standard': {
    name: '20ft Standard',
    dimensions: { width: 2.352, height: 2.385, depth: 5.758 },
    maxVolume: 32.3,
    maxWeight: 28200,
    color: '#4a90e2'
  },
  '20ft-dc': {
    name: "20ft DC",
    dimensions: { width: 2.34, height: 2.38, depth: 5.919 },
    maxVolume: 32.96,
    maxWeight: 22100,
    color: '#abc888'
  },
  '20ft-hc': {
    name: "20ft HC",
    dimensions: { width: 2.352, height: 2.684, depth: 5.758 },
    maxVolume: 36.35,
    maxWeight: 29200,
    color: '#ff5522'
  },
  '40ft-standard': {
    name: '40ft Standard',
    dimensions: { width: 2.352, height: 2.385, depth: 12.032 },
    maxVolume: 67.49,
    maxWeight: 26600,
    color: '#ffaabb'
  },
  '40ft-dc': {
    name: "40ft DC",
    dimensions: { width: 2.34, height: 2.38, depth: 12.051 },
    maxVolume: 67.11,
    maxWeight: 27397,
    color: '#28a745'
  },
  '40ft-hc': {
    name: "40ft HC",
    dimensions: { width: 2.34, height: 2.694, depth: 12.117 },
    maxVolume: 76.385,
    maxWeight: 29600,
    color: '#ffc107'
  },
  '45ft-hc': {
    name: "45ft HC",
    dimensions: { width: 2.347, height: 2.69, depth: 13.582 },
    maxVolume: 85.75,
    maxWeight: 28390,
    color: '#6f42c1'
  }
};

function App() {
  const [goods, setGoods] = useState([]); // Bắt đầu với mảng rỗng, không có dữ liệu mẫu
  const [selectedGood, setSelectedGood] = useState(null);
  const [selectedContainer, setSelectedContainer] = useState('20ft-standard');
  const [optimizedBoxes, setOptimizedBoxes] = useState(null);
  const [showOptimized, setShowOptimized] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showContainerPanel, setShowContainerPanel] = useState(false);
  const [isPacking, setIsPacking] = useState(false); // Trạng thái đã bấm nút 'Chất Hàng'
  const [isOptimizing, setIsOptimizing] = useState(false); // Trạng thái đang tối ưu hóa
  const [pushedCounts, setPushedCounts] = useState({}); // {label: số kiện đã đẩy}
  const [isBoxSelected, setIsBoxSelected] = useState(false); // Trạng thái có kiện hàng được chọn
  const [boxRotations, setBoxRotations] = useState({}); // {boxId: rotationAngle}
  const [removedBoxIds, setRemovedBoxIds] = useState(new Set()); // Set các ID kiện hàng đã bị xóa
  const controlsRef = useRef();
  
  // Debug: theo dõi thay đổi của boxRotations
  useEffect(() => {
    console.log('boxRotations thay đổi:', boxRotations);
  }, [boxRotations]);

  // Hàm điều khiển góc nhìn camera
  const handleSetView = (view) => {
    if (!controlsRef.current) return;
    let pos, target = [0, 1, 0];
    switch (view) {
      case 'front':
        pos = [12, 8, 8];
        break;
      case 'back':
        pos = [-12, 8, 8]; // nhìn từ phải qua trái
        break;
      case 'top':
        pos = [0, 50, 0.01];
        break;
      case 'left':
        pos = [12, 8, 8];
        break;
      default:
        pos = [12, 8, 8];
    }
    // Đặt vị trí camera và target
    controlsRef.current.object.position.set(...pos);
    controlsRef.current.target.set(...target);
    controlsRef.current.update();
  };

  // Hàm sinh ký hiệu theo thứ tự A, B, ..., Z, AA, AB, ...
  function getNextLabel(existingGoods) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const n = existingGoods.length;
    let label = '';
    let num = n;
    do {
      label = alphabet[num % 26] + label;
      num = Math.floor(num / 26) - 1;
    } while (num >= 0);
    return label;
  }

  // Hàm nhân bản hàng hóa theo quantity
  function expandGoods(goods) {
    const expanded = [];
    goods.forEach(good => {
      for (let i = 0; i < good.quantity; i++) {
        expanded.push({
          ...good,
          id: `${good.id}_${i}`,
        });
      }
    });
    return expanded;
  }

  const addGood = (good) => {
    const label = getNextLabel(goods);
    setGoods((prev) => [
      ...prev,
      { ...good, id: Date.now(), label },
    ]);
    // Reset optimization khi thêm hàng mới
    setOptimizedBoxes(null);
    setShowOptimized(false);
  };

  // Hàm thêm nhiều hàng hóa một lần (import excel), sinh label đúng quy tắc nối tiếp
  const addGoodsBulk = (goodsArray) => {
    setGoods(prevGoods => {
      const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
      let n = prevGoods.length;
      const newGoods = goodsArray.map(good => {
        // Sinh label nối tiếp
        let label = '';
        let num = n;
        do {
          label = alphabet[num % 26] + label;
          num = Math.floor(num / 26) - 1;
        } while (num >= 0);
        n++;
        return { ...good, id: Date.now() + Math.random(), label };
      });
      // Reset optimization khi thêm hàng mới
      setOptimizedBoxes(null);
      setShowOptimized(false);
      return [...prevGoods, ...newGoods];
    });
  };

  const editGood = (updatedGood) => {
    setGoods((prev) => prev.map(g => g.id === updatedGood.id ? { ...updatedGood } : g));
    setOptimizedBoxes(null);
    setShowOptimized(false);
  };

  const handleBoxClick = (box) => {
    setSelectedGood(box);
    setIsBoxSelected(true);
  };

  const removeGood = (id) => {
    setGoods((prev) => prev.filter(g => g.id !== id));
    if (selectedGood && selectedGood.id === id) {
      setSelectedGood(null);
    }
    // Reset optimization khi xóa hàng
    setOptimizedBoxes(null);
    setShowOptimized(false);
  };

  const handleContainerChange = (containerType) => {
    setSelectedContainer(containerType);
    // Reset optimization khi thay đổi container
    setOptimizedBoxes(null);
    setShowOptimized(false);
  };

  const handleOptimizedPacking = useCallback((placedBoxes) => {
    console.log('handleOptimizedPacking callback:', placedBoxes);
    // Lọc ra các kiện hàng đã bị xóa
    const filteredBoxes = placedBoxes.filter(box => !removedBoxIds.has(box.id));
    console.log('handleOptimizedPacking - original:', placedBoxes.length, 'filtered:', filteredBoxes.length, 'removed:', removedBoxIds.size);
    setOptimizedBoxes(filteredBoxes);
    setShowOptimized(true);
    setIsOptimizing(false); // Kết thúc trạng thái tối ưu hóa
  }, [removedBoxIds]);

  const toggleOptimizedView = () => {
    setShowOptimized(!showOptimized);
  };

  // Khi bấm nút 'Chất Hàng'
  const handleStartPacking = () => {
    setIsPacking(true);
    setIsOptimizing(true); // Bắt đầu trạng thái tối ưu hóa
    setShowOptimized(true);
    setSelectedGood(null);
    setIsBoxSelected(false);
    setBoxRotations({});
    setRemovedBoxIds(new Set());
  };

  // Hàm xử lý khi click mũi tên đẩy 1 kiện vào container
  const handlePushOne = (label) => {
    setIsPacking(true);
    setShowOptimized(true);
    setPushedCounts(prev => ({
      ...prev,
      [label]: (prev[label] || 0) + 1
    }));
  };

  // Tạo goods cho packing theo pushedCounts
  function getPushedGoods() {
    if (!isPacking || Object.keys(pushedCounts).length === 0) return [];
    const result = [];
    goods.forEach(good => {
      const count = pushedCounts[good.label] || 0;
      for (let i = 0; i < count && i < good.quantity; i++) {
        result.push({ ...good, id: `${good.id}_push_${i}` });
      }
    });
    return result;
  }

  // Reset pushedCounts khi trả hàng
  const handleResetPacking = () => {
    setIsPacking(false);
    setIsOptimizing(false); // Reset trạng thái tối ưu hóa
    setShowOptimized(false);
    setPushedCounts({});
    setSelectedGood(null);
    setIsBoxSelected(false);
    setBoxRotations({});
    setRemovedBoxIds(new Set());
  };

  // Hàm kiểm tra va chạm với container và các kiện hàng khác
  const checkContainerCollision = useCallback((box, rotation, containerDimensions, otherBoxes = []) => {
    // Tính toán kích thước thực tế của box sau khi xoay
    let boxWidth, boxDepth;
    if (rotation === 0 || rotation === 180) {
      boxWidth = box.width;
      boxDepth = box.depth;
    } else {
      boxWidth = box.depth;
      boxDepth = box.width;
    }

    // Kiểm tra xem box có vượt ra ngoài container không
    const halfBoxWidth = boxWidth / 2;
    const halfBoxDepth = boxDepth / 2;
    const halfContainerWidth = containerDimensions.width / 2;
    const halfContainerDepth = containerDimensions.depth / 2;

    // Tính toán vị trí hiện tại của box trong hệ tọa độ container
    // position = [box.position.x - container.dimensions.width/2 + box.width/2, ...]
    const boxX = box.position ? box.position.x : 0;
    const boxZ = box.position ? box.position.z : 0;

    // Chuyển đổi về hệ tọa độ container (container center = 0,0)
    const containerBoxX = boxX - containerDimensions.width/2 + box.width/2;
    const containerBoxZ = boxZ - containerDimensions.depth/2 + box.depth/2;

    // Kiểm tra va chạm
    const leftEdge = containerBoxX - halfBoxWidth;
    const rightEdge = containerBoxX + halfBoxWidth;
    const frontEdge = containerBoxZ - halfBoxDepth;
    const backEdge = containerBoxZ + halfBoxDepth;

    const containerLeft = -halfContainerWidth;
    const containerRight = halfContainerWidth;
    const containerFront = -halfContainerDepth;
    const containerBack = halfContainerDepth;

    // Nếu có va chạm với container, trả về false
    if (leftEdge < containerLeft || rightEdge > containerRight || 
        frontEdge < containerFront || backEdge > containerBack) {
      return false;
    }

    // Kiểm tra va chạm với các kiện hàng khác
    for (const otherBox of otherBoxes) {
      if (otherBox.id === box.id) continue;
      const otherRotation = boxRotations[otherBox.id] || 0;
      let otherBoxWidth, otherBoxDepth;
      if (otherRotation === 0 || otherRotation === 180) {
        otherBoxWidth = otherBox.width;
        otherBoxDepth = otherBox.depth;
      } else {
        otherBoxWidth = otherBox.depth;
        otherBoxDepth = otherBox.width;
      }
      const otherBoxX = otherBox.position ? otherBox.position.x : 0;
      const otherBoxZ = otherBox.position ? otherBox.position.z : 0;
      const otherContainerBoxX = otherBoxX - containerDimensions.width/2 + otherBox.width/2;
      const otherContainerBoxZ = otherBoxZ - containerDimensions.depth/2 + otherBox.depth/2;
      const otherLeftEdge = otherContainerBoxX - otherBoxWidth/2;
      const otherRightEdge = otherContainerBoxX + otherBoxWidth/2;
      const otherFrontEdge = otherContainerBoxZ - otherBoxDepth/2;
      const otherBackEdge = otherContainerBoxZ + otherBoxDepth/2;
      if (!(rightEdge < otherLeftEdge || leftEdge > otherRightEdge || 
            backEdge < otherFrontEdge || frontEdge > otherBackEdge)) {
        return false;
      }
    }
    return true;
  }, [boxRotations]);

  // Hàm xử lý khi click nút "Xoay"
  const handleRotateBox = useCallback(() => {
    console.log('handleRotateBox được gọi, selectedGood:', selectedGood);
    if (selectedGood) {
      const currentRotation = boxRotations[selectedGood.id] || 0;
      const newRotation = (currentRotation + 90) % 360; // Xoay 90 độ sang phải
      
      console.log('Xoay kiện hàng:', selectedGood.id, 'từ', currentRotation, 'đến', newRotation);
      console.log('boxRotations trước:', boxRotations);
      
      // Kiểm tra va chạm với container trước khi xoay
      const container = CONTAINER_TYPES[selectedContainer];
      const otherBoxes = optimizedBoxes ? optimizedBoxes.filter(box => box.id !== selectedGood.id) : [];
      const canRotate = checkContainerCollision(selectedGood, newRotation, container.dimensions, otherBoxes);
      
      if (!canRotate) {
        console.log('Không thể xoay - sẽ vượt ra ngoài container');
        // Có thể hiển thị thông báo cho người dùng
        alert('Không thể xoay kiện hàng này - sẽ vượt ra ngoài container!');
        return;
      }
      
      setBoxRotations(prev => {
        const newRotations = {
          ...prev,
          [selectedGood.id]: newRotation
        };
        console.log('boxRotations sau:', newRotations);
        return newRotations;
      });
      
      // Cập nhật trong danh sách optimizedBoxes nếu có
      if (optimizedBoxes) {
        const updatedBoxes = optimizedBoxes.map(box => 
          box.id === selectedGood.id 
            ? { ...box, rotation: newRotation }
            : box
        );
        setOptimizedBoxes(updatedBoxes);
      }
      
      // Đảm bảo trạng thái được chọn vẫn duy trì
      console.log('Giữ nguyên trạng thái selectedGood:', selectedGood);
    } else {
      console.log('Không có selectedGood');
    }
  }, [selectedGood, boxRotations, optimizedBoxes, selectedContainer, checkContainerCollision]);

  // Hàm xử lý khi click nút "Trả Kiện Hàng Này"
  const handleReturnSelectedBox = useCallback(() => {
    console.log('handleReturnSelectedBox được gọi, selectedGood:', selectedGood);
    if (selectedGood) {
      console.log('Xóa kiện hàng:', selectedGood.id);
      
      // Thêm ID vào danh sách đã xóa
      setRemovedBoxIds(prev => new Set([...prev, selectedGood.id]));
      
      // Xóa kiện hàng đã chọn khỏi danh sách đã xếp
      if (optimizedBoxes) {
        const updatedBoxes = optimizedBoxes.filter(box => box.id !== selectedGood.id);
        console.log('optimizedBoxes trước:', optimizedBoxes.length, 'sau:', updatedBoxes.length);
        setOptimizedBoxes(updatedBoxes);
      }
      
      // Xóa rotation của kiện hàng này
      setBoxRotations(prev => {
        const newRotations = { ...prev };
        delete newRotations[selectedGood.id];
        console.log('Xóa rotation cho kiện hàng:', selectedGood.id);
        return newRotations;
      });
      
      // Reset trạng thái được chọn
      setSelectedGood(null);
      setIsBoxSelected(false);
      
      console.log('Đã xóa kiện hàng và reset trạng thái');
    } else {
      console.log('Không có selectedGood để xóa');
    }
  }, [selectedGood, optimizedBoxes]);

  // Tính toán thông tin container và hàng hóa
  const container = CONTAINER_TYPES[selectedContainer];
  const totalVolume = goods.reduce((sum, g) => sum + g.width * g.height * g.depth, 0);
  const usedVolume = (isPacking && showOptimized && optimizedBoxes)
    ? optimizedBoxes.reduce((sum, g) => sum + g.width * g.height * g.depth, 0)
    : 0;
  const usageRatio = ((usedVolume / container.maxVolume) * 100).toFixed(1);
  const remainingVolume = (container.maxVolume - usedVolume).toFixed(2);

  // Trước khi render PackingOptimizer
  console.log('PackingOptimizer props:', {
    goods: Object.keys(pushedCounts).length > 0 ? getPushedGoods() : expandGoods(goods),
    containerType: selectedContainer,
    containerDimensions: container.dimensions
  });

  return (
    <div style={{width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden'}}>
      {/* Vùng 3D full màn hình */}
      <div style={{position: 'absolute', inset: 0, width: '100vw', height: '100vh', zIndex: 1}}>
        <Container3D 
          goods={isPacking ? (showOptimized ? [] : goods) : []}
          onBoxClick={handleBoxClick} 
          containerType={selectedContainer}
          optimizedBoxes={isPacking && showOptimized ? optimizedBoxes : null}
          setView={handleSetView}
          controlsRef={controlsRef}
          setIsBoxSelected={setIsBoxSelected}
          boxRotations={boxRotations}
        />
        {console.log('App render - boxRotations:', boxRotations)}
        {console.log('App render - isPacking:', isPacking, 'showOptimized:', showOptimized, 'optimizedBoxes length:', optimizedBoxes?.length)}
      </div>

      {/* Nút mở sidebar trái với cải thiện UI */}
      <button
        className="control-btn"
        style={{
          position: 'fixed', 
          top: 24, 
          left: 24, 
          zIndex: 20, 
          width: 44, 
          height: 44, 
          borderRadius: 12, 
          border: '1px solid rgba(255,255,255,0.2)', 
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)', 
          cursor: 'pointer', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backdropFilter: 'blur(10px)'
        }}
        onClick={() => setShowSidebar(v => !v)}
        title="Danh sách hàng hóa"
      >
        <span style={{fontSize: 26, fontWeight: 700, color: '#666'}}>&#9776;</span>
      </button>

      {/* Nút mở/đóng panel container phải với cải thiện UI */}
      <button
        className="control-btn"
        style={{
          position: 'fixed', 
          top: 24, 
          right: 24, 
          zIndex: 40, 
          width: 44, 
          height: 44, 
          borderRadius: 12, 
          border: '1px solid rgba(255,255,255,0.2)', 
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)', 
          cursor: 'pointer', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backdropFilter: 'blur(10px)'
        }}
        onClick={() => setShowContainerPanel(v => !v)}
        title={showContainerPanel ? 'Đóng panel' : 'Chọn container'}
      >
        {showContainerPanel ? (
          <span style={{fontSize: 24, fontWeight: 700, color: '#888'}}>&times;</span>
        ) : (
          <span style={{fontSize: 22, fontWeight: 700, color: '#666'}}>&#128230;</span>
        )}
      </button>

      {/* Nút điều khiển với cải thiện UI */}
      {!showContainerPanel && (
        <div style={{ position: 'fixed', right: 32, bottom: 32, zIndex: 50, display: 'flex', gap: 16 }}>
          {!isBoxSelected ? (
            // Hiển thị nút "Chất Hàng" và "Trả Hàng" khi không có kiện hàng được chọn
            <>
              <button
                className="btn-primary"
                style={{
                  padding: '18px 36px',
                  borderRadius: 16,
                  fontSize: 20,
                  letterSpacing: 1.5,
                  boxShadow: '0 8px 25px rgba(40,167,69,0.3)',
                }}
                onClick={handleStartPacking}
                disabled={goods.length === 0 || isPacking}
                title={goods.length === 0 ? 'Thêm hàng hóa trước khi chất hàng' : (isPacking ? 'Đã chất hàng' : 'Chất Hàng')}
              >
                {isOptimizing ? '🔄 Đang tối ưu...' : (isPacking ? 'Đã Chất Hàng' : 'Chất Hàng')}
              </button>
              <button
                className="btn-danger"
                style={{
                  padding: '18px 36px',
                  borderRadius: 16,
                  fontSize: 20,
                  letterSpacing: 1.5,
                  boxShadow: '0 8px 25px rgba(220,53,69,0.3)',
                  opacity: isPacking ? 1 : 0.6,
                }}
                onClick={handleResetPacking}
                disabled={!isPacking}
                title={!isPacking ? 'Chưa chất hàng' : 'Trả hàng về danh sách'}
              >
                Trả Hàng
              </button>
            </>
          ) : (
            // Hiển thị nút "Xoay" và "Trả Kiện Hàng Này" khi có kiện hàng được chọn
            <>
              <button
                className="btn-primary"
                style={{
                  padding: '18px 36px',
                  borderRadius: 16,
                  fontSize: 20,
                  letterSpacing: 1.5,
                  boxShadow: '0 8px 25px rgba(40,167,69,0.3)',
                }}
                onClick={handleRotateBox}
                title="Xoay kiện hàng đã chọn"
              >
                🔄 Xoay
              </button>
              <button
                className="btn-danger"
                style={{
                  padding: '18px 36px',
                  borderRadius: 16,
                  fontSize: 20,
                  letterSpacing: 1.5,
                  boxShadow: '0 8px 25px rgba(220,53,69,0.3)',
                }}
                onClick={handleReturnSelectedBox}
                title="Trả kiện hàng này về danh sách"
              >
                📦 Trả Kiện Hàng Này
              </button>
            </>
          )}
        </div>
      )}

      {/* Sidebar trái overlay với cải thiện UI */}
      {showSidebar && (
        <div className="summary-panel" style={{
          position: 'fixed', 
          top: 0, 
          left: 0, 
          bottom: 0, 
          width: 340, 
          boxShadow: '4px 0 24px rgba(0,0,0,0.15)', 
          zIndex: 30, 
          padding: 0, 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: '0 16px 16px 0'
        }}>
          <div style={{
            padding: 24, 
            borderBottom: '1px solid rgba(0,0,0,0.1)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '0 16px 0 0'
          }}>
            <span style={{fontWeight: 700, fontSize: 18}}>📦 Danh sách hàng hóa</span>
            <button 
              onClick={() => setShowSidebar(false)} 
              style={{
                background: 'rgba(255,255,255,0.2)', 
                border: 'none', 
                fontSize: 20, 
                cursor: 'pointer', 
                color: 'white',
                borderRadius: '50%',
                width: 32,
                height: 32,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease'
              }}
            >
              &times;
            </button>
          </div>
          <div style={{flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '16px 0'}}>
            <GoodsList goods={goods} onAdd={addGood} onAddBulk={addGoodsBulk} onRemove={removeGood} onEdit={editGood} />
          </div>
        </div>
      )}

      {/* Panel chọn container phải overlay với cải thiện UI */}
      {showContainerPanel && (
        <div className="summary-panel" style={{
          position: 'fixed', 
          top: 88, 
          right: 0, 
          height: 'calc(100vh - 88px)', 
          width: 420, 
          boxShadow: '-4px 0 24px rgba(0,0,0,0.15)', 
          zIndex: 30, 
          padding: 0, 
          display: 'flex', 
          flexDirection: 'column', 
          overflowX: 'hidden',
          borderRadius: '16px 0 0 16px'
        }}>
          <div style={{
            padding: 20,
            borderBottom: '1px solid rgba(0,0,0,0.1)',
            background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
            color: 'white',
            borderRadius: '16px 0 0 0'
          }}>
            <h3 style={{margin: 0, fontWeight: 700}}>🚢 Chọn Container</h3>
          </div>
          <div style={{flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '16px 0'}}>
        <ContainerSelector 
          selectedContainer={selectedContainer}
          onContainerChange={handleContainerChange}
        />
          </div>
        </div>
      )}

      {/* Panel thông tin container nhỏ gọn với cải thiện UI */}
      <div className="summary-panel" style={{
        position: 'fixed', 
        top: 88, 
        right: showContainerPanel ? 444 : 84, 
        zIndex: 30, 
        borderRadius: 16, 
        padding: '16px 20px', 
        minWidth: 240, 
        transition: 'right 0.3s ease',
        boxShadow: '0 8px 32px rgba(0,0,0,0.15)'
      }}>
        <div style={{
          fontWeight: 700, 
          fontSize: 18, 
          color: container.color,
          marginBottom: 8
        }}>
          {container.name}
        </div>
        <div style={{fontSize: 13, color: '#666', marginBottom: 6}}>
          📏 ({container.dimensions.width} × {container.dimensions.height} × {container.dimensions.depth} m)
        </div>
        <div style={{fontSize: 13, color: '#888', marginBottom: 4}}>
          ⚖️ Tải trọng: <span style={{color: '#333', fontWeight: 700}}>{container.maxWeight.toLocaleString()} kg</span>
        </div>
        <div style={{fontSize: 13, color: '#888', marginBottom: 4}}>
          📦 Đã xếp: <span style={{color: '#333'}}>{usedVolume.toFixed(2)} m³</span> / {container.maxVolume} m³
        </div>
        <div style={{fontSize: 13, color: '#888'}}>
          📊 Tỷ lệ: <span style={{color: '#28a745', fontWeight: 700}}>{usageRatio}%</span>
        </div>
      </div>
        
      {/* PackingOptimizer - chỉ hiển thị khi cần thiết */}
      {isPacking && (
        <PackingOptimizer 
          goods={Object.keys(pushedCounts).length > 0 ? getPushedGoods() : expandGoods(goods)}
          containerType={selectedContainer}
          containerDimensions={container.dimensions}
          onOptimizedPacking={handleOptimizedPacking}
        />
      )}

      {/* Hiển thị bảng tóm tắt khi sidebar bị đóng với cải thiện UI */}
      {!showSidebar && (
        <GoodsSummaryPanel
          goods={goods}
          placedBoxes={isPacking && showOptimized ? optimizedBoxes : []}
          onPushOne={handlePushOne}
        />
      )}
    </div>
  );
}

export default App;
