// Hàm sinh ký hiệu theo thứ tự A, B, ..., Z, AA, AB, ...
export function getNextLabel(existingGoods) {
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
export function expandGoods(goods) {
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

// Hàm tính tổng thể tích hàng hóa
export function calculateTotalVolume(goods) {
    return goods.reduce((total, good) => {
        return total + (good.width * good.height * good.depth * (good.quantity || 1));
    }, 0);
}

// Hàm tính tổng trọng lượng hàng hóa
export function calculateTotalWeight(goods) {
    return goods.reduce((total, good) => {
        return total + (good.weight * (good.quantity || 1));
    }, 0);
}

// Hàm format số thập phân
export function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Hàm validate dữ liệu hàng hóa
export function validateGood(good) {
    const errors = [];

    if (!good.name || good.name.trim() === '') {
        errors.push('Tên hàng hóa không được để trống');
    }

    if (!good.width || good.width <= 0) {
        errors.push('Chiều rộng phải lớn hơn 0');
    }

    if (!good.height || good.height <= 0) {
        errors.push('Chiều cao phải lớn hơn 0');
    }

    if (!good.depth || good.depth <= 0) {
        errors.push('Chiều sâu phải lớn hơn 0');
    }

    if (!good.weight || good.weight <= 0) {
        errors.push('Trọng lượng phải lớn hơn 0');
    }

    if (!good.quantity || good.quantity <= 0) {
        errors.push('Số lượng phải lớn hơn 0');
    }

    return errors;
}