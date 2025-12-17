import './Button.css';

function Button({ children, onClick, variant = 'primary', disabled = false, type = 'button' }) {
  return (
    <button
      type={type}
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

export default Button;
