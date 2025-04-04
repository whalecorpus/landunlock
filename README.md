# Land Use Calculator

A tool for comparing the carbon impact of different land use choices, specifically reforestation versus solar panel installation.

Made by: Aarathi, Anna, Jae, Ryan in Terra's Software for Climate class

## Local Development Setup

### Prerequisites

- Node.js (v19+)
- Python (v3.8+)

### Frontend Setup
1. Navigate to the client directory: `cd client`
2. Install dependencies: `npm install`
4. Start the development server: `npm run dev`

### Backend Setup
Add a `.env` file to your `backend` directory with the following form. Get your API key from: https://developer.nrel.gov/signup/
```
FLASK_ENV=development
PVLIB_API_KEY=
PVLIB_EMAIL=
PORT=3000
CORS_ORIGIN=http://localhost:[FRONTEND_PORT]
GEOCODE_MAPS_API_KEY=67ec335734a23161688682xbg65f1ea
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

For team members: We only have two weeks! You can push right to main.
For others: we welcome pull requests. If you're in Terra community, feel free to reach out to us on Slack.
