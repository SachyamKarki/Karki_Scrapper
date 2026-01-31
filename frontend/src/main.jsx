import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import './index.css'

// Dev: empty = same origin, Vite proxy forwards /api to localhost:5555
// Prod: VITE_API_URL = your Render backend (e.g. https://scraper-backend.onrender.com)
const API_URL = import.meta.env.DEV
  ? ''
  : (import.meta.env.VITE_API_URL || 'https://scraper-backend-evss.onrender.com');
axios.defaults.baseURL = API_URL;
axios.defaults.withCredentials = true;

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
