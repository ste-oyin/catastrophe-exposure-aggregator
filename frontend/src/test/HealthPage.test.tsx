import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { HealthPage } from '@/pages/HealthPage'

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>)
}

describe('HealthPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('displays health data on successful fetch', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        version: '0.1.0',
        redis: 'connected',
      }),
    } as Response)

    renderWithRouter(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByTestId('status-badge')).toHaveTextContent('healthy')
    })
    expect(screen.getByTestId('redis-badge')).toHaveTextContent('connected')
    expect(screen.getByTestId('version-text')).toHaveTextContent('v0.1.0')
  })

  it('displays error on fetch failure', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Network error'))

    renderWithRouter(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByText('Connection Error')).toBeInTheDocument()
    })
    expect(screen.getByText('Network error')).toBeInTheDocument()
  })

  it('displays degraded status when Redis is unavailable', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'degraded',
        version: '0.1.0',
        redis: 'unavailable',
      }),
    } as Response)

    renderWithRouter(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByTestId('status-badge')).toHaveTextContent('degraded')
    })
    expect(screen.getByTestId('redis-badge')).toHaveTextContent('unavailable')
  })
})
