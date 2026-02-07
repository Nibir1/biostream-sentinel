import { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Activity, ShieldCheck, RefreshCw } from 'lucide-react';
import ChatAssistant from './ChatAssistant'; // Import the AI Component

interface Anomaly {
    device_id: string;
    risk_level: string;
    anomaly_score: number;
    detected_at: string;
}

export default function Dashboard() {
    const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    const fetchData = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/v1/anomalies');
            setAnomalies(response.data.data);
            setLastUpdated(new Date());
        } catch (error) {
            console.error("Failed to fetch telemetry", error);
        }
    };

    useEffect(() => {
        fetchData(); // Initial fetch
        const interval = setInterval(fetchData, 2000); // Poll every 2s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 max-w-7xl mx-auto min-h-screen bg-clinical-bg">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-ge-blue">BioStream Sentinel</h1>
                    <p className="text-slate-500">Clinical Monitoring Dashboard</p>
                </div>
                <div className="flex items-center text-sm text-slate-400 bg-white px-3 py-1 rounded-full shadow-sm">
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin-slow" />
                    Updated: {lastUpdated.toLocaleTimeString()}
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-500">System Status</p>
                            <p className="text-2xl font-bold text-slate-800">Active</p>
                        </div>
                        <ShieldCheck className="w-8 h-8 text-green-500 opacity-80" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-500">Monitored Devices</p>
                            <p className="text-2xl font-bold text-slate-800">10</p>
                        </div>
                        <Activity className="w-8 h-8 text-blue-500 opacity-80" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-500 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-500">Total Anomalies</p>
                            <p className="text-2xl font-bold text-slate-800">{anomalies.length}</p>
                        </div>
                        <AlertTriangle className="w-8 h-8 text-red-500 opacity-80" />
                    </div>
                </div>
            </div>

            {/* Main Content Grid: Table (Left) + AI Chat (Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: Anomaly Table (Spans 2 columns on large screens) */}
                <div className="lg:col-span-2 bg-white rounded-lg shadow-sm overflow-hidden border border-gray-100 h-fit">
                    <div className="px-6 py-4 border-b border-gray-100 flex items-center bg-gray-50">
                        <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                        <h2 className="text-lg font-semibold text-slate-800">High Risk Alerts</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-50 text-slate-500 uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-3 font-semibold">Device ID</th>
                                    <th className="px-6 py-3 font-semibold">Timestamp</th>
                                    <th className="px-6 py-3 font-semibold">Risk Level</th>
                                    <th className="px-6 py-3 font-semibold">Score</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {anomalies.map((alert, idx) => (
                                    <tr key={idx} className="hover:bg-blue-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900">{alert.device_id}</td>
                                        <td className="px-6 py-4 text-slate-500">
                                            {new Date(alert.detected_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                                                {alert.risk_level}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 font-mono text-slate-500">
                                            {alert.anomaly_score.toFixed(4)}
                                        </td>
                                    </tr>
                                ))}
                                {anomalies.length === 0 && (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                                            <div className="flex flex-col items-center justify-center">
                                                <ShieldCheck className="w-12 h-12 text-green-400 mb-2 opacity-50" />
                                                <p>No active anomalies detected.</p>
                                                <p className="text-xs mt-1">System operating within normal parameters.</p>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Right Column: AI Assistant (Spans 1 column) */}
                <div className="lg:col-span-1 h-full">
                    <ChatAssistant />
                </div>
            </div>
        </div>
    );
}