import React, { useEffect, useState, useMemo } from 'react'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  MessageSquare,
  Clock,
  Target,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Activity,
  Zap,
  Brain,
  Globe,
  Phone,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  Play,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const periodOptions = [
  { value: 'hour', label: 'Last hour', days: 1 },
  { value: 'day', label: 'Last day', days: 7 },
  { value: 'week', label: 'Last week', days: 30 },
  { value: 'month', label: 'Last month', days: 90 },
]

const SentimentChart = ({ data }) => {
  if (!data?.length) {
    return <p className="text-sm text-neutral-500">No sentiment data</p>
  }

  const sentimentData = data.reduce((acc, item) => {
    const sentiment = item.sentiment || 'neutral'
    acc[sentiment] = (acc[sentiment] || 0) + 1
    return acc
  }, {})

  const total = Object.values(sentimentData).reduce((sum, count) => sum + count, 0)

  return (
    <div className="space-y-3">
      {Object.entries(sentimentData).map(([sentiment, count]) => {
        const percentage = ((count / total) * 100).toFixed(1)
        const color = sentiment === 'positive' ? 'bg-green-500' : 
                     sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
        
        return (
          <div key={sentiment} className="flex items-center gap-3">
            <div className="w-16 text-sm capitalize text-neutral-600">{sentiment}</div>
            <div className="flex-1 bg-neutral-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${color} transition-all duration-300`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <div className="w-12 text-sm text-neutral-600 text-right">
              {count} ({percentage}%)
            </div>
          </div>
        )
      })}
    </div>
  )
}

const FunnelChart = ({ data }) => {
  if (!data?.length) {
    return <p className="text-sm text-neutral-500">No funnel data</p>
  }

  const stages = [
    { key: 'started', label: 'Started', icon: Play },
    { key: 'engaged', label: 'Engaged', icon: MessageSquare },
    { key: 'completed', label: 'Completed', icon: CheckCircle2 },
    { key: 'satisfied', label: 'Satisfied', icon: Target },
  ]

  return (
    <div className="space-y-4">
      {stages.map((stage, index) => {
        const count = data.filter(item => item.stage === stage.key).length
        const percentage = data.length > 0 ? ((count / data.length) * 100).toFixed(1) : 0
        const Icon = stage.icon
        
        return (
          <div key={stage.key} className="relative">
            <div className="flex items-center gap-3 p-3 bg-white border border-neutral-200 rounded-lg">
              <Icon className="w-5 h-5 text-primary-500" />
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-neutral-900">{stage.label}</span>
                  <span className="text-sm text-neutral-600">{count} ({percentage}%)</span>
                </div>
                <div className="mt-2 bg-neutral-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
            {index < stages.length - 1 && (
              <div className="absolute left-6 top-full w-px h-4 bg-neutral-300" />
            )}
          </div>
        )
      })}
    </div>
  )
}

