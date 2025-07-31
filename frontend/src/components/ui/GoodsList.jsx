import { useState, useEffect, useRef } from 'react';
import * as XLSX from 'xlsx';

// Định nghĩa màu sắc và icon cho từng loại hàng (A, B, C, D...)
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

function getGoodColor(name) {
  // Lấy ký tự đầu (A, B, C...) để gán màu
  const idx = name && name.length > 0 ? name.charCodeAt(0) - 65 : 0;
  return GOOD_COLORS[idx % GOOD_COLORS.length];
}

function groupGoods(goods) {
  // Nhóm hàng hóa theo ký tự đầu của tên (A, B, C...)
  const groups = {};
  goods.forEach(g => {
    const groupKey = g.name ? g.name[0].toUpperCase() : '?';
    if (!groups[groupKey]) groups[groupKey] = [];
    groups[groupKey].push(g);
  });
  return groups;
}

function GoodsList({ goods, onAdd, onRemove, onEdit, onAddBulk }) {
  const [form, setForm] = useState({ name: '', width: '', height: '', depth: '', weight: '', quantity: '' });
  const [showForm, setShowForm] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState('1');
  const [editGood, setEditGood] = useState(null); // good đang chỉnh sửa
  const formRef = useRef();

  // Thoát chế độ chỉnh sửa khi click ngoài form
  useEffect(() => {
    if (!editGood) return;
    function handleClickOutside(e) {
      if (formRef.current && !formRef.current.contains(e.target)) {
        setEditGood(null);
        setForm({ name: '', width: '', height: '', depth: '', weight: '', quantity: '' });
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [editGood]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name || !form.width || !form.height || !form.depth || !form.weight || !form.quantity) return;
    if (editGood) {
      // Chỉnh sửa hàng
      onEdit({
        ...editGood,
        ...form,
        group: selectedGroup,
        width: parseFloat(form.width) / 1000,
        height: parseFloat(form.height) / 1000,
        depth: parseFloat(form.depth) / 1000,
        weight: parseFloat(form.weight),
        quantity: parseInt(form.quantity, 10),
      });
      setEditGood(null);
    } else {
      // Thêm mới
    onAdd({
        ...form,
        group: selectedGroup,
        width: parseFloat(form.width) / 1000,
        height: parseFloat(form.height) / 1000,
        depth: parseFloat(form.depth) / 1000,
        weight: parseFloat(form.weight),
        quantity: parseInt(form.quantity, 10),
    });
    }
    setForm({ name: '', width: '', height: '', depth: '', weight: '', quantity: '' });
    setShowForm(false);
  };

  // Khi click vào 1 good để chỉnh sửa
  const handleEditClick = (good) => {
    setEditGood(good);
    setShowForm(false);
    setForm({
      name: good.name,
      width: Math.round(good.width * 1000),
      height: Math.round(good.height * 1000),
      depth: Math.round(good.depth * 1000),
      weight: good.weight,
      quantity: good.quantity,
    });
    setSelectedGroup(good.group);
  };

  const calculateVolume = (item) => {
    return (item.width * item.height * item.depth).toFixed(3);
  };

  // Xử lý import Excel
  const handleImportExcel = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const rows = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
      // Giả sử dòng đầu là header: [Tên, Rộng, Cao, Dài, Trọng lượng, Số lượng, Nhóm]
      const goodsToAdd = [];
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row[0]) continue;
        goodsToAdd.push({
          name: row[0],
          width: parseFloat(row[1]) / 1000,
          height: parseFloat(row[2]) / 1000,
          depth: parseFloat(row[3]) / 1000,
          weight: parseFloat(row[4]),
          quantity: parseInt(row[5], 10),
          group: row[6] ? String(row[6]) : '2',
        });
      }
      if (goodsToAdd.length > 0 && typeof onAddBulk === 'function') {
        onAddBulk(goodsToAdd);
      } else {
        goodsToAdd.forEach(good => onAdd(good));
      }
    };
    reader.readAsArrayBuffer(file);
  };

  // Chia hàng hóa theo nhóm
  const goodsPriority = goods.filter(g => g.group === '1');
  const goodsNormal = goods.filter(g => g.group === '2');

  return (
    <div>
      {/* Nút nhập Excel thay cho tiêu đề */}
      <div style={{marginBottom: 18, display: 'flex', alignItems: 'center', gap: 12}}>
        <label htmlFor="excel-import" style={{
          display: 'inline-block',
          background: '#2980b9',
          color: 'white',
          padding: '10px 18px',
          borderRadius: 8,
          fontWeight: 700,
          fontSize: 16,
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(41,128,185,0.08)'
        }}>
          📥 Nhập Excel
        </label>
        <input id="excel-import" type="file" accept=".xlsx,.xls" style={{display: 'none'}} onChange={handleImportExcel} />
      </div>
      <h2 style={{marginBottom: 18, fontSize: 20, color: '#444', fontWeight: 700}}>Nhóm hàng</h2>
      {/* Nút chọn nhóm */}
      <div style={{display: 'flex', gap: 12, marginBottom: 18}}>
        <button
          onClick={() => setSelectedGroup('1')}
          style={{
            flex: 1,
            padding: '10px 0',
            borderRadius: 8,
            border: selectedGroup === '1' ? '2px solid #e67e22' : '1px solid #ccc',
            background: selectedGroup === '1' ? '#fffbe6' : '#f8f9fa',
            color: '#e67e22',
            fontWeight: 700,
            cursor: 'pointer',
            fontSize: 16
          }}
        >
          Nhóm ưu tiên
        </button>
        <button
          onClick={() => setSelectedGroup('2')}
          style={{
            flex: 1,
            padding: '10px 0',
            borderRadius: 8,
            border: selectedGroup === '2' ? '2px solid #2980b9' : '1px solid #ccc',
            background: selectedGroup === '2' ? '#eaf4ff' : '#f8f9fa',
            color: '#2980b9',
            fontWeight: 700,
            cursor: 'pointer',
            fontSize: 16
          }}
        >
          Nhóm thường
        </button>
      </div>
      {/* Danh sách nhóm ưu tiên */}
      <div className="goods-list" style={{padding: 0}}>
        <h3 style={{margin: '18px 0 8px', color: '#e67e22', fontSize: 17}}>Nhóm ưu tiên</h3>
        {goodsPriority.length === 0 ? (
          <p style={{color: '#bbb', fontStyle: 'italic', margin: '0 0 12px 0'}}>Chưa có hàng hóa ưu tiên</p>
        ) : (
          goodsPriority.map((g, i) => (
            <div key={g.id} style={{display: 'flex', alignItems: 'center', marginBottom: 6, padding: '6px 0', borderRadius: 6, background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.03)', cursor: 'pointer'}} onClick={() => handleEditClick(g)}>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 28,
                height: 28,
                borderRadius: 6,
                background: getGoodColor(g.label),
                color: 'white',
                fontWeight: 700,
                fontSize: 16,
                marginRight: 10,
                border: '2px solid #fff',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
              }}>{g.label}</span>
              <div style={{flex: 1}}>
                <span style={{fontWeight: 600, color: '#333', fontSize: 15}}>{g.name}</span>
                <span style={{marginLeft: 8, fontSize: 13, color: '#666'}}>
                  ({Math.round(g.width * 1000)}×{Math.round(g.height * 1000)}×{Math.round(g.depth * 1000)}mm)
                </span>
                <span style={{marginLeft: 8, fontSize: 12, color: '#28a745', fontWeight: 600}}>Thể tích: {(g.width * g.height * g.depth).toFixed(3)} m³</span>
                <span style={{marginLeft: 8, fontSize: 12, color: '#2980b9', fontWeight: 600}}>Trọng lượng: {g.weight} kg</span>
              </div>
            </div>
          ))
        )}
      </div>
      {/* Danh sách nhóm thường */}
      <div className="goods-list" style={{padding: 0}}>
        <h3 style={{margin: '18px 0 8px', color: '#2980b9', fontSize: 17}}>Nhóm thường</h3>
        {goodsNormal.length === 0 ? (
          <p style={{color: '#bbb', fontStyle: 'italic', margin: '0 0 12px 0'}}>Chưa có hàng hóa thường</p>
        ) : (
          goodsNormal.map((g, i) => (
            <div key={g.id} style={{display: 'flex', alignItems: 'center', marginBottom: 6, padding: '6px 0', borderRadius: 6, background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.03)', cursor: 'pointer'}} onClick={() => handleEditClick(g)}>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                background: getGoodColor(g.label),
                    color: 'white',
                    fontWeight: 700,
                    fontSize: 16,
                    marginRight: 10,
                    border: '2px solid #fff',
                    boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
              }}>{g.label}</span>
                  <div style={{flex: 1}}>
                    <span style={{fontWeight: 600, color: '#333', fontSize: 15}}>{g.name}</span>
                <span style={{marginLeft: 8, fontSize: 13, color: '#666'}}>
                  ({Math.round(g.width * 1000)}×{Math.round(g.height * 1000)}×{Math.round(g.depth * 1000)}mm)
                </span>
                <span style={{marginLeft: 8, fontSize: 12, color: '#28a745', fontWeight: 600}}>Thể tích: {(g.width * g.height * g.depth).toFixed(3)} m³</span>
                <span style={{marginLeft: 8, fontSize: 12, color: '#2980b9', fontWeight: 600}}>Trọng lượng: {g.weight} kg</span>
                  </div>
            </div>
          ))
        )}
      </div>
      {/* Form thêm/chỉnh sửa hàng mới */}
      <div className="add-form">
        {(!showForm && !editGood) ? (
          <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 16, marginTop: 24}}>
            <button className="add-btn" style={{width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', background: '#e0e7ef', border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.08)', cursor: 'pointer'}} onClick={() => setShowForm(true)} title="Thêm hàng hóa">
              <img src="/img/box.png" alt="Thêm hàng hóa" style={{width: 38, height: 38, display: 'block', objectFit: 'contain'}} />
            </button>
            <span style={{fontSize: 18, color: '#666', fontWeight: 500}}>Thêm hàng hoá mới</span>
          </div>
        ) : (
          <div ref={formRef} style={{background: '#f8fafd', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', padding: 24, marginTop: 12, position: 'relative', zIndex: 10}}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input 
              name="name" 
              value={form.name} 
              onChange={handleChange} 
              placeholder="Tên hàng hóa" 
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <input 
                name="width" 
                value={form.width} 
                onChange={handleChange} 
                    placeholder="Rộng (mm)" 
                type="number" 
                    step="1" 
                    min="1"
                required
              />
            </div>
            <div className="form-group">
              <input 
                name="height" 
                value={form.height} 
                onChange={handleChange} 
                    placeholder="Cao (mm)" 
                type="number" 
                    step="1" 
                    min="1"
                required
              />
            </div>
            <div className="form-group">
              <input 
                name="depth" 
                value={form.depth} 
                onChange={handleChange} 
                    placeholder="Dài (mm)" 
                    type="number" 
                    step="1" 
                    min="1"
                    required
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <input 
                    name="weight" 
                    value={form.weight} 
                    onChange={handleChange} 
                    placeholder="Cân nặng (kg)" 
                type="number" 
                step="0.01" 
                min="0.01"
                required
              />
            </div>
                <div className="form-group">
                  <input 
                    name="quantity" 
                    value={form.quantity} 
                    onChange={handleChange} 
                    placeholder="Số lượng" 
                    type="number" 
                    min="1"
                    required
                  />
                </div>
              </div>
              <div className="action-row" style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                gap: 12,
                marginTop: 18,
                width: '100%'
              }}>
                <button
                  type="button"
                  onClick={() => {
                    if (editGood) {
                      onRemove(editGood.id);
                      setEditGood(null);
                    } else {
                      setShowForm(false); setEditGood(null); setForm({ name: '', width: '', height: '', depth: '', weight: '', quantity: '' });
                    }
                  }}
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#eee',
                    color: '#666',
                    border: 'none',
                    borderRadius: 8,
                    height: 48,
                    minWidth: 0,
                    padding: 0,
                    lineHeight: 1,
                  }}
                  title={editGood ? 'Xoá' : 'Huỷ'}
                >
                  <img src="/img/trash.png" alt={editGood ? 'Xoá' : 'Huỷ'} style={{width: 24, height: 24, display: 'block', objectFit: 'contain'}} />
                </button>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(90deg,#3498db,#2ecc71)',
                    border: 'none',
                    borderRadius: 8,
                    height: 48,
                    minWidth: 0,
                    padding: 0,
                    lineHeight: 1,
                  }}
                  title={editGood ? 'Lưu' : 'Thêm hàng'}
                >
                  <img src="/img/box.png" alt={editGood ? 'Lưu' : 'Thêm hàng'} style={{width: 28, height: 28, display: 'block', objectFit: 'contain'}} />
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default GoodsList; 


