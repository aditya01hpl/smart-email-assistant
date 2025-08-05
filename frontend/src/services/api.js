import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const getStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

export const syncEmails = async () => {
  const response = await api.post('/api/emails/sync');
  return response.data;
};

export const getEmails = async () => {
  const response = await api.get('/api/emails');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/stats'); // Replace with your actual backend route
  return response.data;
};

export const getEmailDetails = async (emailId) => {
  const response = await api.get(`/api/emails/${emailId}`);
  return response.data;
};

export const sendReply = async (emailId, content) => {
  const response = await api.post(`/api/emails/${emailId}/reply`, { content });
  return response.data;
};
export const regenerateReply = async (emailId) => {
  const response = await api.post(`/api/emails/${emailId}/regenerate-reply`);
  return response.data;
};

export const initiateAuth = async () => {
  const response = await api.get('/auth/login');
  window.location.href = response.data.auth_url;
};

export const formatTimestamp = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleDateString();
  } catch {
    return 'Unknown';
  }
};

export const getSenderInitials = (name, email) => {
  if (name) {
    const parts = name.split(' ');
    return parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0][0].toUpperCase();
  }
  return email ? email[0].toUpperCase() : '?';
};

export const getAvatarColor = (email) => {
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500'];
  return colors[email.charCodeAt(0) % colors.length];
};

export const getEmailPriority = (email) => {
  return 'normal';
};

export default api;