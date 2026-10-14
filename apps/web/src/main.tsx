import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './workspace.css';

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  void navigator.serviceWorker.register('/sw.js').catch(() => {
    // Offline installation is optional; an unavailable cache never enables live capabilities.
  });
}
