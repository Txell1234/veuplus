import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DeveloperDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [apiKeys, setApiKeys] = useState([]);
  const [usageStats, setUsageStats] = useState({});
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newApiKey, setNewApiKey] = useState('');

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load all dashboard data in parallel
      const [keysRes, statsRes, projectsRes] = await Promise.all([
        axios.get(`${API}/dev/api-keys`),
        axios.get(`${API}/dev/analytics/usage?period=7d`),
        axios.get(`${API}/dev/projects`)
      ]);
      
      setApiKeys(keysRes.data.api_keys || []);
      setUsageStats(statsRes.data || {});
      setProjects(projectsRes.data.projects || []);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createApiKey = async (name, description) => {
    try {
      const response = await axios.post(`${API}/dev/api-keys`, {
        name,
        description,
        permissions: ['tts', 'stt', 'chat', 'training']
      });
      
      setNewApiKey(response.data.api_key);
      loadDashboardData();
      
    } catch (error) {
      console.error('Error creating API key:', error);
      alert('Failed to create API key');
    }
  };

  const revokeApiKey = async (keyId) => {
    try {
      await axios.delete(`${API}/dev/api-keys/${keyId}`);
      loadDashboardData();
    } catch (error) {
      console.error('Error revoking API key:', error);
      alert('Failed to revoke API key');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Developer Dashboard...</p>
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
              <h1 className="text-3xl font-bold text-gray-900">Developer Dashboard</h1>
              <p className="text-gray-600">VeuPlus Platform API Management</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Platform Operational</span>
              </div>
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
              { id: 'api-keys', name: 'API Keys', icon: '🔑' },
              { id: 'analytics', name: 'Analytics', icon: '📈' },
              { id: 'projects', name: 'Projects', icon: '📂' },
              { id: 'documentation', name: 'API Docs', icon: '📚' },
              { id: 'billing', name: 'Billing', icon: '💳' }
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
        {activeTab === 'overview' && <OverviewTab usageStats={usageStats} />}
        {activeTab === 'api-keys' && (
          <ApiKeysTab 
            apiKeys={apiKeys} 
            onCreateKey={createApiKey}
            onRevokeKey={revokeApiKey}
            newApiKey={newApiKey}
            setNewApiKey={setNewApiKey}
          />
        )}
        {activeTab === 'analytics' && <AnalyticsTab usageStats={usageStats} />}
        {activeTab === 'projects' && <ProjectsTab projects={projects} />}
        {activeTab === 'documentation' && <DocumentationTab />}
        {activeTab === 'billing' && <BillingTab />}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ usageStats }) => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Total Requests"
        value={usageStats.total_requests || 0}
        icon="📊"
        color="blue"
      />
      <StatCard
        title="TTS Requests"
        value={usageStats.tts_requests || 0}
        icon="🗣️"
        color="green"
      />
      <StatCard
        title="Voice Models"
        value={usageStats.voice_training_sessions || 0}
        icon="🎤"
        color="purple"
      />
      <StatCard
        title="Data Processed"
        value={`${(usageStats.data_processed_mb || 0).toFixed(1)} MB`}
        icon="💾"
        color="orange"
      />
    </div>

    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Platform Features</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <FeatureCard
          title="Hyperrealistic TTS"
          description="6 Catalan dialects with XTTS v2"
          icon="🎭"
          status="Available"
        />
        <FeatureCard
          title="Voice Training"
          description="Custom voice model training"
          icon="🏋️"
          status="Available"
        />
        <FeatureCard
          title="LLM Integration"
          description="OpenAI, Claude, Gemini support"
          icon="🧠"
          status="Available"
        />
        <FeatureCard
          title="Voicebots"
          description="Voice-enabled AI assistants"
          icon="🤖"
          status="Available"
        />
        <FeatureCard
          title="Knowledge Base"
          description="Document processing & RAG"
          icon="📚"
          status="Available"
        />
        <FeatureCard
          title="Embed Widgets"
          description="Easy website integration"
          icon="🔗"
          status="Available"
        />
      </div>
    </div>
  </div>
);

