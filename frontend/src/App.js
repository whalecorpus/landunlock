import React, { useState } from 'react';
import MapDisplay from './components/MapDisplay';
import InputForm from './components/InputForm';
import { calculateLandImpact } from './services/api';
import './App.css';

function App() {
  const [selectedArea, setSelectedArea] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleAreaSelected = (area) => {
    setSelectedArea(area);
    setResults(null);
  };
  
  const handleCalculate = async (formData) => {
    setLoading(true);
    try {
      const calculationResults = await calculateLandImpact(formData);
      setResults(calculationResults);
    } catch (error) {
      console.error('Calculation failed:', error);
      // Handle error display
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>Land Use Calculator</h1>
        <p>Analyze the carbon impact of reforestation or solar panels on a selected area</p>
      </header>
      
      <main>
        <section className="map-section">
          <h2>Select an Area</h2>
          <MapDisplay onAreaSelected={handleAreaSelected} />
        </section>
        
        <section className="calculation-section">
          <h2>Calculate Impact</h2>
          <InputForm 
            onCalculate={handleCalculate} 
            selectedArea={selectedArea} 
          />
          
          {loading && <div className="loading">Calculating...</div>}
          
          {results && (
            <div className="results">
              <h3>Results</h3>
              {results.landUseType === 'reforestation' ? (
                <div>
                  <p>Carbon Sequestration Potential: {results.carbonSequestered} tons CO2e per year</p>
                  <p>Over 30 years: {results.carbonSequestered * 30} tons CO2e</p>
                </div>
              ) : (
                <div>
                  <p>Energy Production: {results.energyProduction} MWh per year</p>
                  <p>Carbon Offset: {results.carbonOffset} tons CO2e per year</p>
                  <p>Over 30 years: {results.carbonOffset * 30} tons CO2e</p>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
      
      <footer>
        <p>Land Use Calculator - A tool for comparing carbon impact of land use choices</p>
      </footer>
    </div>
  );
}

export default App;