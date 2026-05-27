import React from 'react';
import { FiHome, FiUploadCloud, FiAlertCircle, FiSettings } from 'react-icons/fi';
import '../styles/Sidebar.css';

export default function Sidebar({ isOpen, currentPage, onPageChange }) {
    const menuItems = [
        { id: 'dashboard', label: 'Dashboard', icon: FiHome },
        { id: 'deployments', label: 'Deployments', icon: FiUploadCloud },
        { id: 'incidents', label: 'Incidents', icon: FiAlertCircle },
        { id: 'settings', label: 'Settings', icon: FiSettings },
    ];

    return (
        <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
            <nav className="sidebar-nav">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <button
                            key={item.id}
                            className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                            onClick={() => onPageChange(item.id)}
                        >
                            <Icon className="nav-icon" />
                            <span className="nav-label">{item.label}</span>
                        </button>
                    );
                })}
            </nav>
        </aside>
    );
}
