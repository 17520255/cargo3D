import React from 'react';

// Bảng màu giống GoodsList
const GOOD_COLORS = [
  '#e74c3c', // A - đỏ
  '#f1c40f', // B - vàng
  '#27ae60', // C - xanh lá
  '#2980b9', // D - xanh dương
  '#8e44ad', // E - tím
  '#e67e22', // F - cam
  '#16a085', // G - teal
  '#34495e', // H - xám đậm
];
function getGoodColor(label) {
  const idx = label && label.length > 0 ? label.charCodeAt(0) - 65 : 0;
  return GOOD_COLORS[idx % GOOD_COLORS.length];
}

function GoodsSummaryPanel({ goods, placedBoxes, onPushOne }) {
  // Tính số lượng đã xếp cho từng label
  const placedCountByLabel = {};
  if (placedBoxes) {
    placedBoxes.forEach(box => {
      if (!placedCountByLabel[box.label]) placedCountByLabel[box.label] = 0;
      placedCountByLabel[box.label]++;
    });
  }

  // Gom nhóm
  const goodsPriority = goods.filter(g => g.group === '1');
  const goodsNormal = goods.filter(g => g.group === '2');

  // Render 1 dòng hàng với cải thiện UI
  const renderRow = (g) => {
    const placed = placedCountByLabel[g.label] || 0;
    let status = 'enough';
    if (placed < g.quantity) status = 'not-enough';
    if (placed > g.quantity) status = 'over';
    
    return (
      <div 
        key={g.label} 
        className="summary-row"
        style={{
          display: 'flex',
          alignItems: 'center',
          margin: '4px 0',
          fontSize: 13,
          padding: '4px 8px',
          borderRadius: 6,
          transition: 'all 0.2s ease'
        }}
      >
        <span style={{
          width: 38,
          textAlign: 'right',
          fontVariant: 'tabular-nums',
          fontWeight: 600,
          color: '#333'
        }}>
          {placed}/{g.quantity}
        </span>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 24,
          height: 24,
          borderRadius: 6,
          background: getGoodColor(g.label),
          color: '#fff',
          fontWeight: 700,
          fontSize: 13,
          margin: '0 8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
        }}>
          {g.label}
        </span>
        
        {/* Status indicators với cải thiện */}
        {status === 'enough' && (
          <span className="status-indicator status-packed" title="Đã xếp đủ"></span>
        )}
        {status === 'not-enough' && (
          <span className="status-indicator status-partial" title="Chưa xếp đủ"></span>
        )}
        {status === 'over' && (
          <span className="status-indicator status-unpacked" title="Xếp quá số lượng"></span>
        )}
        
        {/* Nút mũi tên với cải thiện */}
        <button
          className="arrow-btn"
          style={{
            marginLeft: 'auto',
            background: 'none',
            border: 'none',
            cursor: placed < g.quantity ? 'pointer' : 'not-allowed',
            fontSize: 20,
            color: placed < g.quantity ? '#28a745' : '#ccc',
            padding: '2px 4px',
            borderRadius: 4,
            fontWeight: 900,
            opacity: placed < g.quantity ? 1 : 0.5,
            transition: 'all 0.2s ease'
          }}
          title={placed < g.quantity ? "Đẩy thêm 1 kiện vào container" : "Đã xếp đủ số lượng"}
          disabled={placed >= g.quantity}
          onClick={() => onPushOne && onPushOne(g.label)}
        >
          &#8594;
        </button>
      </div>
    );
  };

  return (
    <div className="summary-panel" style={{
      position: 'fixed',
      top: 90,
      left: 24,
      minWidth: 260,
      borderRadius: 16,
      padding: '20px 24px',
      zIndex: 100,
      boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
      border: '1px solid rgba(255,255,255,0.3)',
      fontFamily: 'inherit',
      backdropFilter: 'blur(15px)',
      maxHeight: '70vh',
      overflowY: 'auto'
    }}>
      {/* Header với gradient */}
      <div style={{
        marginBottom: 16,
        padding: '12px 16px',
        borderRadius: 12,
        background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
        color: 'white',
        fontWeight: 700,
        fontSize: 16,
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(255,107,107,0.3)'
      }}>
        🚀 Nhóm ưu tiên
      </div>
      
      {goodsPriority.length === 0 ? (
        <div style={{
          color: '#bbb',
          fontStyle: 'italic',
          textAlign: 'center',
          padding: '20px',
          fontSize: 14
        }}>
          Không có hàng hóa
        </div>
      ) : (
        goodsPriority.map(renderRow)
      )}
      
      <div style={{
        margin: '20px 0 16px 0',
        padding: '12px 16px',
        borderRadius: 12,
        background: 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)',
        color: 'white',
        fontWeight: 700,
        fontSize: 16,
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(78,205,196,0.3)'
      }}>
        📦 Nhóm thường
      </div>
      
      {goodsNormal.length === 0 ? (
        <div style={{
          color: '#bbb',
          fontStyle: 'italic',
          textAlign: 'center',
          padding: '20px',
          fontSize: 14
        }}>
          Không có hàng hóa
        </div>
      ) : (
        goodsNormal.map(renderRow)
      )}
      
      {/* Footer với thông tin tổng quan */}
      <div style={{
        marginTop: 16,
        padding: '12px 16px',
        borderRadius: 12,
        background: 'rgba(40,167,69,0.1)',
        border: '1px solid rgba(40,167,69,0.2)',
        fontSize: 13,
        color: '#666'
      }}>
        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 4}}>
          <span>Tổng hàng hóa:</span>
          <span style={{fontWeight: 600}}>{goods.length}</span>
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          <span>Đã xếp:</span>
          <span style={{fontWeight: 600, color: '#28a745'}}>
            {Object.values(placedCountByLabel).reduce((sum, count) => sum + count, 0)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default GoodsSummaryPanel; 