import { useState } from 'react'

function SearchBar() {
  const [url, setUrl] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('URL to scrape:', url)
    // TODO: Call API endpoint
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Title */}
        <div className="text-center mb-2">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Amazon Price Scraper
          </h1>
          <p className="text-gray-600">
            Ingresa la URL de un producto de Amazon para rastrear su precio
          </p>
        </div>

        {/* Search Input */}
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.amazon.com/dp/..."
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-gray-700"
            required
          />
          <button
            type="submit"
            className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-all active:scale-95 whitespace-nowrap"
          >
            Rastrear
          </button>
        </div>

        {/* Helper Text */}
        <p className="text-sm text-gray-500 text-center">
          Ejemplo: https://www.amazon.com/dp/B07RJ18VMF
        </p>
      </form>
    </div>
  )
}

export default SearchBar
