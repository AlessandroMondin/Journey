import config from '../config/config';

/**
 * Register a new user
 * @param {Object} userData - User data from Google
 * @returns {Promise<Object>} - User data from backend
 */
export const registerUser = async (userData) => {
  try {
    // For Google sign-ins, we need to adapt the data to match the backend's expected format
    // Use email as username and generate a secure random password (or use google_id)
    const response = await fetch(config.AUTH_ENDPOINTS.REGISTER, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
      },
    //   credentials: 'include',
      mode: 'cors',
      body: JSON.stringify({
        username: userData.email, // Use email as username
        password: userData.sub,   // Use Google's sub (ID) as password
        // We'll store the picture and google_id in a separate call or modify the backend
      }),
    });

    if (!response.ok) {
      throw new Error(`Error registering user: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error registering user:', error);

    // Return a mock token for development until backend is ready
    console.warn('Returning mock token due to backend connection issues');
    console.warn('This is a temporary solution until your backend is properly configured');

    return {
      token: {
        access_token: 'mock_access_token',
        token_type: 'bearer',
        expires_in: 3600
      }
    };
  }
};

/**
 * Register a user with Google
 * @param {Object} userData - User data from Google
 * @returns {Promise<Object>} - User data from backend
 * @throws {Error} - If user is already registered
 */
export const googleRegister = async (userData) => {
  try {
    console.log('Attempting to register with Google:', userData.email);

    // Ensure we have name and email
    const name = userData.name || userData.given_name || '';
    const email = userData.email;

    const response = await fetch(config.AUTH_ENDPOINTS.REGISTER, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    //   credentials: 'include',
      mode: 'cors',
      body: JSON.stringify({
        username: email,
        password: userData.sub,
      }),
    });

    // Log response status for debugging
    console.log('Registration response status:', response.status);

    if (!response.ok) {
      // If user already exists, throw specific error
      if (response.status === 409 || response.status === 400) {
        throw new Error('User already registered. Please use login instead.');
      }

      // Try to get error details from response
      let errorDetail = 'Unknown error';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorDetail = response.statusText;
      }

      throw new Error(`Error registering with Google: ${errorDetail}`);
    }

    const responseData = await response.json();
    
    // Log if agent_id is present in the response
    if (responseData.agent_id) {
      console.log('Received agent_id in registration response:', responseData.agent_id);
    } else {
      console.warn('No agent_id received in registration response');
    }
    
    return responseData;
  } catch (error) {
    console.error('Error registering with Google:', error);
    throw error;
  }
};

/**
 * Login with Google
 * @param {Object} userData - User data from Google
 * @returns {Promise<Object>} - Token data from backend
 * @throws {Error} - If user does not exist
 */
export const googleLogin = async (userData) => {
  try {
    console.log('Attempting to login with Google:', userData.email);

    // Create form data instead of JSON
    const formData = new URLSearchParams();
    formData.append('username', userData.email);
    formData.append('password', userData.sub);

    const response = await fetch(config.AUTH_ENDPOINTS.TOKEN, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
      },
    //   credentials: 'include',
      mode: 'cors',
      body: formData,
    });

    // Log response status for debugging
    console.log('Login response status:', response.status);

    if (!response.ok) {
      // If user doesn't exist, throw specific error
      if (response.status === 404 || response.status === 400) {
        throw new Error('User not found. Please register first.');
      }

      // Try to get error details from response
      let errorDetail = 'Unknown error';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorDetail = response.statusText;
      }

      throw new Error(`Error logging in with Google: ${errorDetail}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error logging in with Google:', error);
    throw error;
  }
};

/**
 * Get a token for an existing user
 * @param {Object} userData - User data from Google
 * @returns {Promise<Object>} - Token data from backend
 */
export const getToken = async (userData) => {
  try {
    // For Google sign-ins, adapt to the OAuth2PasswordRequestForm expected by FastAPI
    const formData = new URLSearchParams();
    formData.append('username', userData.email);
    formData.append('password', userData.sub); // Using Google's sub as password

    const response = await fetch(config.AUTH_ENDPOINTS.TOKEN, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    //   credentials: 'include',
      mode: 'cors',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error getting token: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting token:', error);

    // Return a mock token for development until backend is ready
    console.warn('Returning mock token due to backend connection issues');
    console.warn('This is a temporary solution until your backend is properly configured');

    return {
      access_token: 'mock_access_token',
      token_type: 'bearer',
      expires_in: 3600
    };
  }
};

/**
 * Get the signed URL for the user's agent and check if voice is set
 * @param {Object} token - The user's access token
 * @returns {Promise<Object>} - Response from the backend with signed_url and has_voice_set
 */
export const getAgentSignedUrl = async (token) => {
  try {
    console.log('Getting agent signed URL');

    const response = await fetch(config.AGENT_ENDPOINTS.SIGNED_URL, {
      method: 'GET',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Authorization': `Bearer ${token.access_token}`,
        'Accept': 'application/json',
      },
    //   credentials: 'include',
      mode: 'cors',
    });

    if (!response.ok) {
      // Try to get error details from response
      let errorDetail = 'Unknown error';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorDetail = response.statusText;
      }

      throw new Error(`Error getting agent signed URL: ${errorDetail}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting agent signed URL:', error);
    throw error;
  }
};

/**
 * Set the voice for the user's agent
 * @param {Object} token - The user's access token
 * @param {Blob} audioBlob - The recorded audio blob
 * @returns {Promise<Object>} - Response from the backend
 */
export const setAgentVoice = async (token, audioBlob) => {
  try {
    console.log('Setting agent voice');

    // Create form data
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'voice-sample.webm');

    const response = await fetch(config.AGENT_ENDPOINTS.VOICE, {
      method: 'PATCH',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Authorization': `Bearer ${token.access_token}`,
      },
    //   credentials: 'include',
      mode: 'cors',
      body: formData,
    });

    if (!response.ok) {
      // Try to get error details from response
      let errorDetail = 'Unknown error';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorDetail = response.statusText;
      }

      throw new Error(`Error setting agent voice: ${errorDetail}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error setting agent voice:', error);
    throw error;
  }
};
