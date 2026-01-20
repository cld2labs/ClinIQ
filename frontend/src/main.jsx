/**
 * Application Entry Point
 * 
 * This is the first file that runs when the React application starts.
 * It:
 * 1. Imports React and ReactDOM
 * 2. Imports the main App component
 * 3. Imports global CSS styles
 * 4. Renders the App into the HTML page
 * 
 * How it works:
 * - ReactDOM.createRoot() creates a React root container
 * - The root is attached to the HTML element with id="root" (in index.html)
 * - React.StrictMode enables additional development checks
 * - App component is rendered inside the root
 * 
 * This is similar to Python's if __name__ == '__main__': block
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'  // Global CSS styles (Tailwind CSS)

// Create React root and render the App
// document.getElementById('root') finds the <div id="root"> in index.html
ReactDOM.createRoot(document.getElementById('root')).render(
  // StrictMode helps catch potential problems during development
  // It runs components twice in development to detect side effects
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
