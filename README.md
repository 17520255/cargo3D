# Cargo Packing Optimization System

Hệ thống tối ưu hóa đóng gói hàng hóa 3D với kiến trúc Backend-Frontend tách biệt.

## 📁 Cấu trúc dự án

```
cargo/
├── backend/                  # Python Backend API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   └── packing.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── schemas.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── cors.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── packing_service.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── packing_algorithm.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_packing.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├──3d/
│   │   │   └── layout/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── styles/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── docs/                     # Documentation
├── docker-compose.yml        # Docker setup
└── README.md
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python -m app.main
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Backend (Python/FastAPI)

### Tính năng:
- **FastAPI**: RESTful API server với auto-documentation
- **Pydantic**: Data validation và serialization
- **Genetic Algorithm**: Thuật toán tối ưu hóa đóng gói
- **Spatial Indexing**: Tối ưu hóa tìm kiếm vị trí
- **3D Bin Packing**: Đóng gói hàng hóa 3D

### API Endpoints:
- `GET /` - Health check
- `GET /docs` - API documentation (Swagger)
- `GET /api/sample` - Lấy dữ liệu mẫu
- `POST /api/pack` - Thực hiện đóng gói

### Cấu trúc Backend:
```
backend/
├── app/                     # Application core
│   ├── main.py             # FastAPI app entry point
│   ├── api/                # API routes và models
│   ├── core/               # Configuration và middleware
│   └── services/           # Business logic
├── algorithms/              # Thuật toán đóng gói
├── tests/                  # Unit tests
└── requirements.txt         # Dependencies
```

## 🎨 Frontend (React/Vite)

### Tính năng:
- **React 19**: Latest React với concurrent features
- **Three.js**: 3D visualization
- **React Three Fiber**: React wrapper cho Three.js
- **Vite**: Fast development server
- **Responsive Design**: Mobile-first approach

### Cấu trúc Frontend:
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── 3d/             # 3D visualization components
│   │   └── layout/         # Layout components
│   ├── services/           # API calls và external services
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   └── styles/             # CSS/SCSS files
├── public/                 # Static assets
└── package.json
```

## 🐳 Docker Setup

```bash
# Build và run với Docker Compose
docker-compose up --build

# Chỉ backend
docker-compose up backend

# Chỉ frontend
docker-compose up frontend
```

## 🔄 Development Workflow

1. **Frontend**: Người dùng nhập dữ liệu hàng hóa và container
2. **API Call**: Frontend gửi request đến Backend qua REST API
3. **Backend**: Thực hiện thuật toán tối ưu hóa
4. **Response**: Trả về kết quả đóng gói dạng JSON
5. **Frontend**: Hiển thị kết quả 3D với Three.js

## 🛠️ Công nghệ sử dụng:

### Backend:
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **NumPy/SciPy**: Scientific computing
- **Genetic Algorithm**: Optimization algorithm
- **Uvicorn**: ASGI server

### Frontend:
- **React 19**: Latest React version
- **Three.js**: 3D graphics library
- **React Three Fiber**: React wrapper for Three.js
- **Vite**: Fast build tool
- **React DnD**: Drag and drop functionality

## 📊 API Documentation

Sau khi chạy backend, truy cập:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend (Production)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 80
```

### Frontend (Production)
```bash
cd frontend
npm run build
# Serve dist/ folder với nginx hoặc static server
```

## 📝 Environment Variables

Tạo file `.env` trong thư mục backend:

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết. 