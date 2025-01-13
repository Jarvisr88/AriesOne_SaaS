/**
 * Forms API client.
 * 
 * This module provides API client functions for form operations.
 */
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Form, FormSubmission, FormCreate, FormUpdate } from '../types/forms';


const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/forms`,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Create new form.
 */
export const createForm = async (data: FormCreate): Promise<Form> => {
  const response = await api.post('', data);
  return response.data;
};

/**
 * Get all forms.
 */
export const getForms = async (activeOnly = true): Promise<Form[]> => {
  const response = await api.get('', {
    params: { active_only: activeOnly },
  });
  return response.data;
};

/**
 * Get form by ID.
 */
export const getForm = async (id: number): Promise<Form> => {
  const response = await api.get(`/${id}`);
  return response.data;
};

/**
 * Update form.
 */
export const updateForm = async (
  id: number,
  data: FormUpdate
): Promise<Form> => {
  const response = await api.put(`/${id}`, data);
  return response.data;
};

/**
 * Submit form response.
 */
export const submitForm = async (
  formId: number,
  data: FormSubmission
): Promise<FormSubmission> => {
  const response = await api.post(`/${formId}/submit`, data);
  return response.data;
};

/**
 * Get form submissions.
 */
export const getFormSubmissions = async (
  formId: number
): Promise<FormSubmission[]> => {
  const response = await api.get(`/${formId}/submissions`);
  return response.data;
};
