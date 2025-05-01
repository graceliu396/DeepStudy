// API utility functions for connecting to the classroom backend
import { API_BASE_URL, WS_BASE_URL, API_ENDPOINTS, formatEndpoint } from '../config/api.config';

// Session management
export const startSession = async (fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.START_SESSION}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_id: fileId }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting session:', error);
    throw error;
  }
};

export const startNextLesson = async (sessionId, fileId) => {
  try {
    const endpoint = formatEndpoint(API_ENDPOINTS.NEXT_LESSON, { sessionId });
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_id: fileId }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting next lesson:', error);
    throw error;
  }
};

export const exitSession = async (sessionId) => {
  try {
    const endpoint = formatEndpoint(API_ENDPOINTS.EXIT_SESSION, { sessionId });
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error exiting session:', error);
    throw error;
  }
};

export const getLessonSummary = async (sessionId, lessonIndex) => {
  try {
    const endpoint = formatEndpoint(API_ENDPOINTS.LESSON_SUMMARY, { sessionId, lessonIndex });
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting lesson summary:', error);
    throw error;
  }
};

// Upload lesson plan
export const uploadLessonPlan = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.UPLOAD_LESSON_PLAN}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading lesson plan:', error);
    throw error;
  }
};

// Upload material to Azure Cosmos DB
export const uploadMaterial = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.UPLOAD_MATERIAL}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading material to Azure Cosmos DB:', error);
    throw error;
  }
};

// WebSocket connections
export const createTeachingWebSocket = (sessionId, lessonIndex, onMessage, onError) => {
  const endpoint = formatEndpoint(API_ENDPOINTS.WS_TEACHING, { sessionId, lessonIndex });
  const socket = new WebSocket(`${WS_BASE_URL}${endpoint}`);
  
  socket.onopen = () => {
    console.log('Teaching WebSocket connection established');
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  socket.onclose = () => {
    console.log('Teaching WebSocket connection closed');
  };
  
  return socket;
};

export const createDiscussionWebSocket = (sessionId, lessonIndex, onMessage, onError) => {
  const endpoint = formatEndpoint(API_ENDPOINTS.WS_DISCUSSION, { sessionId, lessonIndex });
  const socket = new WebSocket(`${WS_BASE_URL}${endpoint}`);
  
  socket.onopen = () => {
    console.log('Discussion WebSocket connection established');
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  socket.onclose = () => {
    console.log('Discussion WebSocket connection closed');
  };
  
  return socket;
}; 