import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { removeItem, updateQuantity } from '../store/slices/cartSlice';
import styled from 'styled-components';
import { RootState } from '../store/store';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  margin-bottom: 2rem;
`;

const Item = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #ddd;
`;

const QuantityInput = styled.input`
  width: 60px;
  padding: 0.5rem;
  text-align: center;
`;

const RemoveButton = styled.button`
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
`;

const Total = styled.div`
  margin-top: 2rem;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: right;
`;

const CheckoutButton = styled.button`
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.25rem;
  margin-top: 1rem;
  width: 100%;
`;

const CartPage: React.FC = () => {
  const cart = useSelector((state: RootState) => state.cart);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleQuantityChange = (id: number, quantity: string) => {
    const numQuantity = parseInt(quantity);
    if (numQuantity > 0) {
      dispatch(updateQuantity({ id, quantity: numQuantity }));
    }
  };

  const handleCheckout = () => {
    navigate('/order');
  };

  if (cart.items.length === 0) {
    return (
      <Container>
        <Title>Корзина пуста</Title>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Корзина</Title>
      {cart.items.map(item => (
        <Item key={item.id}>
          <div>
            <h3>{item.name}</h3>
            <p>{item.price} ₽ за шт.</p>
          </div>
          <div>
            <QuantityInput
              type="number"
              min="1"
              value={item.quantity}
              onChange={(e) => handleQuantityChange(item.id, e.target.value)}
            />
            <RemoveButton onClick={() => dispatch(removeItem(item.id))}>
              Удалить
            </RemoveButton>
          </div>
        </Item>
      ))}
      <Total>
        Итого: {cart.total} ₽
      </Total>
      <CheckoutButton onClick={handleCheckout}>
        Оформить заказ
      </CheckoutButton>
    </Container>
  );
};

export default CartPage;


