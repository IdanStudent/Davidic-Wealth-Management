// Minimal mock for react-chartjs-2 that renders a placeholder div
const React = require('react')

function ChartMock(props) {
  return React.createElement('div', {
    'data-testid': 'chart-mock',
    style: { width: props.width || 300, height: props.height || 150 }
  })
}

module.exports = {
  Bar: ChartMock,
  Line: ChartMock,
  Doughnut: ChartMock,
  Pie: ChartMock,
  Radar: ChartMock,
  PolarArea: ChartMock,
  Bubble: ChartMock,
  Scatter: ChartMock,
  Chart: ChartMock,
  default: ChartMock,
}
