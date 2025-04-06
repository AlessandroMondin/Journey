// Theme configuration file for the application

// Font family configuration
const FONTS = {
  PRIMARY: "'Poppins', sans-serif",
  // Add alternative fonts if needed
  // SECONDARY: "'Open Sans', sans-serif",
};

// Font weights
const FONT_WEIGHTS = {
  THIN: 100,
  EXTRA_LIGHT: 200,
  LIGHT: 300,
  REGULAR: 400,
  MEDIUM: 500,
  SEMI_BOLD: 600,
  BOLD: 700,
  EXTRA_BOLD: 800,
  BLACK: 900,
};

// Color palette
const COLORS = {
  PRIMARY: '#2A7D4F', // Main green from the logo
  PRIMARY_DARK: '#1F6A3F', // Darker green for hover states
  TEXT_LIGHT: '#FFFFFF', // White text
  TEXT_DARK: '#333333', // Dark text
  BACKGROUND_LIGHT: '#FFFFFF', // White background
  ACCENT: '#ff4757', // Red accent for errors
  // Additional theme colors can be added here
};

// Shadows
const SHADOWS = {
  SMALL: '0 2px 5px rgba(0, 0, 0, 0.2)',
  MEDIUM: '0 4px 10px rgba(0, 0, 0, 0.2)',
  LARGE: '0 10px 30px rgba(0, 0, 0, 0.3)',
};

// Export theme configuration
const theme = {
  FONTS,
  FONT_WEIGHTS,
  COLORS,
  SHADOWS,
};

export default theme;
