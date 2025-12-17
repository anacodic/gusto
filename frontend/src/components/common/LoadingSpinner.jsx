import './LoadingSpinner.css';

function LoadingSpinner({ size = 'medium', message = 'Loading...' }) {
  return (
    <div className={`loading-spinner spinner-${size}`}>
      <div className="spinner"></div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
}

export default LoadingSpinner;
