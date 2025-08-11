import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CallCenterDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [callCenters, setCallCenters] = useState([]);
  const [selectedCenter, setSelectedCenter] = useState(null);
  const [analytics, setAnalytics] = useState({});
  const [agents, setAgents] = useState([]);
  const [recentCalls, setRecentCalls] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const getApiBase = () => {
    const envUrl = process.env.REACT_APP_BACKEND_URL;
    if (envUrl && envUrl.trim() !== '') return `${envUrl.replace(/\/$/, '')}`;
    if (typeof window !== 'undefined' && window.location && window.location.port === '3000') {
      return 'http://localhost:8001';
    }
    return '';
  };
  const API = getApiBase();

  useEffect(() => {
    loadCallCenters();
  }, []);

  useEffect(() => {
    if (selectedCenter) {
      loadCenterData(selectedCenter.id);
    }
  }, [selectedCenter]);

  const loadCallCenters = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/api/call-center/`);
      const centers = response.data.call_centers || [];
      setCallCenters(centers);
      
      if (centers.length > 0 && !selectedCenter) {
        setSelectedCenter(centers[0]);
      }
    } catch (error) {
      console.error('Error loading call centers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCenterData = async (centerId) => {
    try {
      const [dashboardRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/api/call-center/dashboard/${centerId}`),
        axios.get(`${API}/api/call-center/analytics/${centerId}?period=7d`)
      ]);

      const dashboardData = dashboardRes.data;
      setAgents(dashboardData.agents || []);
      setRecentCalls(dashboardData.recent_calls || []);
      
      setAnalytics(analyticsRes.data.analytics || {});
      
    } catch (error) {
      console.error('Error loading center data:', error);
    }
  };

  const createCallCenter = async (centerData) => {
    try {
      const response = await axios.post(`${API}/api/call-center/create`, centerData);
      
      if (response.data.call_center_id) {
        await loadCallCenters();
        setShowCreateModal(false);
        
        // Show setup information
        alert(`Call Center created successfully!\n\nSIP Number: ${response.data.sip_number}\nWebhook URL: ${response.data.webhook_url}`);
      }
    } catch (error) {
      console.error('Error creating call center:', error);
      alert('Failed to create call center: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Call Center Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📞 Call Center Management</h1>
              <p className="text-gray-600">AI-Powered Multilingual Call Centers</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedCenter?.id || ''}
                onChange={(e) => {
                  const center = callCenters.find(c => c.id === e.target.value);
                  setSelectedCenter(center);
                }}
                className="border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">Select Call Center</option>
                {callCenters.map(center => (
                  <option key={center.id} value={center.id}>{center.name}</option>
                ))}
              </select>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
              >
                Create Call Center
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: '📊' },
              { id: 'agents', name: 'AI Agents', icon: '🤖' },
              { id: 'calls', name: 'Recent Calls', icon: '📞' },
              { id: 'analytics', name: 'Analytics', icon: '📈' },
              { id: 'settings', name: 'Settings', icon: '⚙️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!selectedCenter ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📞</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Call Centers</h3>
            <p className="text-gray-600 mb-6">Create your first AI call center to get started.</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-purple-500 text-white px-6 py-3 rounded-xl hover:bg-purple-600"
            >
              Create Call Center
            </button>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && <OverviewTab selectedCenter={selectedCenter} analytics={analytics} />}
            {activeTab === 'agents' && <AgentsTab agents={agents} selectedCenter={selectedCenter} />}
            {activeTab === 'calls' && <CallsTab recentCalls={recentCalls} />}
            {activeTab === 'analytics' && <AnalyticsTab analytics={analytics} selectedCenter={selectedCenter} />}
            {activeTab === 'settings' && <SettingsTab selectedCenter={selectedCenter} />}
          </>
        )}
      </div>

      {/* Create Call Center Modal */}
      {showCreateModal && (
        <CreateCallCenterModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createCallCenter}
        />
      )}
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ selectedCenter, analytics }) => (
  <div className="space-y-6">
    {/* Key Metrics */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Calls Today"
        value={analytics.total_calls || 0}
        icon="📞"
        color="blue"
        trend="+12%"
      />
      <MetricCard
        title="Avg Call Duration"
        value={`${analytics.avg_call_duration || 0}m`}
        icon="⏱️"
        color="green"
        trend="-8%"
      />
      <MetricCard
        title="Resolution Rate"
        value={`${Math.round((analytics.resolution_rate || 0) * 100)}%`}
        icon="✅"
        color="purple"
        trend="+5%"
      />
      <MetricCard
        title="Cost Savings"
        value={`€${analytics.cost_savings || 0}`}
        icon="💰"
        color="orange"
        trend="+€247"
      />
    </div>

    {/* Call Center Info */}
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">📍 {selectedCenter.name}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-medium text-gray-700 mb-3">Languages Supported</h4>
          <div className="flex flex-wrap gap-2">
            {JSON.parse(selectedCenter.languages || '[]').map(lang => (
              <span key={lang} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {getLanguageName(lang)}
              </span>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-medium text-gray-700 mb-3">Peak Hours</h4>
          <div className="flex flex-wrap gap-2">
            {(analytics.peak_hours || []).map(hour => (
              <span key={hour} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                {hour}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>

    {/* Quick Actions */}
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickActionCard
          title="Test Call"
          description="Make a test call to verify setup"
          icon="🧪"
          action="Test Now"
        />
        <QuickActionCard
          title="Add Agent"
          description="Create new AI agent for specific tasks"
          icon="👤"
          action="Add Agent"
        />
        <QuickActionCard
          title="View Setup"
          description="Get SIP configuration details"
          icon="🔧"
          action="View Config"
        />
      </div>
    </div>
  </div>
);

// Agents Tab Component
const AgentsTab = ({ agents, selectedCenter }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-gray-900">AI Agents</h2>
      <button className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600">
        Add New Agent
      </button>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map(agent => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  </div>
);

// Calls Tab Component
const CallsTab = ({ recentCalls }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">Recent Calls</h2>
    
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Caller
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Language
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Duration
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Time
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {recentCalls.map((call) => (
            <tr key={call.session_id}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {call.caller_number || 'Unknown'}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-sm text-gray-900">
                  {getLanguageName(call.language)}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {Math.round(call.call_duration || 0)}m
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  call.resolution_status === 'resolved' ? 'bg-green-100 text-green-800' :
                  call.resolution_status === 'escalated' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {call.resolution_status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(call.call_start).toLocaleTimeString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// Analytics Tab Component
const AnalyticsTab = ({ analytics, selectedCenter }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">Call Center Analytics</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Performance Metrics */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
        <div className="space-y-4">
          <MetricRow label="Total Calls" value={analytics.total_calls || 0} />
          <MetricRow label="Average Duration" value={`${analytics.avg_call_duration || 0} minutes`} />
          <MetricRow label="Resolution Rate" value={`${Math.round((analytics.resolution_rate || 0) * 100)}%`} />
          <MetricRow label="Satisfaction Score" value={`${analytics.satisfaction_score || 0}/5 ⭐`} />
        </div>
      </div>

      {/* Language Distribution */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Language Distribution</h3>
        <div className="space-y-3">
          {Object.entries(analytics.language_distribution || {}).map(([lang, count]) => (
            <div key={lang} className="flex justify-between items-center">
              <span className="text-gray-600">{getLanguageName(lang)}</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full" 
                    style={{ width: `${(count / analytics.total_calls) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-semibold">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Analysis */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Cost Analysis</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="text-green-700">AI Cost</span>
            <span className="font-semibold text-green-700">€{((analytics.total_calls || 0) * 0.02).toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
            <span className="text-red-700">Human Agent Cost</span>
            <span className="font-semibold text-red-700">€{((analytics.total_calls || 0) * 0.50).toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
            <span className="text-purple-700">Total Savings</span>
            <span className="font-semibold text-purple-700">€{analytics.cost_savings || 0}</span>
          </div>
        </div>
      </div>

      {/* Peak Hours */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Peak Hours</h3>
        <div className="grid grid-cols-3 gap-3">
          {(analytics.peak_hours || []).map((hour, index) => (
            <div key={hour} className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{hour}</div>
              <div className="text-xs text-blue-600">Peak #{index + 1}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// Settings Tab Component
const SettingsTab = ({ selectedCenter }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">Call Center Settings</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">SIP Configuration</h3>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">SIP Number</label>
            <input type="text" value={`+34-${selectedCenter.id.substring(0, 8)}`} readOnly 
                   className="mt-1 block w-full border-gray-300 rounded-md bg-gray-50" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Webhook URL</label>
            <input type="text" value={`https://veuplus.com/api/call-center/webhook/${selectedCenter.id}`} readOnly
                   className="mt-1 block w-full border-gray-300 rounded-md bg-gray-50" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Business Hours</h3>
        <div className="text-sm text-gray-600">
          <p>Monday - Friday: 09:00 - 18:00</p>
          <p>Saturday: 10:00 - 14:00</p>
          <p>Sunday: Closed</p>
        </div>
      </div>
    </div>
  </div>
);

// Helper Components
const MetricCard = ({ title, value, icon, color, trend }) => (
  <div className="bg-white rounded-xl shadow-sm p-6">
    <div className="flex items-center">
      <div className="text-3xl mr-4">{icon}</div>
      <div className="flex-1">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
        {trend && (
          <p className={`text-sm ${trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
            {trend} from last week
          </p>
        )}
      </div>
    </div>
  </div>
);

const QuickActionCard = ({ title, description, icon, action }) => (
  <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
    <div className="text-2xl mb-2">{icon}</div>
    <h4 className="font-semibold mb-1">{title}</h4>
    <p className="text-sm text-gray-600 mb-3">{description}</p>
    <button className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded hover:bg-purple-200">
      {action}
    </button>
  </div>
);

const AgentCard = ({ agent }) => (
  <div className="bg-white rounded-xl shadow-sm p-6">
    <div className="flex items-center mb-4">
      <div className="text-3xl mr-3">🤖</div>
      <div>
        <h4 className="font-semibold text-gray-900">{agent.name}</h4>
        <p className="text-sm text-gray-500">{agent.specialization}</p>
      </div>
    </div>
    <div className="space-y-2 text-sm">
      <div className="flex justify-between">
        <span className="text-gray-500">Languages:</span>
        <span>{JSON.parse(agent.languages || '[]').length}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-500">Total Calls:</span>
        <span>{agent.total_calls || 0}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-500">Satisfaction:</span>
        <span>{agent.avg_satisfaction || 0}/5 ⭐</span>
      </div>
    </div>
  </div>
);

const MetricRow = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-gray-600">{label}</span>
    <span className="font-semibold">{value}</span>
  </div>
);

// Create Call Center Modal
const CreateCallCenterModal = ({ onClose, onCreate }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    languages: ['ca', 'es'],
    business_hours: {
      timezone: 'Europe/Madrid'
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create Call Center</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded h-20"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Languages</label>
            <div className="space-y-2">
              {['ca', 'es', 'en', 'fr'].map(lang => (
                <label key={lang} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.languages.includes(lang)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData({...formData, languages: [...formData.languages, lang]});
                      } else {
                        setFormData({...formData, languages: formData.languages.filter(l => l !== lang)});
                      }
                    }}
                    className="mr-2"
                  />
                  {getLanguageName(lang)}
                </label>
              ))}
            </div>
          </div>
          <div className="flex space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-2 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-purple-500 text-white py-2 rounded"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Helper function
const getLanguageName = (lang) => {
  const names = {
    'ca': 'Català',
    'es': 'Español', 
    'en': 'English',
    'fr': 'Français',
    'pt': 'Português'
  };
  return names[lang] || lang.toUpperCase();
};

export default CallCenterDashboard;