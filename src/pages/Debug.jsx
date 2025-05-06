import React, { useState, useEffect } from 'react';
import { fetchSneakers } from '../services/api';
import axios from 'axios';

function Debug() {
  const [sneakers, setSneakers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [directImageTest, setDirectImageTest] = useState([]);
  const [corsStatus, setCorsStatus] = useState('Не проверено');
  const [apiUrl] = useState('http://localhost:8000/api/sneakers/');
  const [backendStatus, setBackendStatus] = useState('Проверка...');

  useEffect(() => {
    async function checkBackendStatus() {
      try {
        const response = await axios.get('http://localhost:8000/api/');
        setBackendStatus(`Доступен: ${response.status}`);
      } catch (err) {
        setBackendStatus(`Недоступен: ${err.message}`);
      }
    }
    
    checkBackendStatus();
  }, []);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await fetchSneakers();
        setSneakers(data);
        
        // Пробуем прямой запрос для отладки
        const response = await axios.get(apiUrl);
        console.log('Direct API response:', response.data);
        
        // Проверяем CORS-заголовки
        const corsResponse = await axios.head(apiUrl);
        console.log('CORS Headers:', corsResponse.headers);
        
        if (corsResponse.headers['access-control-allow-origin']) {
          setCorsStatus(`OK: ${corsResponse.headers['access-control-allow-origin']}`);
        } else {
          setCorsStatus('Отсутствуют CORS-заголовки');
        }
        
        if (response.data && response.data.results) {
          const testItems = response.data.results.map(item => ({
            id: item.id,
            title: item.title,
            imageUrl: item.image_url
          }));
          setDirectImageTest(testItems);
        }
      } catch (err) {
        console.error('Debug page error:', err);
        setError(err.message || 'Ошибка при загрузке данных');
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, [apiUrl]);

  // Тестирование прямого доступа к изображениям
  const testDirectImage = async (url) => {
    try {
      const response = await axios.get(url, { responseType: 'blob' });
      console.log('Image direct access response:', response);
      return 'Доступно';
    } catch (err) {
      console.error('Image direct access error:', err);
      return 'Недоступно: ' + err.message;
    }
  };

  return (
    <div className="content p-40">
      <h1>Диагностика проблем с изображениями</h1>
      
      <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f5f5f5' }}>
        <h2>Статус сервисов</h2>
        <p><strong>Бэкенд Django:</strong> {backendStatus}</p>
        <p><strong>CORS-заголовки:</strong> {corsStatus}</p>
      </div>
      
      {loading ? (
        <p>Загрузка данных...</p>
      ) : error ? (
        <p style={{ color: 'red' }}>Ошибка: {error}</p>
      ) : (
        <div>
          <h2>Данные из API ({sneakers.length} элементов)</h2>
          <table border="1" style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Название</th>
                <th>URL изображения</th>
                <th>Тест изображения</th>
              </tr>
            </thead>
            <tbody>
              {sneakers.map(item => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.title}</td>
                  <td>
                    <div>
                      <a href={item.image_url} target="_blank" rel="noopener noreferrer">
                        {item.image_url}
                      </a>
                    </div>
                    {/* Проверяем все возможные ключи для URL изображения */}
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                      <div>imageUrl: {item.imageUrl}</div>
                      <div>image_url: {item.image_url}</div>
                      <div>image: {item.image}</div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <img 
                        src={item.image_url} 
                        alt={item.title} 
                        style={{ maxWidth: '100px', maxHeight: '100px' }} 
                      />
                    </div>
                    <button onClick={async () => {
                      const result = await testDirectImage(item.image_url);
                      alert(`Результат проверки изображения: ${result}`);
                    }}>
                      Проверить доступность
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>Тестовые URL изображений</h2>
          <div>
            {directImageTest.map((item, index) => (
              <div key={index} style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
                <h3>{item.title}</h3>
                <p>URL: {item.imageUrl}</p>
                <img 
                  src={item.imageUrl} 
                  alt={item.title} 
                  style={{ maxWidth: '200px', display: 'block', marginBottom: '10px' }} 
                />
                <div>
                  <button onClick={() => {
                    const img = new Image();
                    img.onload = () => alert('Изображение загружено успешно');
                    img.onerror = () => alert('Ошибка загрузки изображения');
                    img.src = item.imageUrl;
                  }}>
                    Проверить загрузку
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Debug; 