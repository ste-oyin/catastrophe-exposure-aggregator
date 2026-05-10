import { Link, Route, Routes } from 'react-router-dom'
import { HealthPage } from '@/pages/HealthPage'
import { HomePage } from '@/pages/HomePage'

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border">
        <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            CatExposure
          </Link>
          <div className="flex gap-4">
            <Link
              to="/"
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              Home
            </Link>
            <Link
              to="/health"
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              Health
            </Link>
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/health" element={<HealthPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
