import axios from 'axios'

// API base URL - pointing to FastAPI backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Case interface matching backend
export interface Case {
  id?: number
  case_name: string
  docket_number: string
  docket_url?: string
  town?: string
  created_at?: string
  address?: string
  zip_code?: string
  defendant_name?: string
}

// API service functions
export const caseService = {
  // Get all Connecticut towns
  async getConnecticutTowns(): Promise<string[]> {
    try {
      const response = await api.get('/api/v1/towns/')
      return response.data.map((town: any) => town.town).sort()
    } catch (error) {
      console.error('Error fetching towns:', error)
      // Fallback to local list if API fails
      return [
        'Bridgeport', 'Hartford', 'New Haven', 'Stamford', 'Waterbury',
        'Norwalk', 'Danbury', 'New Britain', 'Bristol', 'Meriden',
        'Milford', 'West Haven', 'Middletown', 'Norwich', 'Shelton',
        'Torrington', 'Naugatuck', 'Newington', 'Cheshire', 'Glastonbury',
        'Vernon', 'Windsor', 'Fairfield', 'Hamden', 'Stratford',
        'Manchester', 'Wallingford', 'East Haven', 'Enfield', 'Southington'
      ].sort()
    }
  },

  // Get towns that have been scraped (have cases in DB)
  async getScrapedTowns(): Promise<string[]> {
    try {
      // Get all cases with higher limit to ensure we get all towns
      const response = await api.get('/api/v1/cases/', {
        params: { limit: 1000 }
      })
      const cases = response.data.items || []

      // Extract unique towns from cases
      const townsSet = new Set<string>()
      cases.forEach((c: Case) => {
        if (c.town) {
          townsSet.add(c.town)
        }
      })

      return Array.from(townsSet).sort()
    } catch (error) {
      console.error('Error fetching scraped towns:', error)
      // If the API fails, try just Middletown since you mentioned it has data
      return ['Middletown']
    }
  },

  // Scrape cases for a specific town
  async scrapeTown(town: string): Promise<{ message: string; cases_found: number }> {
    try {
      const response = await api.post('/api/v1/scraper/scrape-town', { town })
      return response.data
    } catch (error) {
      console.error('Error scraping town:', error)
      throw error
    }
  },

  // Get all cases
  async getAllCases(): Promise<Case[]> {
    try {
      const response = await api.get('/api/v1/cases/')
      return response.data.items || []
    } catch (error) {
      console.error('Error fetching cases:', error)
      return []
    }
  },

  // Get cases by town - FIXED to handle nested response
  async getCasesByTown(town: string): Promise<Case[]> {
    try {
      const response = await api.get(`/api/v1/cases/by-town/${town}`)
      // The API returns { cases: [...], total: number, town: string }
      return response.data.cases || []
    } catch (error) {
      console.error('Error fetching cases by town:', error)
      return []
    }
  },

  // Get total case count
  async getTotalCaseCount(): Promise<number> {
    try {
      const response = await api.get('/api/v1/cases/')
      // Use the total from pagination metadata if available
      return response.data.total || response.data.items?.length || 0
    } catch (error) {
      console.error('Error fetching case count:', error)
      return 0
    }
  },
}

// Skip trace statistics interface
export interface TownSkipTraceStats {
  town: string
  scraped: boolean
  total_cases: number
  traced_cases: number
  untraced_cases: number
  error?: string
}

// Skip trace service
export const skipTraceService = {
  // Get skip trace statistics for a town
  async getTownStats(town: string): Promise<TownSkipTraceStats> {
    try {
      const response = await api.get(`/api/v1/skiptraces/town-stats/${town}`)
      return response.data
    } catch (error) {
      console.error('Error fetching town skip trace stats:', error)
      return {
        town,
        scraped: false,
        total_cases: 0,
        traced_cases: 0,
        untraced_cases: 0,
        error: 'Failed to fetch statistics'
      }
    }
  },

  // Perform skip trace for a town
  async performTownSkipTrace(town: string): Promise<any> {
    try {
      const response = await api.post('/api/v1/skiptraces/town-batch', { town })
      return response.data
    } catch (error) {
      console.error('Error performing town skip trace:', error)
      throw error
    }
  }
}