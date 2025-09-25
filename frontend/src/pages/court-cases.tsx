import { useState, useEffect } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { caseService, type Case } from '@/services/api'

export function CourtCasesPage() {
  const [allTowns, setAllTowns] = useState<string[]>([])
  const [scrapedTowns, setScrapedTowns] = useState<string[]>([])
  const [scrapeTown, setScrapeTown] = useState<string>('')
  const [viewTown, setViewTown] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingCases, setIsLoadingCases] = useState(false)
  const [displayedCases, setDisplayedCases] = useState<Case[]>([])
  const [totalCases, setTotalCases] = useState(0)

  // Load towns and initial data on mount
  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    // Load all Connecticut towns
    const towns = await caseService.getConnecticutTowns()
    setAllTowns(towns)

    // Load scraped towns
    await loadScrapedTowns()

    // Load total case count
    const count = await caseService.getTotalCaseCount()
    setTotalCases(count)
  }

  const loadScrapedTowns = async () => {
    const scraped = await caseService.getScrapedTowns()
    setScrapedTowns(scraped)
  }

  const handleScrape = async () => {
    if (!scrapeTown) {
      alert('Please select a town first')
      return
    }

    setIsLoading(true)

    try {
      const result = await caseService.scrapeTown(scrapeTown)

      // Refresh data after scraping
      await loadScrapedTowns()
      const count = await caseService.getTotalCaseCount()
      setTotalCases(count)

      // Auto-select the scraped town for viewing if no town was selected
      if (!viewTown) {
        setViewTown(scrapeTown)
      }

      // If the scraped town was also selected for viewing, refresh the view
      if (viewTown === scrapeTown) {
        const cases = await caseService.getCasesByTown(scrapeTown)
        setDisplayedCases(cases)
      }

      // Show success message with cases found
      const casesFound = result.cases_found || 0
      alert(`✅ Scraping completed for ${scrapeTown}.\n\nFound ${casesFound} total cases.`)
    } catch (error: any) {
      console.error('Scraping error:', error)
      // Only show error if scraping actually failed
      if (error.response?.status !== 200) {
        alert(`Error scraping ${scrapeTown}. Please try again.`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleView = async () => {
    if (!viewTown) {
      alert('Please select a town to view')
      return
    }

    setIsLoadingCases(true)

    try {
      const cases = await caseService.getCasesByTown(viewTown)
      setDisplayedCases(cases)

      if (cases.length === 0) {
        alert(`No cases found for ${viewTown}.`)
      }
    } catch (error) {
      console.error('Error loading cases:', error)
      alert(`Error loading cases for ${viewTown}. Please try again.`)
    } finally {
      setIsLoadingCases(false)
    }
  }

  // Transform API case to display format
  const formatCaseForDisplay = (apiCase: Case) => {
    return {
      docketNumber: apiCase.docket_number,
      caseName: apiCase.case_name,
      address: apiCase.address || 'N/A',
      town: apiCase.town || 'N/A',
      zipCode: apiCase.zip_code || 'N/A',
      defendantName: apiCase.defendant_name || 'N/A',
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Court Cases</h2>
        <p className="text-gray-600 mt-1">Manage and view foreclosure court cases</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {/* Stats Card */}
        <div className="mb-6">
          <div className="bg-blue-50 p-4 rounded-lg max-w-xs">
            <h3 className="text-sm font-medium text-blue-900">Total Cases</h3>
            <p className="text-2xl font-bold text-blue-600 mt-1">{totalCases}</p>
          </div>
        </div>

        {/* Town Selector and Scrape */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Scrape Court Cases</h3>
          <div className="flex gap-4 items-center">
            <div className="flex-1 max-w-xs">
              <Select value={scrapeTown} onValueChange={setScrapeTown}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a town to scrape..." />
                </SelectTrigger>
                <SelectContent>
                  {allTowns.map((town) => (
                    <SelectItem key={town} value={town}>
                      {town}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <button
              onClick={handleScrape}
              disabled={!scrapeTown || isLoading}
              className={`px-6 py-2.5 font-medium rounded-lg transition-colors ${
                scrapeTown && !isLoading
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLoading ? 'Scraping...' : 'Scrape'}
            </button>
          </div>
          {scrapeTown && (
            <p className="mt-2 text-sm text-gray-600">
              Ready to scrape court cases from {scrapeTown}
            </p>
          )}
        </div>

        {/* View Cases Section */}
        <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">View Court Cases</h3>
          <div className="flex gap-4 items-center">
            <div className="flex-1 max-w-xs">
              <Select value={viewTown} onValueChange={setViewTown}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a scraped town to view..." />
                </SelectTrigger>
                <SelectContent>
                  {scrapedTowns.length > 0 ? (
                    scrapedTowns.map((town) => (
                      <SelectItem key={town} value={town}>
                        {town}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="_none" disabled>
                      No towns scraped yet
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
            <button
              onClick={handleView}
              disabled={!viewTown || isLoadingCases || scrapedTowns.length === 0}
              className={`px-6 py-2.5 font-medium rounded-lg transition-colors ${
                viewTown && !isLoadingCases && scrapedTowns.length > 0
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLoadingCases ? 'Loading...' : 'View'}
            </button>
          </div>
          {viewTown && (
            <p className="mt-2 text-sm text-gray-600">
              Ready to view cases from {viewTown}
            </p>
          )}
          {scrapedTowns.length === 0 && (
            <p className="mt-2 text-sm text-amber-600">
              No towns have been scraped yet. Please scrape a town first.
            </p>
          )}
        </div>

        {/* Cases Table */}
        {displayedCases.length > 0 && (
          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-4">
              Court Cases - {viewTown} ({displayedCases.length} cases)
            </h3>
            <Table>
              <TableCaption>Court cases for {viewTown}</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead>Docket Number</TableHead>
                  <TableHead>Case Name</TableHead>
                  <TableHead>Address</TableHead>
                  <TableHead>Town</TableHead>
                  <TableHead>Zip Code</TableHead>
                  <TableHead>Defendant Name</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayedCases.map((caseItem) => {
                  const display = formatCaseForDisplay(caseItem)
                  return (
                    <TableRow key={display.docketNumber}>
                      <TableCell className="font-medium">{display.docketNumber}</TableCell>
                      <TableCell>{display.caseName}</TableCell>
                      <TableCell>{display.address}</TableCell>
                      <TableCell>{display.town}</TableCell>
                      <TableCell>{display.zipCode}</TableCell>
                      <TableCell>{display.defendantName}</TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        )}

        {/* Empty State */}
        {displayedCases.length === 0 && (
          <div className="border-t pt-4">
            <p className="text-gray-500 text-center py-8">
              No cases displayed. Select a town and click "View" to see court cases.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}