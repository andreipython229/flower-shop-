import axios, { AxiosResponse } from 'axios';
import {
  Flower,
  Order,
  OrderData,
  AuthResponse,
  LoginData,
  RegisterData,
  User,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен в заголовки, если он есть
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок 401 (неавторизован)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('accessToken', access);
          error.config.headers.Authorization = `Bearer ${access}`;
          return api.request(error.config);
        } catch {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const flowersAPI = {
  getAll: (): Promise<AxiosResponse<Flower[]>> => api.get('/flowers/'),
  getById: (id: number): Promise<AxiosResponse<Flower>> => api.get(`/flowers/${id}/`),
};

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
  order_id: number;
}

export interface PaymentStatusResponse {
  status: string;
  order_status: string;
  order_id: number;
}

export const ordersAPI = {
  create: (orderData: OrderData): Promise<AxiosResponse<Order>> => api.post('/orders/', orderData),
  getAll: (): Promise<AxiosResponse<Order[]>> => api.get('/orders/'),
  createCheckout: (orderData: OrderData): Promise<AxiosResponse<CheckoutResponse>> =>
    api.post('/checkout/', orderData),
  checkPaymentStatus: (sessionId: string): Promise<AxiosResponse<PaymentStatusResponse>> =>
    api.get(`/payment-status/${sessionId}/`),
};

export const authAPI = {
  register: (data: RegisterData): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/register/', data),
  login: (data: LoginData): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/login/', data),
  getProfile: (): Promise<AxiosResponse<User>> => api.get('/auth/profile/'),
  refreshToken: (refresh: string): Promise<AxiosResponse<{ access: string }>> =>
    api.post('/auth/token/refresh/', { refresh }),
};

export interface Favorite {
  id: number;
  flower: Flower;
  created_at: string;
}

export const favoritesAPI = {
  getAll: (): Promise<AxiosResponse<Favorite[]>> => api.get('/favorites/'),
  add: (flowerId: number): Promise<AxiosResponse<Favorite>> =>
    api.post('/favorites/', { flower: flowerId }),
  remove: (id: number): Promise<AxiosResponse<void>> => api.delete(`/favorites/${id}/`),
};

export default api;


