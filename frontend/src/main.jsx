import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import './index.css'

// In production (Vercel), set VITE_API_URL to your backend URL
const API_URL = import.meta.env.VITE_API_URL || 'https://scraper-backend-evss.onrender.com';
axios.defaults.baseURL = API_URL;
axios.defaults.withCredentials = true

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
