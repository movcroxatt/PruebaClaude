import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function HistoryChart({ historyData }) {
  // If no history data, show a message
  if (!historyData || historyData.length === 0) {
    return (
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Historial de Precios
        </h2>
        <p className="text-gray-600">
          No hay historial de precios disponible aún. Rastrea este producto más veces para ver el gráfico.
        </p>
      </div>
    )
  }

  // Sort history by timestamp (oldest to newest for chart)
  const sortedHistory = [...historyData].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  )

  // Prepare data for Chart.js
  const labels = sortedHistory.map((entry) => {
    const date = new Date(entry.timestamp)
    return date.toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  })

  const prices = sortedHistory.map((entry) => entry.price)

  const data = {
    labels,
    datasets: [
      {
        label: 'Precio (USD)',
        data: prices,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: 'rgb(37, 99, 235)',
        pointHoverBorderColor: '#fff'
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          font: {
            size: 14,
            weight: 'bold'
          },
          color: '#374151'
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 13
        },
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function (context) {
            return `Precio: $${context.parsed.y.toFixed(2)}`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function (value) {
            return '$' + value.toFixed(2)
          },
          font: {
            size: 12
          },
          color: '#6B7280'
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6B7280',
          maxRotation: 45,
          minRotation: 45
        }
      }
    }
  }

  // Calculate price statistics
  const currentPrice = prices[prices.length - 1]
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length

  return (
    <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Historial de Precios
      </h2>

      {/* Price Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-1">Precio Actual</p>
          <p className="text-xl font-bold text-blue-600">${currentPrice.toFixed(2)}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-1">Precio Mínimo</p>
          <p className="text-xl font-bold text-green-600">${minPrice.toFixed(2)}</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-1">Precio Máximo</p>
          <p className="text-xl font-bold text-red-600">${maxPrice.toFixed(2)}</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-1">Precio Promedio</p>
          <p className="text-xl font-bold text-purple-600">${avgPrice.toFixed(2)}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-50 rounded-lg p-4">
        <Line data={data} options={options} />
      </div>

      {/* Data points count */}
      <p className="text-sm text-gray-500 mt-4 text-center">
        {historyData.length} {historyData.length === 1 ? 'registro' : 'registros'} de precio
      </p>
    </div>
  )
}

export default HistoryChart
