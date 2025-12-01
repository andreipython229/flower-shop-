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
  created_at?: string;
}


