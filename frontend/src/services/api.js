const API_BASE_URL = 'http://localhost:8000';

// Lấy dữ liệu mẫu từ backend
export const getSampleData = async() => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sample`);
        if (!response.ok) {
            throw new Error('Failed to fetch sample data');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching sample data:', error);
        throw error;
    }
};

// Gọi API đóng gói hàng hóa
export const packGoods = async(goods, container, algorithm = 'genetic', iterations = 5) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/pack`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goods,
                container,
                algorithm,
                iterations
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to pack goods');
        }

        return await response.json();
    } catch (error) {
        console.error('Error packing goods:', error);
        throw error;
    }
};

// Health check API
export const healthCheck = async() => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            throw new Error('Backend is not healthy');
        }
        return await response.json();
    } catch (error) {
        console.error('Health check failed:', error);
        throw error;
    }
};