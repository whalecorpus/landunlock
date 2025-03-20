import React, { useState } from 'react';

const InputForm = ({ onCalculate, selectedArea }) => {
  const [landUseType, setLandUseType] = useState('reforestation');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onCalculate({
      area: selectedArea,
      landUseType,
      // Add other parameters as needed
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="calculation-form">
      <div className="form-group">
        <label>Land Use Type:</label>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              value="reforestation"
              checked={landUseType === 'reforestation'}
              onChange={() => setLandUseType('reforestation')}
            />
            Reforestation
          </label>
          <label>
            <input
              type="radio"
              value="solar"
              checked={landUseType === 'solar'}
              onChange={() => setLandUseType('solar')}
            />
            Solar Panels
          </label>
        </div>
      </div>
      
      <button type="submit" disabled={!selectedArea}>
        Calculate Impact
      </button>
    </form>
  );
};

export default InputForm;