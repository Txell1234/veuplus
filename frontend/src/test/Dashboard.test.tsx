import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'

// Mock the API module
vi.mock('../config/api', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { agents: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  }
}))

// Helper function to render components with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Dashboard Component', () => {
  it('renders dashboard title', () => {
    renderWithRouter(<Dashboard />)
    
    const title = screen.getByText(/veuplus/i)
    expect(title).toBeInTheDocument()
  })

  it('renders navigation elements', () => {
    renderWithRouter(<Dashboard />)
    
    // Check for common navigation elements
    const convhiElement = screen.queryByText(/convhi/i)
    expect(convhiElement).toBeInTheDocument()
  })

  it('renders without crashing', () => {
    expect(() => renderWithRouter(<Dashboard />)).not.toThrow()
  })
})

describe('API Integration', () => {
  it('handles API errors gracefully', async () => {
    const mockApi = await import('../config/api')
    mockApi.default.get.mockRejectedValueOnce(new Error('API Error'))
    
    expect(() => renderWithRouter(<Dashboard />)).not.toThrow()
  })
})



