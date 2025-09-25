import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom'
import { CourtCasesPage } from './pages/court-cases'
import { SkipTracesPage } from './pages/skip-traces'

function DashboardLayout() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-4">
          <h1 className="text-xl font-bold text-gray-800">AE Solutions</h1>
        </div>
        <nav className="mt-4">
          <Link
            to="/cases"
            className="block px-4 py-2 text-gray-700 hover:bg-gray-200 hover:text-gray-900"
          >
            ⚖️ Court Cases
          </Link>
          <Link
            to="/skip-traces"
            className="block px-4 py-2 text-gray-700 hover:bg-gray-200 hover:text-gray-900"
          >
            👥 Skip Traces
          </Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route index element={<Navigate to="/cases" replace />} />
          <Route path="cases" element={<CourtCasesPage />} />
          <Route path="skip-traces" element={<SkipTracesPage />} />
        </Routes>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<DashboardLayout />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App