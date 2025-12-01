import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #34495e;
  color: white;
  padding: 2rem;
  text-align: center;
  margin-top: auto;
`;

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <p>© 2025 Flower Shop. Все права защищены.</p>
      <p>Контакты: info@flowershop.ru | +7 (999) 123-45-67</p>
    </FooterContainer>
  );
};

export default Footer;


