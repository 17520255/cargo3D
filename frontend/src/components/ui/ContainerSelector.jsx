import { useState } from 'react';

// Dữ liệu các loại container
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
    dimensions: { width: 2.34, height: 2.69, depth: 12.1 },
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

function ContainerSelector({ selectedContainer, onContainerChange }) {
  const [isOpen, setIsOpen] = useState(false);

  const currentContainer = CONTAINER_TYPES[selectedContainer];

  return (
    <div className="container-selector">
      {/* Container hiện tại */}
      <div className="current-container" onClick={() => setIsOpen(!isOpen)}>
        <div className="container-info">
          <h4>{currentContainer.name}</h4>
          <p>{currentContainer.description}</p>
          <div className="container-specs">
            <span>Kích thước: {currentContainer.dimensions.width} × {currentContainer.dimensions.height} × {currentContainer.dimensions.depth} m</span>
            <span>Thể tích: {currentContainer.maxVolume} m³</span>
            <span>Tải trọng: {currentContainer.maxWeight.toLocaleString()} kg</span>
          </div>
        </div>
        <div className="container-preview" style={{ backgroundColor: currentContainer.color }}>
          <div className="container-icon">📦</div>
        </div>
        <button className="select-btn">
          {isOpen ? '▼' : '▶'}
        </button>
      </div>

      {/* Dropdown danh sách container */}
      {isOpen && (
        <div className="container-dropdown">
          {Object.entries(CONTAINER_TYPES).map(([key, container]) => (
            <div
              key={key}
              className={`container-option ${selectedContainer === key ? 'selected' : ''}`}
              onClick={() => {
                onContainerChange(key);
                setIsOpen(false);
              }}
            >
              <div className="option-info">
                <h5>{container.name}</h5>
                <p>{container.description}</p>
                <div className="option-specs">
                  <span>{container.dimensions.width}×{container.dimensions.height}×{container.dimensions.depth}m</span>
                  <span>{container.maxVolume}m³</span>
                  <span>{container.maxWeight.toLocaleString()}kg</span>
                </div>
              </div>
              <div className="option-preview" style={{ backgroundColor: container.color }}>
                <div className="container-icon">📦</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ContainerSelector; 