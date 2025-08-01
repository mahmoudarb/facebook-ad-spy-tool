import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Search, Upload, Eye, Calendar, ExternalLink, Loader2, Database, TrendingUp } from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [pageIds, setPageIds] = useState('')
  const [ads, setAds] = useState([])
  const [pages, setPages] = useState([])
  const [jobs, setJobs] = useState([])
  const [stats, setStats] = useState({ total_pages: 0, total_ads: 0, recent_jobs: [] })
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPage, setSelectedPage] = useState('')
  const [currentJob, setCurrentJob] = useState(null)

  // Fetch initial data
  useEffect(() => {
    fetchStats()
    fetchPages()
    fetchAds()
    fetchJobs()
  }, [])

  // Filter ads based on search and page selection
  const filteredAds = ads.filter(ad => {
    const matchesSearch = !searchTerm || 
      ad.ad_text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ad.page_id?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesPage = !selectedPage || ad.page_id === selectedPage
    return matchesSearch && matchesPage
  })

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`)
      const data = await response.json()
      if (data.success) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchPages = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/pages`)
      const data = await response.json()
      if (data.success) {
        setPages(data.pages)
      }
    } catch (error) {
      console.error('Error fetching pages:', error)
    }
  }

  const fetchAds = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ads?per_page=100`)
      const data = await response.json()
      if (data.success) {
        setAds(data.ads)
      }
    } catch (error) {
      console.error('Error fetching ads:', error)
    }
  }

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs`)
      const data = await response.json()
      if (data.success) {
        setJobs(data.jobs)
      }
    } catch (error) {
      console.error('Error fetching jobs:', error)
    }
  }

  const startScraping = async () => {
    if (!pageIds.trim()) {
      alert('Please enter at least one Page ID')
      return
    }

    setLoading(true)
    try {
      const pageIdList = pageIds.split('\n').map(id => id.trim()).filter(id => id)
      
      const response = await fetch(`${API_BASE_URL}/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page_ids: pageIdList,
          max_ads_per_page: 100
        })
      })

      const data = await response.json()
      if (data.success) {
        setCurrentJob({ id: data.job_id, status: 'running' })
        alert(`Scraping started! Job ID: ${data.job_id}`)
        
        // Poll for job status
        pollJobStatus(data.job_id)
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error starting scraping:', error)
      alert('Error starting scraping')
    } finally {
      setLoading(false)
    }
  }

  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`)
        const data = await response.json()
        
        if (data.success) {
          setCurrentJob(data.job)
          
          if (data.job.status === 'completed' || data.job.status === 'error') {
            clearInterval(pollInterval)
            setCurrentJob(null)
            
            // Refresh data
            fetchStats()
            fetchPages()
            fetchAds()
            fetchJobs()
            
            if (data.job.status === 'completed') {
              alert('Scraping completed successfully!')
            } else {
              alert(`Scraping failed: ${data.job.error_message}`)
            }
          }
        }
      } catch (error) {
        console.error('Error polling job status:', error)
        clearInterval(pollInterval)
      }
    }, 3000) // Poll every 3 seconds
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  const AdCard = ({ ad }) => (
    <Card className="mb-4 hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{pages.find(p => p.page_id === ad.page_id)?.page_name || ad.page_id}</CardTitle>
            <CardDescription>Library ID: {ad.library_id}</CardDescription>
          </div>
          <div className="flex gap-2">
            {ad.platforms?.map(platform => (
              <Badge key={platform} variant="secondary">{platform}</Badge>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <p className="text-sm text-gray-600 mb-2">{ad.ad_text}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Started: {formatDate(ad.start_date)}
              </div>
              {ad.cta && (
                <Badge variant="outline">{ad.cta}</Badge>
              )}
            </div>
          </div>
          <div className="flex justify-center items-center">
            {ad.media_url ? (
              <div className="relative">
                <img 
                  src={ad.media_url} 
                  alt="Ad creative" 
                  className="w-24 h-24 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <Badge className="absolute -top-1 -right-1 text-xs">
                  {ad.media_type}
                </Badge>
              </div>
            ) : (
              <div className="w-24 h-24 bg-gray-100 rounded-lg flex items-center justify-center">
                <Eye className="w-6 h-6 text-gray-400" />
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Facebook Ad Spy Tool</h1>
          <p className="text-gray-600">Discover and analyze Facebook ads from multiple pages</p>
        </div>

        <Tabs defaultValue="scrape" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="scrape">Scrape Ads</TabsTrigger>
            <TabsTrigger value="browse">Browse Ads</TabsTrigger>
            <TabsTrigger value="pages">Pages</TabsTrigger>
            <TabsTrigger value="jobs">Jobs</TabsTrigger>
          </TabsList>

          <TabsContent value="scrape" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Start New Scraping Job
                </CardTitle>
                <CardDescription>
                  Enter Facebook Page IDs (one per line) to scrape their ads from the Facebook Ads Library
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Enter Facebook Page IDs, one per line:&#10;20531316728&#10;123456789&#10;987654321"
                  value={pageIds}
                  onChange={(e) => setPageIds(e.target.value)}
                  rows={6}
                  className="font-mono"
                />
                <Button 
                  onClick={startScraping} 
                  disabled={loading || !pageIds.trim()}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Starting Scraping...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Start Scraping
                    </>
                  )}
                </Button>
                
                {currentJob && (
                  <Card className="bg-blue-50 border-blue-200">
                    <CardContent className="pt-4">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Job {currentJob.id} is {currentJob.status}...</span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Total Pages
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_pages}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Total Ads
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_ads}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Recent Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.recent_jobs.length}</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="browse" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Search & Filter Ads
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    placeholder="Search ads by text or page ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                  <select
                    value={selectedPage}
                    onChange={(e) => setSelectedPage(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Pages</option>
                    {pages.map(page => (
                      <option key={page.page_id} value={page.page_id}>
                        {page.page_name || page.page_id}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="text-sm text-gray-600">
                  Showing {filteredAds.length} of {ads.length} ads
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {filteredAds.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No ads found. Start by scraping some Facebook pages!</p>
                  </CardContent>
                </Card>
              ) : (
                filteredAds.map(ad => (
                  <AdCard key={ad.id} ad={ad} />
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="pages" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Scraped Pages</CardTitle>
                <CardDescription>Overview of all Facebook pages that have been scraped</CardDescription>
              </CardHeader>
              <CardContent>
                {pages.length === 0 ? (
                  <p className="text-gray-600 text-center py-4">No pages scraped yet</p>
                ) : (
                  <div className="space-y-2">
                    {pages.map(page => (
                      <div key={page.page_id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{page.page_name || page.page_id}</div>
                          <div className="text-sm text-gray-600">
                            {page.ad_count} ads • Last scraped: {formatDate(page.last_scraped)}
                          </div>
                        </div>
                        <Badge variant={page.status === 'completed' ? 'default' : 'secondary'}>
                          {page.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="jobs" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Scraping Jobs</CardTitle>
                <CardDescription>History of all scraping operations</CardDescription>
              </CardHeader>
              <CardContent>
                {jobs.length === 0 ? (
                  <p className="text-gray-600 text-center py-4">No scraping jobs yet</p>
                ) : (
                  <div className="space-y-2">
                    {jobs.map(job => (
                      <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">Job #{job.id}</div>
                          <div className="text-sm text-gray-600">
                            {job.page_ids.length} pages • Started: {formatDate(job.started_at)}
                          </div>
                          {job.error_message && (
                            <div className="text-sm text-red-600 mt-1">{job.error_message}</div>
                          )}
                        </div>
                        <Badge variant={
                          job.status === 'completed' ? 'default' : 
                          job.status === 'error' ? 'destructive' : 
                          job.status === 'running' ? 'secondary' : 'outline'
                        }>
                          {job.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

