/**
 * Global application context.
 * 
 * Manages global state like user, theme, notifications.
 * Provides context to all components.
 */

import React, { createContext, useState, useCallback } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notification, setNotification] = useState(null);
    const [theme, setTheme] = useState('dark');

    // Show notification
    const showNotification = useCallback((message, type = 'info', duration = 3000) => {
        setNotification({ message, type });
        
        if (duration > 0) {
            setTimeout(() => setNotification(null), duration);
        }
    }, []);

    // Clear notification
    const clearNotification = useCallback(() => {
        setNotification(null);
    }, []);

    // Toggle theme
    const toggleTheme = useCallback(() => {
        setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
    }, []);

    const value = {
        user,
        setUser,
        loading,
        setLoading,
        notification,
        showNotification,
        clearNotification,
        theme,
        toggleTheme,
    };

    return (
        <AppContext.Provider value={value}>
            {children}
        </AppContext.Provider>
    );
};
