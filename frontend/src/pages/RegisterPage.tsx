import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import { AxiosError } from 'axios';
import { authAPI } from '../services/api';
import { RegisterData } from '../types';

const Container = styled.div`
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 30px;
  color: #333;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Input = styled.input`
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  &:focus {
    outline: none;
    border-color: #4caf50;
  }
`;

const Button = styled.button`
  padding: 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  &:hover {
    background: #45a049;
  }
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const Error = styled.div`
  color: red;
  font-size: 14px;
  margin-top: -10px;
`;

const LinkText = styled.div`
  text-align: center;
  margin-top: 20px;
  color: #666;
  a {
    color: #4caf50;
    text-decoration: none;
    &:hover {
      text-decoration: underline;
    }
  }
`;

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: '',
    phone: '',
  });
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.register(formData);
      const { user, tokens } = response.data;

      // Сохраняем токены и пользователя в localStorage
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(user));

      // Перенаправляем на главную страницу
      navigate('/');
    } catch (err) {
      const error = err as AxiosError<{ [key: string]: string | string[] }>;
      console.error('Registration error:', error);
      const errorData = error.response?.data;
      
      if (errorData) {
        // Обрабатываем разные форматы ошибок
        if (typeof errorData === 'string') {
          setError(errorData);
        } else if (typeof errorData === 'object') {
          // Собираем все ошибки валидации
          const errorMessages: string[] = [];
          
          Object.keys(errorData).forEach((key) => {
            const fieldErrors = errorData[key];
            if (Array.isArray(fieldErrors)) {
              fieldErrors.forEach((error: string) => {
                errorMessages.push(`${key}: ${error}`);
              });
            } else if (typeof fieldErrors === 'string') {
              errorMessages.push(`${key}: ${fieldErrors}`);
            }
          });
          
          if (errorMessages.length > 0) {
            setError(errorMessages.join(', '));
          } else {
            setError('Ошибка регистрации. Проверьте данные.');
          }
        } else {
          setError('Ошибка регистрации. Проверьте данные.');
        }
      } else {
        setError('Ошибка регистрации. Проверьте подключение к серверу.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Title>Регистрация</Title>
      <Form onSubmit={handleSubmit}>
        <Input
          type="text"
          name="username"
          placeholder="Имя пользователя"
          value={formData.username}
          onChange={handleChange}
          required
        />
        <Input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <Input
          type="text"
          name="first_name"
          placeholder="Имя"
          value={formData.first_name}
          onChange={handleChange}
          required
        />
        <Input
          type="text"
          name="last_name"
          placeholder="Фамилия"
          value={formData.last_name}
          onChange={handleChange}
        />
        <Input
          type="tel"
          name="phone"
          placeholder="Телефон (необязательно)"
          value={formData.phone}
          onChange={handleChange}
        />
        <Input
          type="password"
          name="password"
          placeholder="Пароль"
          value={formData.password}
          onChange={handleChange}
          required
        />
        <Input
          type="password"
          name="password2"
          placeholder="Подтвердите пароль"
          value={formData.password2}
          onChange={handleChange}
          required
        />
        {error && <Error>{error}</Error>}
        <Button type="submit" disabled={loading}>
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </Button>
      </Form>
      <LinkText>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </LinkText>
    </Container>
  );
};

export default RegisterPage;

