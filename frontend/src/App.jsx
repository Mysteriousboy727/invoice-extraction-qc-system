import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

// Helper function to format currency
const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount || 0)
}

function App() {
  const [invoices, setInvoices] = useState([])
  const [validationResults, setValidationResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showOnlyInvalid, setShowOnlyInvalid] = useState(false)
  const [backendStatus, setBackendStatus] = useState(null)

  // Check backend connection on component mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 })
        if (response.data.status === 'ok') {
          setBackendStatus('connected')
        }
      } catch (err) {
        setBackendStatus('disconnected')
      }
    }
    checkBackend()
    const interval = setInterval(checkBackend, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setLoading(true)
    setError(null)

    try {
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            const jsonData = JSON.parse(e.target.result)
            const invoiceList = Array.isArray(jsonData) ? jsonData : [jsonData]
            
            const response = await axios.post(`${API_BASE_URL}/validate-json`, {
              invoices: invoiceList
            }, {
              timeout: 30000,
              headers: {
                'Content-Type': 'application/json',
              }
            })
            
            setInvoices(invoiceList)
            setValidationResults(response.data)
          } catch (err) {
            if (err.code === 'ECONNABORTED') {
              setError('Request timeout. Please check if the backend server is running.')
            } else if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
              setError('Cannot connect to backend server. Please make sure the API is running on http://localhost:8000')
            } else if (err.response) {
              setError(`Server error: ${err.response.data?.detail || err.response.statusText}`)
            } else {
              setError(`Error processing JSON: ${err.message}`)
            }
          } finally {
            setLoading(false)
          }
        }
        reader.readAsText(file)
      } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        const formData = new FormData()
        formData.append('files', file)

        try {
          const response = await axios.post(
            `${API_BASE_URL}/extract-and-validate-pdfs`,
            formData,
            {
              timeout: 60000,
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            }
          )

          setInvoices(response.data.extracted_invoices)
          setValidationResults(response.data.validation_report)
        } catch (err) {
          if (err.code === 'ECONNABORTED') {
            setError('Request timeout. PDF processing is taking too long.')
          } else if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
            setError('Cannot connect to backend server. Please make sure the API is running on http://localhost:8000')
          } else if (err.response) {
            setError(`Server error: ${err.response.data?.detail || err.response.statusText}`)
          } else {
            setError(`Error processing PDF: ${err.message}`)
          }
        } finally {
          setLoading(false)
        }
      } else {
        setError('Unsupported file type. Please upload a PDF or JSON file.')
        setLoading(false)
      }
    } catch (err) {
      if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
        setError('Cannot connect to backend server. Please make sure the API is running on http://localhost:8000')
      } else {
        setError(`Error: ${err.response?.data?.detail || err.message}`)
      }
      setLoading(false)
    }
  }

  const getInvoiceStatus = (invoiceId) => {
    if (!validationResults) return null
    const result = validationResults.results.find(r => r.invoice_id === invoiceId)
    return result ? result.is_valid : null
  }

  const getInvoiceErrors = (invoiceId) => {
    if (!validationResults) return []
    const result = validationResults.results.find(r => r.invoice_id === invoiceId)
    return result ? result.errors : []
  }

  const filteredInvoices = showOnlyInvalid
    ? invoices.filter(inv => {
        const status = getInvoiceStatus(inv.invoice_id || inv.invoice_number)
        return status === false
      })
    : invoices

  const validCount = validationResults?.summary?.valid_invoices || 0
  const invalidCount = validationResults?.summary?.invalid_invoices || 0
  const totalCount = validationResults?.summary?.total_invoices || 0
  const successRate = totalCount > 0 ? Math.round((validCount / totalCount) * 100) : 0

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">Invoice QC Service</h1>
                <p className="text-xs text-slate-500">Quality Control Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {backendStatus && (
                <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-100">
                  <div className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                  <span className="text-xs font-medium text-slate-700">
                    {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900 mb-1">Upload Invoice</h2>
              <p className="text-sm text-slate-500">Upload PDF or JSON files for validation</p>
            </div>
            {invoices.length > 0 && (
              <div className="text-right">
                <div className="text-2xl font-bold text-slate-900">{invoices.length}</div>
                <div className="text-xs text-slate-500 uppercase tracking-wide">Invoices</div>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <label className="relative cursor-pointer group">
              <input
                type="file"
                accept=".pdf,.json"
                onChange={handleFileUpload}
                className="hidden"
                disabled={loading}
              />
              <div className="px-5 py-2.5 bg-slate-900 text-white rounded-lg font-medium text-sm hover:bg-slate-800 transition-colors duration-200 shadow-sm group-hover:shadow-md">
                {loading ? 'Processing...' : 'Choose File'}
              </div>
            </label>
            {loading && (
              <div className="flex items-center gap-2 text-slate-600">
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-sm">Processing invoice...</span>
              </div>
            )}
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-800">{error}</p>
                  {error.includes('Cannot connect to backend') && (
                    <div className="mt-2 text-xs text-red-700 bg-white p-2 rounded border border-red-200">
                      <p className="font-semibold mb-1">Quick fix:</p>
                      <p>Run <code className="bg-red-50 px-1 rounded">python run_api.py</code> in the project directory</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Summary Cards */}
        {validationResults && validationResults.summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-600">Total Invoices</span>
                <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <div className="text-3xl font-bold text-slate-900">{totalCount}</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-600">Valid</span>
                <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="text-3xl font-bold text-emerald-600">{validCount}</div>
              <div className="text-xs text-slate-500 mt-1">{successRate}% success rate</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-600">Invalid</span>
                <div className="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              </div>
              <div className="text-3xl font-bold text-red-600">{invalidCount}</div>
              <div className="text-xs text-slate-500 mt-1">{totalCount > 0 ? Math.round((invalidCount / totalCount) * 100) : 0}% need attention</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-600">Error Types</span>
                <div className="w-8 h-8 bg-amber-50 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div className="text-3xl font-bold text-amber-600">
                {Object.keys(validationResults.summary.error_counts || {}).length}
              </div>
            </div>
          </div>
        )}

        {/* Charts Section */}
        {validationResults && validationResults.summary && totalCount > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Status Distribution */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-base font-semibold text-slate-900 mb-4">Validation Status</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-600">Valid invoices</span>
                    <span className="font-medium text-slate-900">{validCount} ({successRate}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                    <div 
                      className="bg-emerald-500 h-2.5 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${successRate}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-600">Invalid invoices</span>
                    <span className="font-medium text-slate-900">{invalidCount} ({100 - successRate}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                    <div 
                      className="bg-red-500 h-2.5 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${100 - successRate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Error Breakdown */}
            {validationResults.summary.error_counts && Object.keys(validationResults.summary.error_counts).length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-base font-semibold text-slate-900 mb-4">Error Breakdown</h3>
                <div className="space-y-3">
                  {Object.entries(validationResults.summary.error_counts)
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 5)
                    .map(([type, count]) => {
                      const maxCount = Math.max(...Object.values(validationResults.summary.error_counts))
                      return (
                        <div key={type}>
                          <div className="flex justify-between text-sm mb-1.5">
                            <span className="text-slate-700 font-medium capitalize">{type.replace(/_/g, ' ')}</span>
                            <span className="text-red-600 font-semibold">{count}</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                            <div 
                              className="bg-red-500 h-2 rounded-full transition-all duration-500 ease-out"
                              style={{ width: `${(count / maxCount) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Filter Toggle */}
        {invoices.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="showInvalid"
                checked={showOnlyInvalid}
                onChange={(e) => setShowOnlyInvalid(e.target.checked)}
                className="w-4 h-4 text-red-600 border-slate-300 rounded focus:ring-red-500"
              />
              <label htmlFor="showInvalid" className="text-sm font-medium text-slate-700 cursor-pointer">
                Show only invalid invoices
              </label>
            </div>
            <div className="text-sm text-slate-500">
              Showing <span className="font-semibold text-slate-900">{filteredInvoices.length}</span> of <span className="font-semibold text-slate-900">{invoices.length}</span> invoices
            </div>
          </div>
        )}

        {/* Invoice Table */}
        {filteredInvoices.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-base font-semibold text-slate-900">Invoice Details</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Invoice ID</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Number</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Seller</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Buyer</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Total</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Errors</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {filteredInvoices.map((invoice, index) => {
                    const status = getInvoiceStatus(invoice.invoice_id || invoice.invoice_number)
                    const errors = getInvoiceErrors(invoice.invoice_id || invoice.invoice_number)
                    return (
                      <tr key={index} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                          {invoice.invoice_id || invoice.invoice_number || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                          {invoice.invoice_number || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                          {invoice.invoice_date || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                          {invoice.seller_name || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                          {invoice.buyer_name || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                          {formatCurrency(invoice.gross_total, invoice.currency)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {status === true ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                              Valid
                            </span>
                          ) : status === false ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              Invalid
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                              Unknown
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {errors.length > 0 ? (
                            <details className="cursor-pointer">
                              <summary className="text-red-600 hover:text-red-700 font-medium text-xs">
                                {errors.length} error{errors.length > 1 ? 's' : ''}
                              </summary>
                              <div className="mt-2 p-3 bg-red-50 rounded-lg border border-red-200">
                                <ul className="space-y-1.5">
                                  {errors.map((error, i) => (
                                    <li key={i} className="text-xs text-red-700 flex items-start">
                                      <span className="text-red-500 mr-2">•</span>
                                      <span className="break-words">{error}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </details>
                          ) : (
                            <span className="text-emerald-600 font-medium text-xs">No errors</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty State */}
        {invoices.length === 0 && !loading && (
          <div className="bg-white rounded-xl shadow-sm border-2 border-dashed border-slate-300 p-12 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No invoices loaded</h3>
              <p className="text-sm text-slate-500 mb-4">
                Upload a PDF or JSON file to start validating invoices
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
