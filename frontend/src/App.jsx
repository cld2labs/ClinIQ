/**
 * Main Application Component - React Router Setup
 * 
 * This is the root component of the React application. It sets up:
 * 1. Routing: Defines which component to show for each URL path
 * 2. Toast Notifications: Configures success/error message popups
 * 3. Layout: Wraps all pages with a consistent header/footer
 * 
 * How React Router Works:
 * - BrowserRouter: Enables client-side routing (no page refreshes)
 * - Routes: Container for all route definitions
 * - Route: Maps a URL path to a React component
 * 
 * Example:
 * - URL: "/" → Shows Home component
 * - URL: "/chat" → Shows Chat component
 * 
 * The Layout component wraps both routes, providing consistent navigation.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Chat from './pages/Chat';

function App() {
  return (
    // BrowserRouter enables client-side routing
    // This allows navigation without full page reloads
    <BrowserRouter>
      {/* Toast Notification System */}
      {/* Shows temporary success/error messages at the top-right */}
      <Toaster
        position="top-right"  // Where notifications appear
        toastOptions={{
          duration: 4000,  // How long notifications stay (4 seconds)
          style: {
            background: '#fff',  // White background
            color: '#374151',  // Gray text
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',  // Subtle shadow
          },
          // Success notifications (green checkmark)
          success: {
            iconTheme: {
              primary: '#22c55e',  // Green color
              secondary: '#fff',  // White checkmark
            },
          },
          // Error notifications (red X)
          error: {
            iconTheme: {
              primary: '#ef4444',  // Red color
              secondary: '#fff',  // White X
            },
          },
        }}
      />
      
      {/* Route Definitions */}
      {/* Defines which component to render for each URL path */}
      <Routes>
        {/* Layout wraps all child routes, providing header/footer */}
        <Route path="/" element={<Layout />}>
          {/* Index route: "/" shows the Home page */}
          <Route index element={<Home />} />
          
          {/* Chat route: "/chat" shows the Chat page */}
          <Route path="chat" element={<Chat />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
