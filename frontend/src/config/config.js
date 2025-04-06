// Configuration file for the application

// API Base URLs
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Auth endpoints
const AUTH_ENDPOINTS = {
  REGISTER: `${API_BASE_URL}/auth/register`,
  TOKEN: `${API_BASE_URL}/auth/token`,
};

// Agent endpoints
const AGENT_ENDPOINTS = {
  SIGNED_URL: `${API_BASE_URL}/agent/signed_url`,
  VOICE: `${API_BASE_URL}/agent/voice`,
};

// ElevenLabs API
const ELEVENLABS_API = {
  BASE_URL: 'https://api.elevenlabs.io',
  WS_BASE_URL: 'wss://api.elevenlabs.io',
};

// Export configuration
const config = {
  API_BASE_URL,
  AUTH_ENDPOINTS,
  AGENT_ENDPOINTS,
  ELEVENLABS_API,
};

export default config;
