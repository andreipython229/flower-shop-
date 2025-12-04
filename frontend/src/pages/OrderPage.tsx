import React, { useState, FormEvent, ChangeEvent } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { AxiosError } from 'axios';
import { ordersAPI } from '../services/api';
import { clearCart } from '../store/slices/cartSlice';
import styled from 'styled-components';
import { RootState } from '../store/store';
import Toast from '../components/Toast';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
`;

const TextArea = styled.textarea`
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-height: 100px;
`;

const Button = styled.button`
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.25rem;
  margin-top: 1rem;
  &:hover {
    background-color: #229954;
  }
`;

const PayButton = styled.button`
  background-color: #635bff;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.25rem;
  margin-top: 0.5rem;
  &:hover {
    background-color: #5851ea;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

interface OrderFormData {
  name: string;
  phone: string;
  email: string;
  address: string;
  comment: string;
}

const OrderPage: React.FC = () => {
  const cart = useSelector((state: RootState) => state.cart);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<OrderFormData>({
    name: '',
    phone: '',
    email: '',
    address: '',
    comment: '',
  });

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const [isProcessing, setIsProcessing] = useState(false);
  const [toast, setToast] = useState<{ show: boolean; message: string; type: 'success' | 'error' | 'info' }>({
    show: false,
    message: '',
    type: 'success',
  });

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setToast({ show: true, message, type });
  };

  const hideToast = () => {
    setToast({ ...toast, show: false });
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Проверяем, что корзина не пуста
    if (cart.items.length === 0) {
      alert('Корзина пуста. Добавьте товары в корзину перед оформлением заказа.');
      navigate('/');
      return;
    }

    try {
      const response = await ordersAPI.create({
        ...formData,
        items: cart.items,
        total: cart.total,
      });
      
      // Очищаем корзину только после успешного создания заказа
      dispatch(clearCart());
      showToast(`Заказ №${response.data.id} успешно оформлен! Спасибо за покупку!`, 'success');
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err) {
      const error = err as AxiosError<{ detail?: string; message?: string }>;
      console.error('Error creating order:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Ошибка при оформлении заказа';
      showToast(`Ошибка: ${errorMessage}`, 'error');
    }
  };

  const handlePayWithStripe = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    
    // Проверяем, что корзина не пуста
    if (cart.items.length === 0) {
      alert('Корзина пуста. Добавьте товары в корзину перед оформлением заказа.');
      navigate('/');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await ordersAPI.createCheckout({
        ...formData,
        items: cart.items,
        total: cart.total,
      });
      
      // Редирект на страницу оплаты Stripe
      window.location.href = response.data.checkout_url;
    } catch (err) {
      const error = err as AxiosError<{ error?: string; message?: string }>;
      console.error('Error creating checkout:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.message || 'Ошибка при создании платежа';
      alert(`Ошибка: ${errorMessage}`);
      setIsProcessing(false);
    }
  };

  return (
    <>
      <Toast
        message={toast.message}
        type={toast.type}
        show={toast.show}
        onClose={hideToast}
        duration={3000}
      />
      <Container>
        <h1>Оформление заказа</h1>
      <Form onSubmit={handleSubmit}>
        <Input
          type="text"
          name="name"
          placeholder="Имя"
          value={formData.name}
          onChange={handleInputChange}
          required
        />
        <Input
          type="tel"
          name="phone"
          placeholder="Телефон"
          value={formData.phone}
          onChange={handleInputChange}
          required
        />
        <Input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleInputChange}
          required
        />
        <Input
          type="text"
          name="address"
          placeholder="Адрес доставки"
          value={formData.address}
          onChange={handleInputChange}
          required
        />
        <TextArea
          name="comment"
          placeholder="Комментарий к заказу"
          value={formData.comment}
          onChange={handleInputChange}
        />
        <div>
          <strong>Итого: {cart.total} ₽</strong>
        </div>
        <ButtonGroup>
          <PayButton 
            type="button" 
            onClick={handlePayWithStripe}
            disabled={isProcessing}
          >
            {isProcessing ? 'Обработка...' : '💳 Оплатить онлайн'}
          </PayButton>
          <Button type="submit">Подтвердить заказ (без оплаты)</Button>
        </ButtonGroup>
      </Form>
    </Container>
    </>
  );
};

export default OrderPage;


