import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

// Настраиваем axios для включения куки в запросы (для сессий)
axios.defaults.withCredentials = true;

// Получение токена аутентификации из localStorage (если есть)
const getAuthToken = () => localStorage.getItem('authToken');

// Настройка axios-экземпляра с заголовками авторизации
const createAuthInstance = () => {
  const token = getAuthToken();
  return axios.create({
    baseURL: API_URL,
    headers: token ? { Authorization: `Token ${token}` } : {},
    withCredentials: true,
  });
};

// Кроссовки
export const fetchSneakers = async () => {
  try {
    const response = await axios.get(`${API_URL}sneakers/`);
    console.log('API Response data:', response.data);

    // Проверяем формат ответа и извлекаем массив кроссовок
    if (response.data && Array.isArray(response.data)) {
      console.log('Direct array response:', response.data);
      return response.data; // Если сервер вернул массив напрямую
    } else if (response.data && Array.isArray(response.data.results)) {
      console.log('Paginated response:', response.data.results);
      return response.data.results; // Если сервер вернул пагинированный ответ
    } else {
      console.error('Unexpected data format:', response.data);
      return []; // Возвращаем пустой массив в случае неожиданного формата
    }
  } catch (error) {
    console.error('Error fetching sneakers:', error);
    return []; // Возвращаем пустой массив в случае ошибки
  }
};

export const fetchSneakerById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}sneakers/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching sneaker with id ${id}:`, error);
    throw error;
  }
};

// Корзина
export const fetchCart = async () => {
  try {
    // Если пользователь авторизован, используем /api/cart/, иначе /api/anonymous/cart/
    const endpoint = getAuthToken() ? 'cart/' : 'anonymous/cart/';
    const authInstance = createAuthInstance();
    const response = await authInstance.get(`${API_URL}${endpoint}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching cart:', error);
    throw error;
  }
};

export const addItemToCart = async (sneakerId, quantity = 1) => {
  try {
    const endpoint = getAuthToken() ? 'cart/add/' : 'anonymous/cart/add/';
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}${endpoint}`, {
      sneaker: sneakerId,
      quantity
    });
    return response.data;
  } catch (error) {
    console.error('Error adding item to cart:', error);
    throw error;
  }
};

export const updateCartItem = async (sneakerId, quantity) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}cart/update/`, {
      sneaker_id: sneakerId,
      quantity
    });
    return response.data;
  } catch (error) {
    console.error('Error updating cart item:', error);
    throw error;
  }
};

export const removeItemFromCart = async (sneakerId) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}cart/remove/`, {
      sneaker_id: sneakerId
    });
    return response.data;
  } catch (error) {
    console.error('Error removing item from cart:', error);
    throw error;
  }
};

export const clearCart = async () => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}cart/clear/`);
    return response.data;
  } catch (error) {
    console.error('Error clearing cart:', error);
    throw error;
  }
};

// Избранное
export const fetchFavorites = async () => {
  try {
    const endpoint = getAuthToken() ? 'favorites/' : 'anonymous/favorites/';
    const authInstance = createAuthInstance();
    const response = await authInstance.get(`${API_URL}${endpoint}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching favorites:', error);
    throw error;
  }
};

export const addToFavorites = async (sneakerId) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}favorites/add/`, {
      sneaker: sneakerId
    });
    return response.data;
  } catch (error) {
    console.error('Error adding to favorites:', error);
    throw error;
  }
};

export const removeFromFavorites = async (sneakerId) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}favorites/remove/`, {
      sneaker_id: sneakerId
    });
    return response.data;
  } catch (error) {
    console.error('Error removing from favorites:', error);
    throw error;
  }
};

export const checkIsFavorite = async (sneakerId) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.get(`${API_URL}favorites/check/?sneaker_id=${sneakerId}`);
    return response.data.is_favorite;
  } catch (error) {
    console.error('Error checking if item is favorite:', error);
    return false;
  }
};

// Заказы
export const fetchOrders = async () => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.get(`${API_URL}orders/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
};

export const createOrder = async (orderData) => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.post(`${API_URL}orders/`, orderData);
    return response.data;
  } catch (error) {
    console.error('Error creating order:', error);
    throw error;
  }
};

// Аутентификация пользователя
export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}auth/token/login/`, {
      username,
      password
    });
    const { auth_token } = response.data;
    
    // Сохраняем токен в localStorage
    localStorage.setItem('authToken', auth_token);
    
    return true;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const logout = async () => {
  try {
    const authInstance = createAuthInstance();
    await authInstance.post(`${API_URL}auth/token/logout/`);
    
    // Удаляем токен из localStorage
    localStorage.removeItem('authToken');
    
    return true;
  } catch (error) {
    console.error('Logout error:', error);
    // Даже при ошибке удаляем токен
    localStorage.removeItem('authToken');
    throw error;
  }
};

export const register = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}auth/users/`, userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const fetchUserProfile = async () => {
  try {
    const authInstance = createAuthInstance();
    const response = await authInstance.get(`${API_URL}auth/users/me/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};
