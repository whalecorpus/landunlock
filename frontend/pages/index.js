import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import Head from 'next/head';

// Import MapDisplay with no SSR since Mapbox requires browser environment
const MapDisplay = dynamic(() => import('../components/MapDisplay'), { 
  ssr: false 
});
import InputForm from '../components/InputForm';

export default function Home() {
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
      const response = await fetch('http://localhost:5000/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const calculationResults = await response.json();
      setResults(calculationResults);
    } catch (error) {
      console.error('Calculation failed:', error);
      // Handle error display
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <Head>
        <title>Land Use Calculator</title>
        <meta name="description" content="Compare carbon impact of reforestation vs solar panels" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold">Land Use Calculator</h1>
          <p className="text-lg">Analyze the carbon impact of reforestation or solar panels on a selected area</p>
        </header>
        
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4">Select an Area</h2>
          <MapDisplay onAreaSelected={handleAreaSelected} />
        </section>
        
        <section>
          <h2 className="text-xl font-bold mb-4">Calculate Impact</h2>
          <InputForm 
            onCalculate={handleCalculate} 
            selectedArea={selectedArea} 
          />
          
          {loading && <div className="my-4">Calculating...</div>}
          
          {results && (
            <div className="my-4 p-4 border rounded">
              <h3 className="text-lg font-bold mb-2">Results</h3>
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
      
      <footer className="mt-8 py-4 text-center text-gray-600">
        <p>Land Use Calculator - A tool for comparing carbon impact of land use choices</p>
      </footer>
    </div>
  );
}