// API Keys Tab Component
const ApiKeysTab = ({ apiKeys, onCreateKey, onRevokeKey, newApiKey, setNewApiKey }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [keyDescription, setKeyDescription] = useState('');

  const handleCreateKey = async () => {
    if (!keyName) return;
    await onCreateKey(keyName, keyDescription);
    setShowCreateModal(false);
    setKeyName('');
    setKeyDescription('');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
        >
          Create New Key
        </button>
      </div>

      {newApiKey && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 mb-2">New API Key Created!</h3>
          <div className="flex items-center space-x-2">
            <code className="bg-green-100 px-3 py-1 rounded flex-1 font-mono text-sm">
              {newApiKey}
            </code>
            <button
              onClick={() => {
                navigator.clipboard.writeText(newApiKey);
                alert('API key copied to clipboard!');
              }}
              className="bg-green-500 text-white px-3 py-1 rounded text-sm"
            >
              Copy
            </button>
          </div>
          <p className="text-green-700 text-sm mt-2">
            ⚠️ Save this key securely. It won't be shown again.
          </p>
          <button
            onClick={() => setNewApiKey('')}
            className="text-green-600 text-sm mt-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {apiKeys.map((key) => (
              <tr key={key.name}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{key.name}</div>
                    <div className="text-sm text-gray-500">{key.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(key.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {key.usage_count || 0} requests
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    key.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {key.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onRevokeKey(key.key)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Revoke
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New API Key</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Name
                </label>
                <input
                  type="text"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="My App API Key"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={keyDescription}
                  onChange={(e) => setKeyDescription(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded h-20"
                  placeholder="Description of how this key will be used..."
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateKey}
                className="flex-1 bg-purple-500 text-white py-2 rounded"
              >
                Create Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Analytics Tab Component
const AnalyticsTab = ({ usageStats }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">Usage Analytics</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Request Distribution</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">TTS Requests</span>
            <span className="font-semibold">{usageStats.tts_requests || 0}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">STT Requests</span>
            <span className="font-semibold">{usageStats.stt_requests || 0}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Chat Requests</span>
            <span className="font-semibold">{usageStats.chat_requests || 0}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Training Sessions</span>
            <span className="font-semibold">{usageStats.voice_training_sessions || 0}</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Avg Response Time</span>
            <span className="font-semibold">{"< 2s"}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Success Rate</span>
            <span className="font-semibold text-green-600">99.8%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Uptime</span>
            <span className="font-semibold text-green-600">99.9%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Data Processed</span>
            <span className="font-semibold">{(usageStats.data_processed_mb || 0).toFixed(1)} MB</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Projects Tab Component
const ProjectsTab = ({ projects }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
      <button className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600">
        New Project
      </button>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <div key={project.id} className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-2">{project.name}</h3>
          <p className="text-gray-600 text-sm mb-4">{project.description}</p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">API Keys</span>
              <span>{project.api_keys?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Status</span>
              <span className={`px-2 py-1 rounded text-xs ${
                project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {project.status}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Documentation Tab Component
const DocumentationTab = () => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">API Documentation</h2>
    
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Getting Started</h3>
      <div className="prose max-w-none">
        <p className="text-gray-600 mb-4">
          Welcome to the VeuPlus Developer Platform! Get started with hyperrealistic Catalan voice synthesis.
        </p>
        
        <h4 className="font-semibold mb-2">Authentication</h4>
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <code className="text-sm">
            curl -H "Authorization: Bearer YOUR_API_KEY" \<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;https://api.veuplus.com/api/synthesis
          </code>
        </div>

        <h4 className="font-semibold mb-2">Voice Synthesis Example</h4>
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <code className="text-sm">
            POST /api/synthesis<br/>
            {JSON.stringify({
              text: "Hola, bon dia! Com estàs avui?",
              voice_model_id: "catalan_enhanced",
              language: "ca"
            }, null, 2)}
          </code>
        </div>

        <h4 className="font-semibold mb-2">Supported Catalan Dialects</h4>
        <ul className="list-disc list-inside text-gray-600 space-y-1">
          <li>Central (Barcelona, Girona)</li>
          <li>Balearic (Illes Balears)</li>
          <li>Valencian (País Valencià)</li>
          <li>Andorran (Andorra)</li>
          <li>Rossellonès (França del Nord)</li>
          <li>Alguerès (L'Alguer, Sardenya)</li>
        </ul>
      </div>
    </div>
  </div>
);

// Billing Tab Component
const BillingTab = () => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900">Billing & Usage</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Current Usage</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">TTS Minutes</span>
            <span className="font-semibold">0 / 1000</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">API Requests</span>
            <span className="font-semibold">0 / 100k</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Voice Training</span>
            <span className="font-semibold">0 / 10</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Pricing Plans</h3>
        <div className="space-y-3">
          <div className="border border-purple-200 rounded-lg p-3">
            <div className="font-semibold text-purple-600">Starter - $99/month</div>
            <div className="text-sm text-gray-600">1000 TTS hours, 1 voice model</div>
          </div>
          <div className="border border-gray-200 rounded-lg p-3">
            <div className="font-semibold">Professional - $299/month</div>
            <div className="text-sm text-gray-600">10k TTS hours, 5 voice models</div>
          </div>
          <div className="border border-gray-200 rounded-lg p-3">
            <div className="font-semibold">Enterprise - $999/month</div>
            <div className="text-sm text-gray-600">Unlimited, dedicated support</div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Helper Components
const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-white rounded-xl shadow-sm p-6">
    <div className="flex items-center">
      <div className={`text-3xl mr-4`}>{icon}</div>
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
      </div>
    </div>
  </div>
);

const FeatureCard = ({ title, description, icon, status }) => (
  <div className="border border-gray-200 rounded-lg p-4">
    <div className="flex items-center mb-2">
      <span className="text-2xl mr-3">{icon}</span>
      <h4 className="font-semibold">{title}</h4>
    </div>
    <p className="text-sm text-gray-600 mb-2">{description}</p>
    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
      {status}
    </span>
  </div>
);

export default DeveloperDashboard;