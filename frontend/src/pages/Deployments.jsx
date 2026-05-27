import React, { useState, useEffect } from 'react';
import { deployments } from '../services/api';
import '../styles/Deployments.css';

export default function Deployments() {
    const [deploymentList, setDeploymentList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        environment: '',
        status: '',
    });

    useEffect(() => {
        const fetchDeployments = async () => {
            try {
                setLoading(true);
                const data = await deployments.list({
                    limit: 50,
                    environment: filters.environment || undefined,
                    status: filters.status || undefined,
                });
                setDeploymentList(data);
            } catch (error) {
                console.error('Failed to fetch deployments:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchDeployments();
    }, [filters]);

    return (
        <div className="deployments-page">
            <h2>Deployments</h2>

            <div className="filters">
                <select
                    value={filters.environment}
                    onChange={(e) => setFilters({ ...filters, environment: e.target.value })}
                >
                    <option value="">All Environments</option>
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="development">Development</option>
                </select>

                <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="success">Success</option>
                    <option value="failed">Failed</option>
                </select>
            </div>

            {loading ? (
                <div className="loading">Loading deployments...</div>
            ) : (
                <div className="deployment-list">
                    {deploymentList.length === 0 ? (
                        <p className="empty-state">No deployments found</p>
                    ) : (
                        deploymentList.map((deployment) => (
                            <DeploymentItem key={deployment.id} deployment={deployment} />
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

function DeploymentItem({ deployment }) {
    const statusColor = {
        pending: '#ff9800',
        success: '#4caf50',
        failed: '#f44336',
    };

    return (
        <div className="deployment-card card">
            <div className="deployment-header">
                <div>
                    <h3>{deployment.name}</h3>
                    <p className="deployment-meta">
                        {deployment.application} → {deployment.environment}
                    </p>
                </div>
                <span
                    className="badge"
                    style={{ backgroundColor: statusColor[deployment.status] }}
                >
                    {deployment.status}
                </span>
            </div>

            <div className="deployment-details">
                <div>
                    <span className="label">Version:</span>
                    <span>{deployment.version}</span>
                </div>
                <div>
                    <span className="label">Created:</span>
                    <span>{new Date(deployment.created_at).toLocaleString()}</span>
                </div>
                {deployment.duration_seconds && (
                    <div>
                        <span className="label">Duration:</span>
                        <span>{deployment.duration_seconds}s</span>
                    </div>
                )}
            </div>
        </div>
    );
}
