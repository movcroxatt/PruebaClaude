import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

function PriceVisualizer({ currentPrice, minPrice, maxPrice }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!svgRef.current || currentPrice === undefined || minPrice === undefined || maxPrice === undefined) {
      return
    }

    // Clear previous SVG content
    d3.select(svgRef.current).selectAll('*').remove()

    // SVG dimensions
    const width = 200
    const height = 400
    const margin = { top: 40, right: 40, bottom: 40, left: 40 }
    const innerHeight = height - margin.top - margin.bottom

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    // Create a group for the chart
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)

    // Create price scale - IMPORTANT: domain goes from max to min for top-to-bottom orientation
    const priceScale = d3.scaleLinear()
      .domain([maxPrice, minPrice])  // Top to bottom
      .range([0, innerHeight])

    // Add gradient definition for the scale bar
    const defs = svg.append('defs')
    const gradient = defs.append('linearGradient')
      .attr('id', 'price-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%')

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ef4444')
      .attr('stop-opacity', 0.8)

    gradient.append('stop')
      .attr('offset', '50%')
      .attr('stop-color', '#fbbf24')
      .attr('stop-opacity', 0.8)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#10b981')
      .attr('stop-opacity', 0.8)

    // Draw the vertical scale bar
    g.append('rect')
      .attr('x', 50)
      .attr('y', 0)
      .attr('width', 20)
      .attr('height', innerHeight)
      .attr('fill', 'url(#price-gradient)')
      .attr('rx', 10)
      .attr('opacity', 0.6)

    // Add tick marks and labels
    const ticks = [maxPrice, (maxPrice + minPrice) / 2, minPrice]

    ticks.forEach(tick => {
      const y = priceScale(tick)

      // Tick mark
      g.append('line')
        .attr('x1', 45)
        .attr('x2', 75)
        .attr('y1', y)
        .attr('y2', y)
        .attr('stroke', '#6b7280')
        .attr('stroke-width', 2)

      // Tick label
      g.append('text')
        .attr('x', 25)
        .attr('y', y)
        .attr('dy', '0.35em')
        .attr('text-anchor', 'end')
        .attr('fill', '#374151')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(`$${tick.toFixed(2)}`)
    })

    // Calculate position of current price bubble
    const currentY = priceScale(currentPrice)

    // Add a glow effect (drop shadow)
    const filter = defs.append('filter')
      .attr('id', 'glow')
    filter.append('feGaussianBlur')
      .attr('stdDeviation', '4')
      .attr('result', 'coloredBlur')
    const feMerge = filter.append('feMerge')
    feMerge.append('feMergeNode')
      .attr('in', 'coloredBlur')
    feMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')

    // Draw the price bubble (circle)
    const bubbleGroup = g.append('g')
      .attr('transform', `translate(60, ${currentY})`)

    // Outer ring for emphasis
    bubbleGroup.append('circle')
      .attr('r', 50)
      .attr('fill', '#3b82f6')
      .attr('opacity', 0.2)
      .attr('filter', 'url(#glow)')

    // Main bubble
    bubbleGroup.append('circle')
      .attr('r', 40)
      .attr('fill', '#3b82f6')
      .attr('opacity', 0.9)
      .attr('stroke', '#fff')
      .attr('stroke-width', 3)
      .attr('filter', 'url(#glow)')

    // Price text inside bubble
    bubbleGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.3em')
      .attr('fill', '#fff')
      .attr('font-size', '18px')
      .attr('font-weight', 'bold')
      .text(`$${currentPrice.toFixed(2)}`)

    // "Current" label
    bubbleGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '1.2em')
      .attr('fill', '#fff')
      .attr('font-size', '10px')
      .attr('font-weight', '500')
      .text('ACTUAL')

    // Add connecting line from bubble to scale
    g.append('line')
      .attr('x1', 70)
      .attr('x2', 60)
      .attr('y1', currentY)
      .attr('y2', currentY)
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('opacity', 0.5)

    // Add labels
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .attr('fill', '#1f2937')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('Escala de Precio')

  }, [currentPrice, minPrice, maxPrice])

  return (
    <div className="flex flex-col items-center">
      <svg ref={svgRef}></svg>
      <div className="mt-2 text-center">
        <p className="text-xs text-gray-500">
          Visualización D3.js
        </p>
      </div>
    </div>
  )
}

export default PriceVisualizer
