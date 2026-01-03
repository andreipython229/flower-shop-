import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { authAPI, ordersAPI, favoritesAPI } from '../services/api';
import { User, Order, Favorite, CartItem } from '../types';
import { addItem } from '../store/slices/cartSlice';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Tabs = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #ddd;
`;

const Tab = styled.button<{ $active: boolean }>`
  padding: 1rem 2rem;
  background: none;
  border: none;
  border-bottom: 3px solid ${(props) => (props.$active ? '#4caf50' : 'transparent')};
  color: ${(props) => (props.$active ? '#4caf50' : '#666')};
  font-size: 1.1rem;
  cursor: pointer;
  font-weight: ${(props) => (props.$active ? 'bold' : 'normal')};
  &:hover {
    color: #4caf50;
  }
`;

const Section = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const Title = styled.h2`
  margin-bottom: 1.5rem;
  color: #333;
`;

const OrderCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  background: #f9f9f9;
`;

const OrderHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const OrderInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Status = styled.span<{ $status?: string }>`
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  background: ${(props) => {
    switch (props.$status) {
      case 'completed':
        return '#4caf50';
      case 'processing':
        return '#ff9800';
      case 'cancelled':
        return '#f44336';
      default:
        return '#2196f3';
    }
  }};
  color: white;
`;

const Button = styled.button`
  background: #4caf50;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  &:hover {
    background: #45a049;
  }
  margin-top: 1rem;
`;

const PayButton = styled.button`
  background: #635bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 0.5rem;
  margin-right: 0.5rem;
  &:hover {
    background: #5851ea;
  }
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const FlowerGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
`;

const FlowerCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  transition: transform 0.2s;
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const FlowerImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
`;

const FlowerInfo = styled.div`
  padding: 1rem;
`;

const FlowerName = styled.h3`
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
`;

const FlowerPrice = styled.div`
  font-size: 1.2rem;
  font-weight: bold;
  color: #4caf50;
  margin: 0.5rem 0;
`;

const RemoveButton = styled.button`
  background: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
  margin-top: 0.5rem;
  &:hover {
    background: #d32f2f;
  }
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 3rem;
  color: #666;
  font-size: 1.1rem;
`;

const ProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'orders' | 'favorites'>('orders');
  const [user, setUser] = useState<User | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [profileRes, ordersRes, favoritesRes] = await Promise.all([
        authAPI.getProfile(),
        ordersAPI.getAll(),
        favoritesAPI.getAll(),
      ]);
      setUser(profileRes.data);
      setOrders(ordersRes.data);
      setFavorites(favoritesRes.data);
    } catch (error) {
      console.error('Error loading profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReorder = (order: Order) => {
    // Добавляем все товары из заказа в корзину
    order.items.forEach((item: CartItem) => {
      for (let i = 0; i < item.quantity; i++) {
        dispatch(addItem(item));
      }
    });
    navigate('/cart');
  };

  const handlePayOrder = async (order: Order) => {
    try {
      // Создаём checkout сессию для существующего заказа
      const response = await ordersAPI.createCheckout({
        name: user?.first_name || '',
        phone: user?.profile?.phone || '',
        email: user?.email || '',
        address: order.address || '',
        comment: order.comment || '',
        items: order.items,
        total: order.total,
      });
      
      // Редирект на страницу оплаты Stripe
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Ошибка при создании платежа. Попробуйте позже.');
    }
  };

  const handleRemoveFavorite = async (favoriteId: number) => {
    try {
      await favoritesAPI.remove(favoriteId);
      setFavorites(favorites.filter((f) => f.id !== favoriteId));
    } catch (error) {
      console.error('Error removing favorite:', error);
    }
  };

  const getStatusText = (status?: string) => {
    if (!status) return 'Неизвестно';
    const statusMap: { [key: string]: string } = {
      pending: 'Ожидает обработки',
      processing: 'В обработке',
      completed: 'Завершен',
      cancelled: 'Отменен',
    };
    return statusMap[status] || status;
  };

  if (loading) {
    return (
      <Container>
        <EmptyMessage>Загрузка...</EmptyMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Личный кабинет</Title>
      {user && (
        <Section>
          <h3>Профиль</h3>
          <p>
            <strong>Имя:</strong> {user.first_name} {user.last_name}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          {user.profile?.phone && (
            <p>
              <strong>Телефон:</strong> {user.profile.phone}
            </p>
          )}
        </Section>
      )}

      <Tabs>
        <Tab $active={activeTab === 'orders'} onClick={() => setActiveTab('orders')}>
          История заказов ({orders.length})
        </Tab>
        <Tab $active={activeTab === 'favorites'} onClick={() => setActiveTab('favorites')}>
          Избранное ({favorites.length})
        </Tab>
      </Tabs>

      {activeTab === 'orders' && (
        <Section>
          <Title>История заказов</Title>
          {orders.length === 0 ? (
            <EmptyMessage>У вас пока нет заказов</EmptyMessage>
          ) : (
            orders.map((order) => (
              <OrderCard key={order.id}>
                <OrderHeader>
                  <OrderInfo>
                    <strong>Заказ №{order.id}</strong>
                    <div>Дата: {new Date(order.created_at || '').toLocaleDateString('ru-RU')}</div>
                    <div>Сумма: {order.total} ₽</div>
                  </OrderInfo>
                  <Status $status={order.status || 'pending'}>
                    {getStatusText(order.status)}
                  </Status>
                </OrderHeader>
                <div>
                  <strong>Товары:</strong>
                  <ul>
                    {order.items.map((item: CartItem, index: number) => (
                      <li key={index}>
                        {item.name} - {item.quantity} шт. × {item.price} ₽
                      </li>
                    ))}
                  </ul>
                </div>
                <ButtonGroup>
                  {order.status === 'pending' && (
                    <PayButton onClick={() => handlePayOrder(order)}>
                      💳 Оплатить заказ
                    </PayButton>
                  )}
                  <Button onClick={() => handleReorder(order)}>Повторить заказ</Button>
                </ButtonGroup>
              </OrderCard>
            ))
          )}
        </Section>
      )}

      {activeTab === 'favorites' && (
        <Section>
          <Title>Избранное</Title>
          {favorites.length === 0 ? (
            <EmptyMessage>У вас пока нет избранных товаров</EmptyMessage>
          ) : (
            <FlowerGrid>
              {favorites.map((favorite) => (
                <FlowerCard key={favorite.id}>
                  <FlowerImage
                    src={favorite.flower.image_url || '/images/default-flower.jpg'}
                    alt={favorite.flower.name}
                  />
                  <FlowerInfo>
                    <FlowerName>{favorite.flower.name}</FlowerName>
                    <FlowerPrice>{favorite.flower.price} ₽</FlowerPrice>
                    <Button onClick={() => dispatch(addItem(favorite.flower))}>
                      В корзину
                    </Button>
                    <RemoveButton onClick={() => handleRemoveFavorite(favorite.id)}>
                      Удалить из избранного
                    </RemoveButton>
                  </FlowerInfo>
                </FlowerCard>
              ))}
            </FlowerGrid>
          )}
        </Section>
      )}
    </Container>
  );
};

export default ProfilePage;

