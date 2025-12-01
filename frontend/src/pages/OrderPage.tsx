import React, { useState, FormEvent, ChangeEvent } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services/api';
import { clearCart } from '../store/slices/cartSlice';
import styled from 'styled-components';
import { RootState } from '../store/store';

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

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await ordersAPI.create({
        ...formData,
        items: cart.items,
        total: cart.total,
      });
      dispatch(clearCart());
      alert('Заказ успешно оформлен!');
      navigate('/');
    } catch (error) {
      console.error('Error creating order:', error);
      alert('Ошибка при оформлении заказа');
    }
  };

  return (
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
        <Button type="submit">Подтвердить заказ</Button>
      </Form>
    </Container>
  );
};

export default OrderPage;


