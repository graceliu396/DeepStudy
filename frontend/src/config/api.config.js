// Backend API configuration

// Base URLs
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';
export const WS_BASE_URL = process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8080';

// API endpoints
export const API_ENDPOINTS = {
  // Lesson plan upload
  UPLOAD_LESSON_PLAN: '/api/lesson-plan',
  UPLOAD_MATERIAL: '/material/upload',
  
  // Session management
  START_SESSION: '/session/start',
  NEXT_LESSON: '/session/:sessionId/next_lesson',
  EXIT_SESSION: '/session/:sessionId/exit',
  
  // Lesson interaction
  LESSON_SUMMARY: '/session/:sessionId/lesson/:lessonIndex/summary',
  
  // WebSocket endpoints
  WS_TEACHING: '/ws/session/:sessionId/lesson/:lessonIndex/teaching',
  WS_DISCUSSION: '/ws/session/:sessionId/lesson/:lessonIndex/discussion'
};

// Helper function to replace path parameters
export const formatEndpoint = (endpoint, params = {}) => {
  let formattedEndpoint = endpoint;
  
  // Replace all parameters in the endpoint
  Object.keys(params).forEach(key => {
    formattedEndpoint = formattedEndpoint.replace(`:${key}`, params[key]);
  });
  
  return formattedEndpoint;
}; 