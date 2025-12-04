import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../store/store';
import { User } from '../types';

const HeaderContainer = styled.header`
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
`;

const Nav = styled.nav`
  display: flex;
  gap: 2rem;
  align-items: center;
`;

const NavLink = styled(Link)`
  color: white;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;

const CartBadge = styled.span`
  background-color: #e74c3c;
  border-radius: 50%;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  margin-left: 0.5rem;
`;

const Button = styled.button`
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  &:hover {
    background-color: #45a049;
  }
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
`;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const cartItemsCount = useSelector((state: RootState) => 
    state.cart.items.reduce((sum, item) => sum + item.quantity, 0)
  );

  const token = localStorage.getItem('accessToken');
  const userStr = localStorage.getItem('user');
  const user: User | null = userStr ? JSON.parse(userStr) : null;

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <HeaderContainer>
      <Logo to="/">🌸 Flower Shop</Logo>
      <Nav>
        <NavLink to="/">Каталог</NavLink>
        <NavLink to="/cart">
          Корзина
          {cartItemsCount > 0 && <CartBadge>{cartItemsCount}</CartBadge>}
        </NavLink>
        {token && user ? (
          <UserInfo>
            <NavLink to="/profile">Личный кабинет</NavLink>
            <span>{user.first_name} {user.last_name}</span>
            <Button onClick={handleLogout}>Выйти</Button>
          </UserInfo>
        ) : (
          <>
            <NavLink to="/login">Вход</NavLink>
            <Button onClick={() => navigate('/register')}>Регистрация</Button>
          </>
        )}
      </Nav>
    </HeaderContainer>
  );
};

export default Header;


