import axios, { AxiosResponse } from 'axios';
import { Flower, Order, OrderData } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const flowersAPI = {
  getAll: (): Promise<AxiosResponse<Flower[]>> => api.get('/flowers/'),
  getById: (id: number): Promise<AxiosResponse<Flower>> => api.get(`/flowers/${id}/`),
};

export const ordersAPI = {
  create: (orderData: OrderData): Promise<AxiosResponse<Order>> => api.post('/orders/', orderData),
  getAll: (): Promise<AxiosResponse<Order[]>> => api.get('/orders/'),
};

export default api;


