/**
 * Main App component.
 * 
 * Root component for the application.
 * Sets up routing and layout.
 */

import React, { useState, useEffect } from 'react';
import { AppProvider } from './context/AppContext';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Deployments from './pages/Deployments';
import Incidents from './pages/Incidents';
import { healthCheck } from './services/api';
import './App.css';

export default function App() {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [apiHealth, setApiHealth] = useState(false);

    // Check API health on mount
    useEffect(() => {
        const checkHealth = async () => {
            try {
                await healthCheck();
                setApiHealth(true);
            } catch (error) {
                console.error('API health check failed:', error);
                setApiHealth(false);
            }
        };

        checkHealth();
        // Check health every 30 seconds
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    // Render current page
    const renderPage = () => {
        switch (currentPage) {
            case 'deployments':
                return <Deployments />;
            case 'incidents':
                return <Incidents />;
            case 'dashboard':
            default:
                return <Dashboard />;
        }
    };

    return (
        <AppProvider>
            <div className="app">
                {!apiHealth && (
                    <div className="api-warning">
                        ⚠️ Backend API not reachable. Some features may not work.
                    </div>
                )}
                
                <Header 
                    onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
                    apiHealth={apiHealth}
                />
                
                <div className="app-container">
                    <Sidebar 
                        isOpen={sidebarOpen}
                        currentPage={currentPage}
                        onPageChange={setCurrentPage}
                    />
                    
                    <main className="main-content">
                        {renderPage()}
                    </main>
                </div>
            </div>
        </AppProvider>
    );
}
