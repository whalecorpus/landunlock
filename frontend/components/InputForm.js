import React, { useState } from 'react';

const InputForm = ({ onCalculate, selectedArea }) => {
  const [landUseType, setLandUseType] = useState('reforestation');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onCalculate({
      area: selectedArea,
      landUseType,
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-4">
        <label className="block mb-2 font-medium">Land Use Type:</label>
        <div className="space-x-4">
          <label className="inline-flex items-center">
            <input
              type="radio"
              className="form-radio"
              value="reforestation"
              checked={landUseType === 'reforestation'}
              onChange={() => setLandUseType('reforestation')}
            />
            <span className="ml-2">Reforestation</span>
          </label>
          <label className="inline-flex items-center">
            <input
              type="radio"
              className="form-radio"
              value="solar"
              checked={landUseType === 'solar'}
              onChange={() => setLandUseType('solar')}
            />
            <span className="ml-2">Solar Panels</span>
          </label>
        </div>
      </div>
      
      {selectedArea ? (
        <div className="mb-4">
          <p>Selected area: {selectedArea.toFixed(2)} hectares</p>
        </div>
      ) : (
        <div className="mb-4 text-yellow-600">
          <p>Please select an area on the map first</p>
        </div>
      )}
      
      <button 
        type="submit" 
        disabled={!selectedArea}
        className={`py-2 px-4 rounded ${!selectedArea 
          ? 'bg-gray-300 cursor-not-allowed' 
          : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
      >
        Calculate Impact
      </button>
    </form>
  );
};

export default InputForm;

