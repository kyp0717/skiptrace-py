import { useState, useEffect } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { caseService, skipTraceService } from '@/services/api'
import type { TownSkipTraceStats } from '@/services/api'
import { SkipTraceDialog } from '@/components/SkipTraceDialog'

export function SkipTracesPage() {
  const [towns, setTowns] = useState<string[]>([])
  const [selectedTown, setSelectedTown] = useState<string>('')
  const [selectedCounty, setSelectedCounty] = useState<string>('')
  const [docketNumber, setDocketNumber] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDialog, setShowDialog] = useState(false)
  const [townStats, setTownStats] = useState<TownSkipTraceStats | null>(null)
  const [isLoadingStats, setIsLoadingStats] = useState(false)

  // Connecticut counties
  const counties = [
    'Fairfield',
    'Hartford',
    'Litchfield',
    'Middlesex',
    'New Haven',
    'New London',
    'Tolland',
    'Windham'
  ]

  useEffect(() => {
    loadTowns()
  }, [])

  const loadTowns = async () => {
    try {
      const townList = await caseService.getConnecticutTowns()
      setTowns(townList)
    } catch (error) {
      console.error('Error loading towns:', error)
    }
  }

  const handleSkipTraceByTown = async () => {
    if (!selectedTown) {
      alert('Please select a town first')
      return
    }

    // Load skip trace statistics for the town
    setIsLoadingStats(true)
    setShowDialog(true)

    try {
      const stats = await skipTraceService.getTownStats(selectedTown)
      setTownStats(stats)
    } catch (error) {
      console.error('Error loading town stats:', error)
      setTownStats({
        town: selectedTown,
        scraped: false,
        total_cases: 0,
        traced_cases: 0,
        untraced_cases: 0,
        error: 'Failed to load statistics'
      })
    } finally {
      setIsLoadingStats(false)
    }
  }

  const handleProceedWithSkipTrace = async () => {
    if (!selectedTown || !townStats) return

    setIsLoading(true)
    try {
      await skipTraceService.performTownSkipTrace(selectedTown)
      // Reload stats after skip tracing
      const updatedStats = await skipTraceService.getTownStats(selectedTown)
      setTownStats(updatedStats)
      alert(`Skip trace completed for ${selectedTown}. Processed ${townStats.untraced_cases} cases.`)
    } catch (error) {
      console.error('Error performing skip trace:', error)
      alert('Failed to perform skip trace. Please try again.')
    } finally {
      setIsLoading(false)
      setShowDialog(false)
    }
  }

  const handleSkipTraceByCounty = () => {
    if (!selectedCounty) {
      alert('Please select a county first')
      return
    }
    console.log('Skip tracing for county:', selectedCounty)
    // TODO: Implement skip trace functionality
  }

  const handleSkipTraceByDocket = () => {
    if (!docketNumber.trim()) {
      alert('Please enter a docket number')
      return
    }
    console.log('Skip tracing for docket:', docketNumber)
    // TODO: Implement skip trace functionality
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Skip Traces</h2>
        <p className="text-gray-600 mt-1">Manage skip trace lookups and results</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-900">Total Lookups</h3>
            <p className="text-2xl font-bold text-purple-600 mt-1">0</p>
          </div>
          <div className="bg-indigo-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-indigo-900">Successful Traces</h3>
            <p className="text-2xl font-bold text-indigo-600 mt-1">0</p>
          </div>
          <div className="bg-pink-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-pink-900">Total Cost</h3>
            <p className="text-2xl font-bold text-pink-600 mt-1">$0.00</p>
          </div>
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold mb-4">Skip Trace by Town</h3>
          <div className="flex gap-4 items-center mb-6">
            <Select value={selectedTown} onValueChange={setSelectedTown}>
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select a town" />
              </SelectTrigger>
              <SelectContent>
                {towns.map((town) => (
                  <SelectItem key={town} value={town}>
                    {town}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <button
              onClick={handleSkipTraceByTown}
              disabled={!selectedTown || isLoading}
              className="px-4 py-2 bg-pink-800 text-white rounded-lg hover:bg-pink-900 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Processing...' : 'Skip Trace'}
            </button>
          </div>
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold mb-4">Skip Trace by County</h3>
          <div className="flex gap-4 items-center mb-6">
            <Select value={selectedCounty} onValueChange={setSelectedCounty}>
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select a county" />
              </SelectTrigger>
              <SelectContent>
                {counties.map((county) => (
                  <SelectItem key={county} value={county}>
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <button
              onClick={handleSkipTraceByCounty}
              disabled={!selectedCounty || isLoading}
              className="px-4 py-2 bg-pink-800 text-white rounded-lg hover:bg-pink-900 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Processing...' : 'Skip Trace'}
            </button>
          </div>
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold mb-4">Skip Trace by Docket</h3>
          <div className="flex gap-4 items-center mb-6">
            <input
              type="text"
              value={docketNumber}
              onChange={(e) => setDocketNumber(e.target.value)}
              placeholder="Enter docket number"
              className="w-[300px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              onClick={handleSkipTraceByDocket}
              disabled={!docketNumber.trim() || isLoading}
              className="px-4 py-2 bg-pink-800 text-white rounded-lg hover:bg-pink-900 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Processing...' : 'Skip Trace'}
            </button>
          </div>
        </div>
      </div>

      <SkipTraceDialog
        isOpen={showDialog}
        onClose={() => setShowDialog(false)}
        stats={townStats}
        isLoading={isLoadingStats}
        onProceed={handleProceedWithSkipTrace}
      />
    </div>
  )
}