import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text, Box, Grid, Environment, useTexture } from '@react-three/drei';
import { useState, useRef, useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useThree, useFrame } from '@react-three/fiber';
import React from "react";

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
    color: '#4a90e2'
  },
  '20ft-hc': {
    name: "20ft HC",
    dimensions: { width: 2.352, height: 2.684, depth: 5.758 },
    maxVolume: 36.35,
    maxWeight: 29200,
    color: '#4a90e2'
  },
  '40ft-standard': {
    name: '40ft Standard',
    dimensions: { width: 2.352, height: 2.385, depth: 12.032 },
    maxVolume: 67.49,
    maxWeight: 26600,
    color: '#28a745'
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

// Định nghĩa màu sắc cho từng loại hàng (A, B, C, ...)
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

// Hàm giảm độ sáng màu hex
function darkenColor(hex, amount = 0.6) {
  let col = hex.replace('#', '');
  if (col.length === 3) col = col.split('').map(x => x + x).join('');
  const num = parseInt(col, 16);
  let r = ((num >> 16) & 0xFF) * amount;
  let g = ((num >> 8) & 0xFF) * amount;
  let b = (num & 0xFF) * amount;
  r = Math.round(r);
  g = Math.round(g);
  b = Math.round(b);
  return `rgb(${r},${g},${b})`;
}

// Hàm tạo texture canvas với màu nền và viền đen
function createBoxTexture(color = '#e74c3c') {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = darkenColor(color, 0.7); // giảm sáng 30%
  ctx.fillRect(0, 0, 512, 512);
  ctx.strokeStyle = 'black';
  ctx.lineWidth = 2;
  ctx.strokeRect(1, 1, 512 - 2, 512 - 2);
  return new THREE.CanvasTexture(canvas);
}

function GoodsBox({ box, onBoxClick, container, optimized, selected, rotation = 0 }) {
  const boxColor = getGoodColor(box.label);
  // Tạo texture chỉ khi boxColor thay đổi
  const boxTexture = useMemo(() => createBoxTexture(boxColor), [boxColor]);
  
  // Tính vị trí
  let position;
  if (optimized && box.position) {
    position = [
      box.position.x - container.dimensions.width/2 + box.width/2,  // X axis = width
      box.position.y + box.height/2,                               // Y axis = height  
      box.position.z - container.dimensions.depth/2 + box.depth/2  // Z axis = depth
    ];
  } else {
    position = [-container.dimensions.width/2 + box.index * 0.6, box.height/2, 0];
  }
  return (
    <group key={`${box.id}-${rotation}`} position={position}>
      {/* Viền vàng nổi bật nếu được chọn */}
      {selected && (
        <mesh rotation={[0, (rotation * Math.PI) / 180, 0]}>
          <boxGeometry args={[box.width, box.height, box.depth]} />
          <meshBasicMaterial color="yellow" transparent opacity={1} />
        </mesh>
      )}
      {/* Group chứa mesh và text labels - tất cả sẽ xoay cùng nhau */}
      <group rotation={[0, (rotation * Math.PI) / 180, 0]}>
        <mesh 
          onClick={e => {
            e.stopPropagation();
            onBoxClick(box);
          }}
          castShadow
          receiveShadow
        >
          <boxGeometry args={[box.width, box.height, box.depth]} />
          <meshBasicMaterial attach="material" map={boxTexture} />
        </mesh>
        {/* Label trên 4 mặt bên với cải thiện visibility */}
        {/* +X (phải) */}
        <Text 
          position={[box.width/2+0.01, 0, 0]} 
          rotation={[0, -Math.PI/2, 0]} 
          fontSize={box.height/2.5} 
          color="#ffffff" 
          anchorX="center" 
          anchorY="middle"
          outlineWidth={0.03}
          outlineColor="#000000"
        >
          {box.label}
        </Text>
        {/* -X (trái) */}
        <Text 
          position={[-box.width/2-0.01, 0, 0]} 
          rotation={[0, Math.PI/2, 0]} 
          fontSize={box.height/2.5} 
          color="#ffffff" 
          anchorX="center" 
          anchorY="middle"
          outlineWidth={0.03}
          outlineColor="#000000"
        >
          {box.label}
        </Text>
        {/* +Z (trước) */}
        <Text 
          position={[0, 0, box.depth/2+0.01]} 
          rotation={[0, 0, 0]} 
          fontSize={box.height/2.5} 
          color="#ffffff" 
          anchorX="center" 
          anchorY="middle"
          outlineWidth={0.03}
          outlineColor="#000000"
        >
          {box.label}
        </Text>
        {/* -Z (sau) */}
        <Text
          position={[0, 0, -box.depth/2-0.01]} 
          rotation={[0, Math.PI, 0]} 
          fontSize={box.height/2.5} 
          color="#ffffff" 
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.03}
          outlineColor="#000000"
        >
          {box.label}
        </Text>
      </group>
    </group>
  );
}

