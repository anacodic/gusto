import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

console.log('main.jsx: Starting React app...');
console.log('main.jsx: Document ready state:', document.readyState);
console.log('main.jsx: Body background:', window.getComputedStyle(document.body).background);

const rootElement = document.getElementById('root');
console.log('main.jsx: Root element found:', !!rootElement);

try {
  if (!rootElement) {
    throw new Error('Root element not found!');
  }
  
  const root = ReactDOM.createRoot(rootElement);
  
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
  console.log('main.jsx: React app rendered successfully');
} catch (error) {
  console.error('main.jsx: Error rendering app:', error);
  console.error('main.jsx: Error stack:', error.stack);
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="padding: 40px; font-family: Arial; background: #ff6b6b; color: white; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <h1 style="font-size: 2rem; margin-bottom: 1rem;">❌ Error Loading App</h1>
        <p style="font-size: 1.2rem; margin-bottom: 1rem;">${error.message}</p>
        <pre style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; overflow: auto; max-width: 800px; text-align: left;">${error.stack}</pre>
        <button onclick="window.location.reload()" style="padding: 10px 20px; margin-top: 20px; font-size: 1rem; cursor: pointer; background: white; color: #ff6b6b; border: none; border-radius: 4px;">Reload Page</button>
      </div>
    `;
  }
}