const TimelineChart = ({ data }) => {
  if (!data?.length) {
    return <p className="text-sm text-neutral-500">No timeline data</p>
  }

  const maxValue = Math.max(...data.map(d => d.total_conversations || 0), 1)

  return (
    <div className="space-y-2">
      {data.map((item, index) => {
        const height = ((item.total_conversations || 0) / maxValue) * 100
        return (
          <div key={index} className="flex items-end gap-2">
            <div className="w-20 text-xs text-neutral-600 truncate">
              {new Date(item.date).toLocaleDateString('ca-ES', { month: 'short', day: 'numeric' })}
            </div>
            <div className="flex-1 bg-neutral-200 rounded relative h-8">
              <div
                className="bg-primary-500 rounded h-8 transition-all duration-300 flex items-center justify-end pr-2"
                style={{ width: `${height}%` }}
              >
                {item.total_conversations > 0 && (
                  <span className="text-xs text-white font-medium">
                    {item.total_conversations}
                  </span>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

const PerformanceMetrics = ({ data }) => {
  const metrics = useMemo(() => {
    if (!data?.length) return {}

    const totalConversations = data.length
    const completedConversations = data.filter(c => c.status === 'completed').length
    const avgDuration = data.reduce((sum, c) => sum + (c.duration || 0), 0) / totalConversations
    const satisfactionRate = data.filter(c => c.satisfaction_score >= 4).length / totalConversations * 100

    return {
      totalConversations,
      completionRate: (completedConversations / totalConversations * 100).toFixed(1),
      avgDuration: Math.round(avgDuration),
      satisfactionRate: satisfactionRate.toFixed(1)
    }
  }, [data])

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="text-center p-4 bg-blue-50 rounded-lg">
        <div className="text-2xl font-bold text-blue-600">{metrics.totalConversations || 0}</div>
        <div className="text-sm text-blue-700">Converses totals</div>
      </div>
      <div className="text-center p-4 bg-green-50 rounded-lg">
        <div className="text-2xl font-bold text-green-600">{metrics.completionRate || 0}%</div>
        <div className="text-sm text-green-700">Taxa de completació</div>
      </div>
      <div className="text-center p-4 bg-orange-50 rounded-lg">
        <div className="text-2xl font-bold text-orange-600">{metrics.avgDuration || 0}s</div>
        <div className="text-sm text-orange-700">Durada mitjana</div>
      </div>
      <div className="text-center p-4 bg-purple-50 rounded-lg">
        <div className="text-2xl font-bold text-purple-600">{metrics.satisfactionRate || 0}%</div>
        <div className="text-sm text-purple-700">Satisfacció</div>
      </div>
    </div>
  )
}

export default function ConvHiAnalytics() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [period, setPeriod] = useState('day')
  const [agentFilter, setAgentFilter] = useState('all')
  const [timeline, setTimeline] = useState([])
  const [agentOptions, setAgentOptions] = useState([])
  const [sentimentData, setSentimentData] = useState([])
  const [funnelData, setFunnelData] = useState([])
  const [performanceData, setPerformanceData] = useState([])
  const [realTimeStats, setRealTimeStats] = useState({
    activeUsers: 0,
    currentConversations: 0,
    avgResponseTime: 0,
    systemHealth: 'healthy'
  })

  // Real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      loadRealTimeStats()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const loadRealTimeStats = async () => {
    try {
      const response = await api.get('/api/convhi/analytics/realtime')
      setRealTimeStats(response.data)
    } catch (error) {
      console.error('Error loading real-time stats:', error)
    }
  }

  const exportAnalytics = async () => {
    try {
      const response = await api.get('/api/convhi/analytics/export', {
        params: { period, agent_id: agentFilter }
      })
      
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `veuplus-analytics-${period}-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast.success('Analytics exportats correctament')
    } catch (error) {
      console.error('Error exporting analytics:', error)
      toast.error('Error exportant analytics')
    }
  }

  const loadTimeline = async (periodValue = period, agentValue = agentFilter) => {
    try {
      setLoading(true)
      const option = periodOptions.find((p) => p.value === periodValue)
      const days = option?.days || 30

      const [timelineRes, sentimentRes, funnelRes, performanceRes] = await Promise.all([
        api.get('/api/convhi/analytics/timeline', {
          params: { days, agent_id: agentValue === 'all' ? undefined : agentValue },
        }),
        api.get('/api/convhi/analytics/sentiment', {
          params: { days, agent_id: agentValue === 'all' ? undefined : agentValue },
        }),
        api.get('/api/convhi/analytics/funnel', {
          params: { days, agent_id: agentValue === 'all' ? undefined : agentValue },
        }),
        api.get('/api/convhi/analytics/performance', {
          params: { days, agent_id: agentValue === 'all' ? undefined : agentValue },
        }),
      ])

      setTimeline(timelineRes.data.timeline || [])
      setSentimentData(sentimentRes.data.sentiment_data || [])
      setFunnelData(funnelRes.data.funnel_data || [])
      setPerformanceData(performanceRes.data.performance_data || [])
    } catch (error) {
      console.error('Error loading analytics:', error)
      toast.error('Error carregant analytics')
    } finally {
      setLoading(false)
    }
  }

  const loadSummary = async (periodValue = period, agentValue = agentFilter) => {
    try {
      setLoading(true)
      const query = new URLSearchParams({ period: periodValue })
      if (agentValue && agentValue !== 'all') {
        query.append('agent_id', agentValue)
      }
      const response = await api.get(`/api/convhi/analytics/dashboard?${query.toString()}`)
      setSummary(response.data || {})
    } catch (error) {
      console.error('Summary error', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAgents = async () => {
    try {
      const response = await api.get('/api/convhi/agents')
      const options = (response.data?.agents || []).map((agent) => ({
        value: agent.id,
        label: agent.name ? `${agent.name} (${agent.id})` : agent.id,
      }))
      setAgentOptions(options)
    } catch (error) {
      console.error('Agents fetch error', error)
    }
  }

  useEffect(() => {
    loadAgents()
  }, [])

  useEffect(() => {
    loadSummary(period, agentFilter)
    loadTimeline(period, agentFilter)
  }, [period, agentFilter])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-primary-500" />
            ConvHi Analytics
          </h1>
          <p className="text-sm text-gray-600">
            Anàlisi avançada de converses, rendiment i mètriques en temps real.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={exportAnalytics}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Exportar
          </button>
          <button
            onClick={() => {
              loadSummary()
              loadTimeline()
              loadRealTimeStats()
            }}
            disabled={loading}
            className="btn-primary inline-flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Actualitzar
          </button>
          <select
            className="input-field"
            value={agentFilter}
            onChange={(event) => setAgentFilter(event.target.value)}
          >
            <option value="all">All agents</option>
            {agentOptions.map((agent) => (
              <option key={agent.value} value={agent.value}>
                {agent.label}
              </option>
            ))}
          </select>
          <select
            className="input-field"
            value={period}
            onChange={(event) => setPeriod(event.target.value)}
          >
            {periodOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? <div className="text-sm text-gray-600">Loading analytics...</div> : null}

      {!loading && summary ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="card border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Total conversations</div>
              <div className="text-2xl font-semibold">
                {summary.conversation_metrics?.total_conversations ?? 0}
              </div>
            </div>
            <div className="card border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Average duration (s)</div>
              <div className="text-2xl font-semibold">
                {Math.round((summary.conversation_metrics?.average_duration ?? 0) * 10) / 10}
              </div>
            </div>
            <div className="card border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Active calls</div>
              <div className="text-2xl font-semibold">
                {summary.real_time_metrics?.active_calls ?? 0}
              </div>
            </div>
            <div className="card border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Conversations today</div>
              <div className="text-2xl font-semibold">
                {summary.real_time_metrics?.calls_today ?? 0}
              </div>
            </div>
          </div>

          <div className="card border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-3">Language breakdown</h3>
            {summary.language_breakdown?.length ? (
              <ul className="list-disc space-y-1 pl-6 text-sm text-gray-700">
                {summary.language_breakdown.map((item, index) => (
                  <li key={`${item.language}-${index}`}>
                    {(item.language || '').toUpperCase()} - {item.total_calls} calls ({Math.round((item.percentage || 0) * 10) / 10}%)
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-600">No language data</p>
            )}
          </div>

          <div className="card border border-gray-200 p-6">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Timeline</h3>
              <p className="text-xs text-gray-500">
                Showing daily totals for the selected period
              </p>
            </div>
            <TimelineChart data={timeline} />
          </div>
        </div>
      ) : null}

      {/* Analytics avançats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Anàlisi de sentiment */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary-500" />
            Anàlisi de Sentiment
          </h3>
          <SentimentChart data={sentimentData} />
        </div>

        {/* Funnel de conversió */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-primary-500" />
            Funnel de Conversió
          </h3>
          <FunnelChart data={funnelData} />
        </div>
      </div>

      {/* Mètriques de rendiment */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary-500" />
          Mètriques de Rendiment
        </h3>
        <PerformanceMetrics data={performanceData} />
      </div>

      {/* Estadístiques en temps real */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary-500" />
          Estadístiques en Temps Real
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-green-600">{realTimeStats.activeUsers}</div>
            <div className="text-sm text-green-700">Usuaris actius</div>
          </div>
          
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              <MessageSquare className="w-6 h-6 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-blue-600">{realTimeStats.currentConversations}</div>
            <div className="text-sm text-blue-700">Converses actives</div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-orange-600">{realTimeStats.avgResponseTime}ms</div>
            <div className="text-sm text-orange-700">Temps de resposta</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              {realTimeStats.systemHealth === 'healthy' ? (
                <CheckCircle2 className="w-6 h-6 text-purple-600" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-600" />
              )}
            </div>
            <div className={`text-2xl font-bold ${
              realTimeStats.systemHealth === 'healthy' ? 'text-purple-600' : 'text-red-600'
            }`}>
              {realTimeStats.systemHealth === 'healthy' ? 'OK' : 'Error'}
            </div>
            <div className={`text-sm ${
              realTimeStats.systemHealth === 'healthy' ? 'text-purple-700' : 'text-red-700'
            }`}>
              Estat del sistema
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
