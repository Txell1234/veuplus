import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Home,
  Bot,
  Menu,
  X,
  Volume2,
  Radio,
  Brain,
  Headphones,
  Globe,
  Settings,
  Phone,
} from 'lucide-react'
import logo from '../assets/ambtu-logo.svg'
import { Badge } from './ui'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'ConvHi Agents', href: '/convhi-agents', icon: Bot, badge: 'Nou' },
    { name: 'SIP Configuration', href: '/convhi-sip', icon: Phone, badge: 'Config' },
    { name: 'WebRTC Configuration', href: '/convhi-webrtc', icon: Radio, badge: 'Config' },
    { name: 'ConvHi Widgets', href: '/convhi-widgets', icon: Globe, badge: 'Nou' },
    { name: 'Widget Management', href: '/convhi-widget-management', icon: Settings, badge: 'Admin' },
    { name: 'Batch Calling', href: '/convhi-batch-calling', icon: Phone, badge: 'Nou' },
    { name: 'ConvHi (complet)', href: '/convhi-agents-full', icon: Bot },
    { name: 'Veus externes', href: '/convhi-voices', icon: Volume2 },
    { name: 'Analytics', href: '/convhi-analytics', icon: Bot },
    { name: 'ALIA Kit BSC', href: '/alia-kit-bsc', icon: Brain, badge: 'BSC' },
    { name: 'Veus Edge-TTS', href: '/edge-tts-standard', icon: Radio },
    { name: 'Live Sandbox', href: '/sandbox', icon: Headphones },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="flex h-screen bg-neutral-50 text-neutral-900">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-white shadow-xl transition-transform duration-300 ease-in-out lg:static lg:inset-0 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-20 items-center justify-between border-b border-neutral-200 bg-gradient-to-br from-white to-primary-50/30 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary-600 to-primary-500 p-2.5 shadow-sm">
              <img src={logo} alt="AT Hub - Grup Amb Tu" className="h-full w-full object-contain" />
            </div>
            <div className="leading-tight">
              <p className="text-lg font-bold text-primary-900">AT Hub - Amb Tu</p>
              <p className="text-xs uppercase tracking-wide text-primary-600/80">VeuPlus Platform</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="rounded-md p-1 text-neutral-400 transition hover:bg-neutral-100 hover:text-neutral-600 lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-6 px-4 pb-32">
          <ul className="space-y-1.5">
            {navigation.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`group flex items-center justify-between rounded-xl border border-transparent px-4 py-3 text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-primary-50 text-primary-700 border-primary-200 shadow-sm'
                        : 'text-neutral-600 hover:bg-neutral-50 hover:text-primary-700'
                    }`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`flex h-9 w-9 items-center justify-center rounded-xl transition-all duration-200 ${
                          active
                            ? 'bg-gradient-to-br from-primary-600 to-primary-500 text-white shadow-md'
                            : 'bg-neutral-100 text-neutral-600 group-hover:bg-primary-50 group-hover:text-primary-600 group-hover:shadow-sm'
                        }`}
                      >
                        <Icon className={`h-5 w-5 ${active ? 'scale-110' : ''} transition-transform duration-200`} />
                      </span>
                      {item.name}
                    </div>
                    {item.badge ? (
                      <Badge variant={active ? 'accent' : 'primary'}>{item.badge}</Badge>
                    ) : null}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-neutral-200 bg-white px-4 py-4">
          <div className="flex items-center gap-3 rounded-lg bg-gradient-to-br from-primary-50 to-white p-3 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-primary-500 text-white shadow-sm">
              <span className="text-sm font-bold">AT</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-primary-900 truncate">Equip Amb Tu</p>
              <p className="text-xs text-neutral-600 truncate">Administrador</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden lg:ml-0">
        {/* Mobile top bar */}
        <header className="border-b border-neutral-200 bg-white/90 backdrop-blur lg:hidden">
          <div className="flex h-16 items-center justify-between px-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-md p-2 text-neutral-500 transition hover:text-primary-700"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="flex items-center gap-3">
              <img src={logo} alt="AT Hub - Grup Amb Tu" className="h-9 w-9 object-contain" />
              <div className="leading-tight">
                <p className="text-base font-semibold text-primary-800">AT Hub - Amb Tu</p>
                <p className="text-[11px] uppercase tracking-wide text-neutral-500">VeuPlus Platform</p>
              </div>
            </div>
            <div className="w-8" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="px-6 py-6 lg:px-10 lg:py-8">{children}</div>
        </main>
      </div>

      {/* Overlay */}
      {sidebarOpen ? (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      ) : null}
    </div>
  )
}

export default Layout
