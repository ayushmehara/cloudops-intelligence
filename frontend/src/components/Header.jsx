import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';
import '../styles/Header.css';

export default function Header({ onSidebarToggle, apiHealth }) {
    const { theme, toggleTheme } = useContext(AppContext);

    return (
        <header className="header">
            <div className="header-left">
                <button className="sidebar-toggle" onClick={onSidebarToggle}>
                    ☰
                </button>
                <h1 className="app-title">CloudOps Intelligence</h1>
            </div>

            <div className="header-right">
                <div className={`api-status ${apiHealth ? 'healthy' : 'unhealthy'}`}>
                    <span className="status-dot"></span>
                    {apiHealth ? 'API Connected' : 'API Offline'}
                </div>

                <button className="theme-toggle" onClick={toggleTheme}>
                    {theme === 'dark' ? '☀️' : '🌙'}
                </button>

                <div className="user-menu">
                    <span>Admin</span>
                </div>
            </div>
        </header>
    );
}
