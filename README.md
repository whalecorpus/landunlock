# Land Use Calculator

A tool for comparing the carbon impact of different land use choices, specifically reforestation versus solar panel installation.

## Local Development Setup

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
<!--- Mapbox API key (for the map functionality; I believe it's free up to 50k uses, and we're going to navigate away from this library early in development I hope)-->


### Frontend Setup
1. Navigate to the client directory: `cd client`
2. Install dependencies: `npm install`
<!--3. Swap in your Mapbox API key in MapDisplay.js for `MAPBOX_TOKEN`-->
4. Start the development server: `npm run dev`

### Backend Setup
Add a `.env` file to your `backend` directory with the following form. Get your API key from: https://developer.nrel.gov/signup/
```
PVLIB_API_KEY=
PVLIB_API_EMAIL=
PORT=3000
CORS_ORIGIN=http://localhost:[FRONTEND_PORT]
```

To get the app running!
1. `cd backend`
2.
```
python -m venv venv
source venv/bin/activate
```
3. Install dependencies:
`pip install -r requirements.txt`
4. Start the Flask server
`python app.py`

## Usage

1. Open your browser and navigate to `http://localhost:[FRONTEND_PORT]`
2. Use the map to select an area of land
3. Choose between reforestation or solar panels
4. View the calculated carbon impact

## Contributing

We only have two weeks! You can push right to main.
