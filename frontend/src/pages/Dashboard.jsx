import React, { useState, useEffect } from 'react';
import { deployments, incidents } from '../services/api';
import '../styles/Dashboard.css';

export default function Dashboard() {
    const [stats, setStats] = useState({
        totalDeployments: 0,
        successfulDeployments: 0,
        failedDeployments: 0,
        activeIncidents: 0,
        criticalIncidents: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setLoading(true);

                // Fetch deployments
                const deploymentsData = await deployments.list({ limit: 100 });
                const successful = deploymentsData.filter((d) => d.status === 'success').length;
                const failed = deploymentsData.filter((d) => d.status === 'failed').length;

                // Fetch incidents
                const incidentsData = await incidents.list({ limit: 100 });
                const active = incidentsData.filter((i) => i.status === 'open').length;
                const critical = incidentsData.filter(
                    (i) => i.status === 'open' && i.severity === 'critical'
                ).length;

                setStats({
                    totalDeployments: deploymentsData.length,
                    successfulDeployments: successful,
                    failedDeployments: failed,
                    activeIncidents: active,
                    criticalIncidents: critical,
                });
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        // Refresh every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return <div className="dashboard loading">Loading dashboard...</div>;
    }

    return (
        <div className="dashboard">
            <h2>Dashboard</h2>

            <div className="stats-grid">
                <StatCard
                    title="Total Deployments"
                    value={stats.totalDeployments}
                    color="#2196f3"
                />
                <StatCard
                    title="Successful"
                    value={stats.successfulDeployments}
                    color="#4caf50"
                />
                <StatCard
                    title="Failed"
                    value={stats.failedDeployments}
                    color="#f44336"
                />
                <StatCard
                    title="Active Incidents"
                    value={stats.activeIncidents}
                    color="#ff9800"
                />
                <StatCard
                    title="Critical"
                    value={stats.criticalIncidents}
                    color="#d32f2f"
                />
            </div>

            <div className="dashboard-section">
                <h3>Quick Links</h3>
                <div className="quick-links">
                    <a href="#/deployments" className="quick-link-button">
                        View Deployments
                    </a>
                    <a href="#/incidents" className="quick-link-button">
                        View Incidents
                    </a>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, color }) {
    return (
        <div className="stat-card" style={{ borderLeftColor: color }}>
            <h3>{title}</h3>
            <p className="stat-value" style={{ color }}>
                {value}
            </p>
        </div>
    );
}
