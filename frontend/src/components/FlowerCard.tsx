import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { addItem } from '../store/slices/cartSlice';
import styled from 'styled-components';
import { Flower } from '../types';
import { favoritesAPI } from '../services/api';

interface FlowerCardProps {
  flower: Flower;
}

const Card = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }
`;

const Image = styled.img`
  width: 100%;
  height: 250px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 1rem;
  background-color: #f5f5f5;
  display: block;
  min-height: 250px;
`;

const Title = styled.h3`
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
`;

const Price = styled.p`
  font-size: 1.5rem;
  font-weight: bold;
  color: #e74c3c;
  margin: 0.5rem 0;
`;

const Button = styled.button`
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: auto;
  &:hover {
    background-color: #229954;
  }
`;

const FavoriteButton = styled.button<{ $isFavorite: boolean }>`
  background-color: ${(props) => (props.$isFavorite ? '#f44336' : '#ff9800')};
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  width: 100%;
  &:hover {
    background-color: ${(props) => (props.$isFavorite ? '#d32f2f' : '#f57c00')};
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
`;

interface PlaceholderStyle {
  bg: string;
  circle: string;
  center: string;
}

const FlowerCard: React.FC<FlowerCardProps> = ({ flower }) => {
  const dispatch = useDispatch();
  const [isFavorite, setIsFavorite] = useState(false);
  const token = localStorage.getItem('accessToken');

  useEffect(() => {
    // Проверяем, есть ли цветок в избранном (если пользователь авторизован)
    if (token) {
      favoritesAPI
        .getAll()
        .then((response) => {
          const favoriteIds = response.data.map((f) => f.flower.id);
          setIsFavorite(favoriteIds.includes(flower.id));
        })
        .catch(() => {
          // Игнорируем ошибку, если пользователь не авторизован
        });
    }
  }, [token, flower.id]);

  const handleAddToCart = () => {
    dispatch(addItem(flower));
  };

  const handleToggleFavorite = async () => {
    if (!token) {
      alert('Войдите в систему, чтобы добавлять товары в избранное');
      return;
    }

    try {
      if (isFavorite) {
        // Находим ID избранного и удаляем
        const favorites = await favoritesAPI.getAll();
        const favorite = favorites.data.find((f) => f.flower.id === flower.id);
        if (favorite) {
          await favoritesAPI.remove(favorite.id);
          setIsFavorite(false);
        }
      } else {
        await favoritesAPI.add(flower.id);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  // КАК С СОБАЧКАМИ: Используем image_url или image, с fallback на placeholder
  // image_url может быть внешним URL или локальным путем через API
  const imageUrl = flower.image_url || (flower.image ? flower.image : null);
  
  // Генерируем уникальный цвет placeholder на основе названия цветка
  const getPlaceholderStyle = (name: string): PlaceholderStyle => {
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors: PlaceholderStyle[] = [
      { bg: '#e8f5e9', circle: '#4caf50', center: '#ffeb3b' },
      { bg: '#fff3e0', circle: '#ff9800', center: '#ffc107' },
      { bg: '#fce4ec', circle: '#e91e63', center: '#f48fb1' },
      { bg: '#e3f2fd', circle: '#2196f3', center: '#64b5f6' },
      { bg: '#f3e5f5', circle: '#9c27b0', center: '#ba68c8' },
      { bg: '#e0f2f1', circle: '#009688', center: '#4db6ac' },
      { bg: '#fff9c4', circle: '#fbc02d', center: '#fdd835' },
      { bg: '#ffebee', circle: '#f44336', center: '#ef5350' },
    ];
    return colors[hash % colors.length];
  };
  
  const placeholderStyle = getPlaceholderStyle(flower.name);

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    // Если изображение не загрузилось, показываем цветной placeholder
    e.currentTarget.style.display = 'none';
    const placeholderDiv = e.currentTarget.nextSibling as HTMLElement;
    if (placeholderDiv) placeholderDiv.style.display = 'flex';
  };

  return (
    <Card>
      {imageUrl ? (
        <Image 
          src={imageUrl} 
          alt={flower.name} 
          loading="lazy"
          onError={handleImageError}
        />
      ) : null}
      <div style={{
        width: '100%',
        height: '250px',
        backgroundColor: placeholderStyle.bg,
        borderRadius: '4px',
        marginBottom: '1rem',
        display: imageUrl ? 'none' : 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        position: 'relative'
      }}>
        <div style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          border: `3px solid ${placeholderStyle.circle}`,
          backgroundColor: placeholderStyle.bg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: placeholderStyle.center
          }}></div>
          <div style={{
            position: 'absolute',
            width: '30px',
            height: '30px',
            borderRadius: '50%',
            backgroundColor: '#fff',
            top: '20px',
            left: '20px'
          }}></div>
          <div style={{
            position: 'absolute',
            width: '30px',
            height: '30px',
            borderRadius: '50%',
            backgroundColor: '#fff',
            top: '20px',
            right: '20px'
          }}></div>
          <div style={{
            position: 'absolute',
            width: '30px',
            height: '30px',
            borderRadius: '50%',
            backgroundColor: '#fff',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)'
          }}></div>
        </div>
        <span style={{ color: '#999', marginTop: '10px', fontSize: '14px' }}>Изображение цветка</span>
      </div>
      <Title>{flower.name}</Title>
      <p>{flower.description}</p>
      <Price>{flower.price} ₽</Price>
      <ButtonGroup>
        <Button onClick={handleAddToCart}>В корзину</Button>
        <FavoriteButton $isFavorite={isFavorite} onClick={handleToggleFavorite}>
          {isFavorite ? '❤️ В избранном' : '🤍 В избранное'}
        </FavoriteButton>
      </ButtonGroup>
    </Card>
  );
};

export default FlowerCard;


