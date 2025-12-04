import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { ordersAPI } from '../services/api';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
`;

const SuccessIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1rem;
`;

const Title = styled.h1`
  color: #4caf50;
  margin-bottom: 1rem;
`;

const Message = styled.p`
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: #666;
`;

const Button = styled.button`
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  &:hover {
    background-color: #45a049;
  }
`;

const OrderSuccessPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('session_id');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    sessionId ? 'loading' : 'error'
  );

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    // Проверяем статус оплаты и обновляем заказ
    const checkStatus = async () => {
      try {
        const response = await ordersAPI.checkPaymentStatus(sessionId);
        if (response.data.status === 'paid') {
          setStatus('success');
          // Статус заказа автоматически обновится на бэкенде
        } else {
          setStatus('error');
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
        setStatus('error');
      }
    };

    checkStatus();
  }, [sessionId]);

  if (status === 'loading') {
    return (
      <Container>
        <Message>Проверка статуса оплаты...</Message>
      </Container>
    );
  }

  if (status === 'error') {
    return (
      <Container>
        <SuccessIcon>❌</SuccessIcon>
        <Title>Ошибка оплаты</Title>
        <Message>Произошла ошибка при обработке платежа. Пожалуйста, свяжитесь с поддержкой.</Message>
        <Button onClick={() => navigate('/')}>Вернуться на главную</Button>
      </Container>
    );
  }

  return (
    <Container>
      <SuccessIcon>✅</SuccessIcon>
      <Title>Оплата успешна!</Title>
      <Message>Спасибо за покупку! Ваш заказ обрабатывается.</Message>
      <Button onClick={() => navigate('/profile')}>Перейти в личный кабинет</Button>
    </Container>
  );
};

export default OrderSuccessPage;

