import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../store/store';

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

const Header: React.FC = () => {
  const cartItemsCount = useSelector((state: RootState) => 
    state.cart.items.reduce((sum, item) => sum + item.quantity, 0)
  );

  return (
    <HeaderContainer>
      <Logo to="/">🌸 Flower Shop</Logo>
      <Nav>
        <NavLink to="/">Каталог</NavLink>
        <NavLink to="/cart">
          Корзина
          {cartItemsCount > 0 && <CartBadge>{cartItemsCount}</CartBadge>}
        </NavLink>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;


