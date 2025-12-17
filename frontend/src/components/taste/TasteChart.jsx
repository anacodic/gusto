import { useMemo } from 'react';
import './TasteChart.css';

function TasteChart({ tasteHistory = [], currentTaste = null }) {
  const chartData = useMemo(() => {
    if (!tasteHistory || tasteHistory.length === 0) {
      return null;
    }
    
    const labels = ['Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'];
    const datasets = labels.map((label, idx) => ({
      label,
      data: tasteHistory.map(entry => entry.taste_vector?.[idx] || 0),
      color: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'][idx]
    }));
    
    return { labels, datasets };
  }, [tasteHistory]);

  if (!chartData) {
    return (
      <div className="taste-chart">
        <p>No taste history available</p>
      </div>
    );
  }

  return (
    <div className="taste-chart">
      <h4>Taste Evolution</h4>
      <div className="chart-container">
        {chartData.datasets.map((dataset, idx) => (
          <div key={idx} className="chart-line">
            <div className="line-label">{dataset.label}</div>
            <div className="line-chart">
              {dataset.data.map((value, i) => (
                <div
                  key={i}
                  className="line-point"
                  style={{
                    left: `${(i / (dataset.data.length - 1)) * 100}%`,
                    bottom: `${value * 100}%`,
                    backgroundColor: dataset.color
                  }}
                  title={`${dataset.label}: ${value.toFixed(2)}`}
                />
              ))}
              {currentTaste && (
                <div
                  className="line-point current"
                  style={{
                    left: '100%',
                    bottom: `${currentTaste[idx] * 100}%`,
                    backgroundColor: dataset.color
                  }}
                  title={`Current ${dataset.label}: ${currentTaste[idx].toFixed(2)}`}
                />
              )}
            </div>
          </div>
        ))}
      </div>
      {currentTaste && (
        <div className="current-indicator">
          <span>●</span> Current taste profile
        </div>
      )}
    </div>
  );
}

export default TasteChart;
