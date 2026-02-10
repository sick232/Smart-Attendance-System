import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Helper function to format error messages
const formatErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    // If detail is an array of validation errors
    if (Array.isArray(detail)) {
      return detail.map(err => {
        if (typeof err === 'object' && err.msg) {
          return `${err.msg} (${err.loc?.join(' -> ') || 'unknown field'})`;
        }
        return String(err);
      }).join('; ');
    }
    // If detail is a string or object, convert to string
    return String(detail);
  }
  return error.message || 'An error occurred';
};

// API functions
export const registerPerson = async (name, personId, images) => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('person_id', personId);
  
  images.forEach((image, index) => {
    formData.append('images', image, `image_${index}.jpg`);
  });

  const response = await fetch(`${API_BASE_URL}/api/register`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw { response: { data: error } };
  }

  return response.json();
};

export const recognizeFace = async (imageBlob) => {
  const formData = new FormData();
  formData.append('image', imageBlob, 'capture.jpg');

  const response = await api.post('/api/recognize', formData);
  
  return response.data;
};

export const getAttendance = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);
  if (filters.personId) params.append('person_id', filters.personId);
  
  const response = await api.get(`/api/attendance?${params.toString()}`);
  return response.data;
};

export const getAllPersons = async () => {
  const response = await api.get('/api/persons');
  return response.data;
};

export const deletePerson = async (personId) => {
  const response = await api.delete(`/api/person/${personId}`);
  return response.data;
};

export const exportToCSV = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);
  if (filters.personId) params.append('person_id', filters.personId);
  
  const response = await api.get(`/api/export/csv?${params.toString()}`, {
    responseType: 'blob',
  });
  
  return response.data;
};

export const exportToExcel = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);
  if (filters.personId) params.append('person_id', filters.personId);
  
  const response = await api.get(`/api/export/excel?${params.toString()}`, {
    responseType: 'blob',
  });
  
  return response.data;
};

export default api;
