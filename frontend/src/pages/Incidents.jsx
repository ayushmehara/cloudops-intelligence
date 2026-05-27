import React, { useState, useEffect } from 'react';
import { incidents } from '../services/api';
import '../styles/Incidents.css';

export default function Incidents() {
    const [incidentList, setIncidentList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        severity: '',
        status: '',
    });

    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                setLoading(true);
                const data = await incidents.list({
                    limit: 50,
                    severity: filters.severity || undefined,
                    status: filters.status || undefined,
                });
                setIncidentList(data);
            } catch (error) {
                console.error('Failed to fetch incidents:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchIncidents();
    }, [filters]);

    return (
        <div className="incidents-page">
            <h2>Incidents</h2>

            <div className="filters">
                <select
                    value={filters.severity}
                    onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                >
                    <option value="">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                </select>

                <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                    <option value="">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="resolved">Resolved</option>
                </select>
            </div>

            {loading ? (
                <div className="loading">Loading incidents...</div>
            ) : (
                <div className="incident-list">
                    {incidentList.length === 0 ? (
                        <p className="empty-state">No incidents found</p>
                    ) : (
                        incidentList.map((incident) => (
                            <IncidentItem key={incident.id} incident={incident} />
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

function IncidentItem({ incident }) {
    const severityColor = {
        critical: '#d32f2f',
        high: '#f44336',
        medium: '#ff9800',
        low: '#4caf50',
    };

    return (
        <div className="incident-card card">
            <div className="incident-header">
                <div>
                    <h3>{incident.title}</h3>
                    <p className="incident-meta">{incident.service}</p>
                </div>
                <span
                    className="badge"
                    style={{ backgroundColor: severityColor[incident.severity] }}
                >
                    {incident.severity}
                </span>
            </div>

            {incident.description && (
                <p className="incident-description">{incident.description}</p>
            )}

            <div className="incident-details">
                <div>
                    <span className="label">Status:</span>
                    <span>{incident.status}</span>
                </div>
                <div>
                    <span className="label">Created:</span>
                    <span>{new Date(incident.created_at).toLocaleString()}</span>
                </div>
            </div>

            {incident.ai_analysis && (
                <div className="ai-analysis">
                    <p className="label">AI Analysis:</p>
                    <p className="analysis-text">{incident.ai_analysis}</p>
                </div>
            )}
        </div>
    );
}
