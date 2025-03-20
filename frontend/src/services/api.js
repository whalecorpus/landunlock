// frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:5000/api';

export const calculateLandImpact = async (landData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(landData),
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error calculating land impact:', error);
    throw error;
  }
};