import { useState } from 'react'
import { motion } from 'framer-motion'
import HistoryChart from './HistoryChart'
import PriceVisualizer from './PriceVisualizer'

function SearchBar() {
  const [url, setUrl] = useState('')
  const [scrapeResults, setScrapeResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Reset states
    setError(null)
    setScrapeResults(null)
    setIsLoading(true)

    // Call API endpoint
    try {
      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
      })

      const data = await response.json()

      // Check if API returned an error
      if (!response.ok || !data.success) {
        setError(data.error || 'Error al procesar la solicitud')
        setScrapeResults(null)
      } else {
        setScrapeResults(data)
        setError(null)
      }
    } catch (error) {
      console.error('Error calling API:', error)
      setError('Error de conexión: No se pudo conectar con el servidor. Asegúrate de que el backend esté corriendo.')
      setScrapeResults(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Title */}
        <div className="text-center mb-2">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Multi-Store Price Tracker
          </h1>
          <p className="text-gray-600">
            Rastrea precios de Amazon, MercadoLibre y más
          </p>
        </div>

        {/* Search Input */}
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Ingresa URL de Amazon, MercadoLibre..."
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-gray-700"
            required
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className={`px-8 py-3 font-semibold rounded-lg focus:outline-none focus:ring-4 transition-all whitespace-nowrap ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-300 active:scale-95'
            }`}
          >
            {isLoading ? 'Rastreando...' : 'Rastrear'}
          </button>
        </div>

        {/* Helper Text */}
        <p className="text-sm text-gray-500 text-center">
          Soportamos: Amazon, MercadoLibre (México, Argentina, Colombia, Brasil)
        </p>
      </form>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="mt-8 flex flex-col items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Rastreando producto...</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-8 bg-red-50 border-l-4 border-red-500 p-6 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-semibold text-red-800">Error</h3>
              <p className="mt-2 text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {scrapeResults && !isLoading && (() => {
        // Calculate price statistics
        const priceHistory = scrapeResults.data?.price_history || []
        const prices = priceHistory.map(entry => entry.price)
        const currentPriceFloat = prices.length > 0 ? prices[0] : null // Most recent price
        const minPrice = prices.length > 0 ? Math.min(...prices) : null
        const maxPrice = prices.length > 0 ? Math.max(...prices) : null

        // Get store name from most recent price history entry
        const storeName = priceHistory.length > 0 ? priceHistory[0].store_name : null

        // Determine badge color based on store
        const getStoreBadgeColors = (store) => {
          if (!store) return 'bg-gray-100 text-gray-800 border-gray-300'

          const storeLower = store.toLowerCase()
          if (storeLower.includes('amazon')) {
            return 'bg-orange-100 text-orange-800 border-orange-300'
          } else if (storeLower.includes('mercadolibre') || storeLower.includes('mercadolivre')) {
            return 'bg-yellow-100 text-yellow-800 border-yellow-300'
          }
          return 'bg-blue-100 text-blue-800 border-blue-300'
        }

        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          >
            <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800">
                  Información del Producto
                </h2>
                {storeName && (
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold border-2 ${getStoreBadgeColors(storeName)}`}>
                    {storeName}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left column - Product info */}
                <div className="space-y-3">
                  {scrapeResults.data?.title && (
                    <div>
                      <span className="font-semibold text-gray-700">Título: </span>
                      <span className="text-gray-600">{scrapeResults.data.title}</span>
                    </div>
                  )}

                  {scrapeResults.data?.image_url && (
                    <div>
                      <span className="font-semibold text-gray-700 block mb-2">Imagen:</span>
                      <img
                        src={scrapeResults.data.image_url}
                        alt={scrapeResults.data.title || 'Product'}
                        className="max-w-xs rounded-lg shadow-md"
                      />
                    </div>
                  )}

                  {scrapeResults.data?.product_id && (
                    <div>
                      <span className="font-semibold text-gray-700">ID del Producto: </span>
                      <span className="text-gray-600">{scrapeResults.data.product_id}</span>
                    </div>
                  )}
                </div>

                {/* Right column - Price Visualizer */}
                <div className="flex items-center justify-center">
                  {currentPriceFloat !== null && minPrice !== null && maxPrice !== null ? (
                    <PriceVisualizer
                      currentPrice={currentPriceFloat}
                      minPrice={minPrice}
                      maxPrice={maxPrice}
                    />
                  ) : scrapeResults.data?.price ? (
                    <div className="text-center">
                      <span className="font-semibold text-gray-700 block mb-2">Precio: </span>
                      <span className="text-4xl font-bold text-blue-600">{scrapeResults.data.price}</span>
                    </div>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Price History Chart */}
            {scrapeResults.data?.price_history && (
              <HistoryChart historyData={scrapeResults.data.price_history} />
            )}
          </motion.div>
        )
      })()}
    </div>
  )
}

export default SearchBar
