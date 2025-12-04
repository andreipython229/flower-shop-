// Типы для цветов
export interface Flower {
  id: number;
  name: string;
  description: string;
  price: number;
  image?: string;
  image_url?: string;
}

// Типы для корзины
export interface CartItem extends Flower {
  quantity: number;
}

export interface CartState {
  items: CartItem[];
  total: number;
}

// Типы для заказов
export interface OrderData {
  name: string;
  phone: string;
  email: string;
  address: string;
  comment?: string;
  items: CartItem[];
  total: number;
}

export interface Order extends OrderData {
  id: number;
  status?: string;
  created_at?: string;
}

// Типы для авторизации
export interface UserProfile {
  phone?: string;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile?: UserProfile;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password2: string;
  phone?: string;
}

export interface Favorite {
  id: number;
  flower: Flower;
  created_at: string;
}