function GoodsBoxes({ goods, onBoxClick, containerType, optimizedBoxes = null, selectedBox, boxRotations = {} }) {
  const container = CONTAINER_TYPES[containerType];
  const boxesToRender = optimizedBoxes || goods;
  
  console.log('GoodsBoxes render - goods:', goods.length, 'optimizedBoxes:', optimizedBoxes?.length, 'boxesToRender:', boxesToRender.length);
  console.log('boxesToRender IDs:', boxesToRender.map(box => box.id));
  
  return boxesToRender.map((box, i) => (
    <GoodsBox
      key={`${box.id}-${boxRotations[box.id] || 0}`}
      box={{...box, index: i}}
      onBoxClick={onBoxClick}
      container={container}
      optimized={!!optimizedBoxes}
      selected={selectedBox && selectedBox.id === box.id}
      rotation={boxRotations[box.id] || 0}
    />
  ));
}

function Container({ containerType }) {
  const container = CONTAINER_TYPES[containerType];
  const { width, height, depth } = container.dimensions;
  const meshRef = useRef();
  const { camera } = useThree();

  // Load textures cho từng nhóm mặt
  const leftRightTexture = useTexture('/textures/container_lr.jpg');
  const frontBackTexture = useTexture('/textures/container_side.jpg');
  const floorTexture = useTexture('/textures/container_floor.jpg');

  useEffect(() => {
    // Trái/phải: repeat
    leftRightTexture.wrapS = leftRightTexture.wrapT = THREE.RepeatWrapping;
    leftRightTexture.repeat.set(Math.round(depth), 1);
    leftRightTexture.needsUpdate = true;
    // Trước/sau: repeat theo chiều sâu (depth), không repeat theo chiều cao
    frontBackTexture.wrapS = frontBackTexture.wrapT = THREE.RepeatWrapping;
    frontBackTexture.repeat.set(3,1);
    frontBackTexture.needsUpdate = true;
    // Đáy: repeat theo chiều rộng và chiều sâu
    const repeatX = Math.round(width);
    const repeatY = Math.round(depth);
    floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
    floorTexture.repeat.set(repeatX, repeatY);
    floorTexture.needsUpdate = true;
  }, [leftRightTexture, frontBackTexture, floorTexture, width, depth]);

  // State cho materials
  const [materials, setMaterials] = useState([
    null, // +x (phải)
    <meshStandardMaterial attach="material-1" map={leftRightTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
    null, // +y (nóc)
    <meshStandardMaterial attach="material-3" map={floorTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
    <meshStandardMaterial attach="material-4" map={frontBackTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
    <meshStandardMaterial attach="material-5" map={frontBackTexture} opacity={0.8} transparent side={THREE.DoubleSide} />
  ]);

  useFrame(() => {
    if (!meshRef.current) return;
    const containerWorldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(containerWorldPos);

    const camZ = camera.position.z;
    const containerZ = containerWorldPos.z;
    const camX = camera.position.x;
    const containerX = containerWorldPos.x;
    const camY = camera.position.y;
    // Lấy hướng nhìn của camera (polar angle)
    const v = new THREE.Vector3();
    camera.getWorldDirection(v);
    // Tính polar angle (góc giữa hướng nhìn và trục y dương)
    const polar = Math.acos(v.y);
    // maxPolarAngle của OrbitControls
    const maxPolar = Math.PI / 2 - 0.1;
    const SHOW_ROOF_THRESHOLD = 0.03;
    // Hiển thị mặt nóc nếu camera ở rất thấp (chạm đáy)
    const showRoof = camera.position.y < 2;

    // Tạo mảng materials mới
    const baseMaterials = [
      <meshStandardMaterial attach="material-0" map={leftRightTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
      <meshStandardMaterial attach="material-1" map={leftRightTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
      showRoof
        ? <meshStandardMaterial attach="material-2" map={floorTexture} opacity={0.8} transparent side={THREE.DoubleSide} />
        : null,
    <meshStandardMaterial attach="material-3" map={floorTexture} opacity={0.8} transparent side={THREE.DoubleSide} />,
      <meshStandardMaterial attach="material-4" map={frontBackTexture} opacity={0.8} transparent side={THREE.DoubleSide} />, 
      <meshStandardMaterial attach="material-5" map={frontBackTexture} opacity={0.8} transparent side={THREE.DoubleSide} />
    ];

    // Ẩn mặt trước/sau
    if (camZ > containerZ) {
      baseMaterials[4] = null; // ẩn mặt trước
    } else {
      baseMaterials[5] = null; // ẩn mặt sau
    }

    // Ẩn mặt phải/trái
    if (camX > containerX) {
      baseMaterials[0] = null; // ẩn mặt phải
    } else {
      baseMaterials[1] = null; // ẩn mặt trái
    }

    setMaterials((prev) => {
      let changed = false;
      for (let i = 0; i < 6; i++) {
        if ((prev[i] === null) !== (baseMaterials[i] === null)) changed = true;
      }
      if (changed) return baseMaterials;
      return prev;
    });
  });

  return (
    <group>
      {/* Container box với texture từng mặt */}
      <mesh ref={meshRef} position={[0, height/2, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, height, depth]} />
        {materials.map((mat, idx) => mat && React.cloneElement(mat, { key: idx }))}
      </mesh>
      {/* Viền container */}
      <lineSegments>
        <edgesGeometry>
          <boxGeometry args={[width, height, depth]} />
        </edgesGeometry>
        <lineBasicMaterial color={container.color} linewidth={2} />
      </lineSegments>
      {/* Label và kích thước giữ nguyên */}
    </group>
  );
}

// Nền sàn với texture
function GroundTexture() {
  const texture = useTexture('/textures/floor.jpg');
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(10, 10);
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
      <planeGeometry args={[40, 40]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  );
}

function SceneEnvironment() {
  return (
    <>
      {/* Lighting setup đơn giản */}
      <ambientLight intensity={0.5} />
      <directionalLight 
        position={[10, 10, 5]} 
        intensity={1.1} 
        castShadow 
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-far={30}
        shadow-camera-left={-8}
        shadow-camera-right={8}
        shadow-camera-top={8}
        shadow-camera-bottom={-8}
      />
      {/* Nền môi trường xám nhạt */}
      <Environment preset="city" background={false} />
    </>
  );
}

function Container3D({ goods = [], onBoxClick = () => {}, containerType = '20ft-standard', optimizedBoxes = null, setView, controlsRef, setIsBoxSelected, boxRotations = {} }) {
  const [selectedBox, setSelectedBox] = useState(null);
  const [showCameraGuide, setShowCameraGuide] = useState(true);
  const container = CONTAINER_TYPES[containerType];
  const infoPanelRef = useRef();
  
  console.log('Container3D render - boxRotations:', boxRotations);
  console.log('Container3D render - optimizedBoxes:', optimizedBoxes);

  useEffect(() => {
    if (!selectedBox) return;
    function handleClickOutside(event) {
      // Kiểm tra xem click có phải vào nút "Xoay" hoặc "Trả Kiện Hàng Này" không
      const isRotateButton = event.target.closest('button') && event.target.textContent.includes('Xoay');
      const isReturnButton = event.target.closest('button') && event.target.textContent.includes('Trả Kiện Hàng Này');
      
      if (infoPanelRef.current && !infoPanelRef.current.contains(event.target) && !isRotateButton && !isReturnButton) {
        setSelectedBox(null);
        if (setIsBoxSelected) {
          setIsBoxSelected(false);
        }
      }
    }
    window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [selectedBox, setIsBoxSelected]);

  const handleBoxClick = (box) => {
    setSelectedBox(box);
    onBoxClick(box);
  };

  const resetView = () => {
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  // Tính toán thể tích sử dụng
  const boxesToCalculate = optimizedBoxes || goods;
  const usedVolume = boxesToCalculate.reduce((sum, g) => sum + g.width * g.height * g.depth, 0);
  const usageRatio = ((usedVolume / container.maxVolume) * 100).toFixed(1);

  return (
    <div style={{ position: 'absolute', inset: 0, width: '100vw', height: '100vh', background: '#e0e7ef', zIndex: 1 }}>
      {/* Menu chọn góc nhìn với cải thiện UI */}
      {typeof setView === 'function' && (
      <div style={{
          position: 'fixed',
          top: 12,
          right: 84,
          zIndex: 40,
          background: 'rgba(255,255,255,0.95)',
        borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          padding: '12px 16px',
          display: 'flex',
          gap: '10px',
          alignItems: 'center',
          border: '1px solid rgba(255,255,255,0.2)',
          backdropFilter: 'blur(10px)'
        }}>
          <span style={{fontWeight: 600, fontSize: 14, color: '#444'}}>👁️ View:</span>
        <button 
            className="view-btn"
            onClick={() => setView('front')} 
          style={{
              padding: '8px 14px', 
              borderRadius: 8, 
            border: 'none',
              background: '#e0e7ef', 
              color: '#333', 
              fontWeight: 500, 
            
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            ⬅️ Left
          </button>
          <button 
            className="view-btn"
            onClick={() => setView('back')} 
            style={{
              padding: '8px 14px', 
              borderRadius: 8, 
              border: 'none', 
              background: '#e0e7ef', 
              color: '#333', 
              fontWeight: 500, 
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            ➡️ Right
          </button>
          <button 
            className="view-btn"
            onClick={() => setView('top')} 
            style={{
              padding: '8px 14px', 
              borderRadius: 8, 
              border: 'none', 
              background: '#e0e7ef', 
              color: '#333', 
              fontWeight: 500, 
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            ⬆️ Top
        </button>
      </div>
      )}

      {/* Enhanced Info Panel với cải thiện UI */}
      {selectedBox && (
        <div ref={infoPanelRef} className="info-panel" style={{
          position: 'fixed',
          top: 24,
          left: 364,
          zIndex: 200,
          background: 'none',
          padding: 0,
          border: 'none',
          boxShadow: 'none',
          backdropFilter: 'none',
          minWidth: '200px',
          maxWidth: '320px',
          animation: 'slideIn 0.3s ease-out',
          textAlign: 'center'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: 18
          }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              background: getGoodColor(selectedBox.label),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 700,
              fontSize: 18,
              marginRight: 12
            }}>
              {selectedBox.label}
            </div>
            <h4 style={{ margin: 0, color: '#333', fontSize: '20px', fontWeight: '700' }}>
            {selectedBox.name}
          </h4>
          </div>
          <div style={{ fontSize: '15px', color: '#666', lineHeight: '1.7' }}>
            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
              <strong>📏 Kích thước:</strong> 
              <span>{selectedBox.width} × {selectedBox.height} × {selectedBox.depth} m</span>
            </div>
            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
              <strong>⚖️ Trọng lượng:</strong>
              <span>{selectedBox.weight ? selectedBox.weight.toLocaleString() : '—'} kg</span>
            </div>
          </div>
        </div>
      )}

      
      <Canvas 
        camera={{ position: [12, 8, 8], fov: 35 }}
        style={{ position: 'absolute', inset: 0, width: '100vw', height: '100vh', background: '#e0e7ef' }}
        shadows
      >
        <GroundTexture />
        <SceneEnvironment />
        <Container containerType={containerType} />
        <GoodsBoxes 
          goods={goods} 
          onBoxClick={handleBoxClick} 
          containerType={containerType}
          optimizedBoxes={optimizedBoxes}
          selectedBox={selectedBox}
          boxRotations={boxRotations}
        />
        <OrbitControls 
          ref={controlsRef}
          enablePan={false}
          enableZoom={true}
          enableRotate={true}
          minDistance={1}
          maxDistance={25}
          autoRotate={false}
          dampingFactor={0.05}
          enableDamping={true}
          minPolarAngle={0.05}
          maxPolarAngle={Math.PI / 2 - 0.02}
          target={[0, 1, 0]}
          rotateSpeed={0.25}
          panSpeed={0.6}
          zoomSpeed={0.6}
          enableKeys={false}
          mouseButtons={{
            LEFT: THREE.MOUSE.ROTATE,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.PAN
          }}
        />
      </Canvas>
    </div>
  );
}

export default Container3D; 