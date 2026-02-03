import axios from 'axios';

// Ensure this matches your running Python backend port (usually 8000)
const API_URL = 'http://127.0.0.1:8000';

export const registerAudioAPI = async (file, audioId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('audio_id', audioId);

  try {
    const response = await axios.post(`${API_URL}/register`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error("Registration Error:", error);
    throw error;
  }
};

export const verifyAudioAPI = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/verify`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error("Verification Error:", error);
    throw error;
  }
};