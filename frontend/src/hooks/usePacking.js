import { useState, useCallback } from 'react';
import { packGoods } from '../services/api';

export const usePacking = () => {
    const [isPacking, setIsPacking] = useState(false);
    const [packingResult, setPackingResult] = useState(null);
    const [error, setError] = useState(null);

    const startPacking = useCallback(async(goods, container, algorithm = 'genetic', iterations = 5) => {
        setIsPacking(true);
        setError(null);

        try {
            const result = await packGoods(goods, container, algorithm, iterations);
            setPackingResult(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setIsPacking(false);
        }
    }, []);

    const resetPacking = useCallback(() => {
        setPackingResult(null);
        setError(null);
    }, []);

    return {
        isPacking,
        packingResult,
        error,
        startPacking,
        resetPacking
    };
};