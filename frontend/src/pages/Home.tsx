import React, { useEffect, useState } from 'react';
import { flowersAPI } from '../services/api';
import FlowerCard from '../components/FlowerCard';
import styled from 'styled-components';
import { Flower } from '../types';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  width: 100%;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const Home: React.FC = () => {
  const [flowers, setFlowers] = useState<Flower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    flowersAPI.getAll()
      .then(response => {
        setFlowers(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching flowers:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <Container><p>Загрузка...</p></Container>;
  }

  return (
    <Container>
      <Title>Каталог цветов</Title>
      <Grid>
        {flowers.map(flower => (
          <FlowerCard key={flower.id} flower={flower} />
        ))}
      </Grid>
    </Container>
  );
};

export default Home;


