import React from "react";
import { Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import { fetchSneakers } from './services/api';

import AppContext from "./context";

import Header from "./components/Header";
import Drawer from "./components/Drawer";
import Favorites from "./pages/Favorites";
import Home from "./pages/Home";
import Orders from "./pages/Orders";
import Debug from "./pages/Debug";

function App() {

  const [cartOpened, setCartOpened] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [items, setItems] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [searchValue, setSearchValue] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);
        const sneakersData = await fetchSneakers();
        
        // Проверяем, что получили массив
        if (Array.isArray(sneakersData)) {
          setItems(sneakersData);
        } else {
          console.error('Received data is not an array:', sneakersData);
          setItems([]);
          setError('Ошибка загрузки данных: неверный формат');
        }
      } catch (error) {
        console.error('Failed to load sneakers:', error);
        setItems([]);
        setError('Ошибка загрузки данных: ' + (error.message || 'неизвестная ошибка'));
      } finally {
        setIsLoading(false);
      }
    }
    
    loadData();
  }, []);

  const onAddToCart = async (obj) => {
    // console.log(obj);
    try {
      const findItem = cartItems.find((item) => Number(item.parentId) === Number(obj.id));
      if (findItem) {
        setCartItems((prev) => prev.filter((item) => Number(item.id) !== Number(obj.id)));
        await axios.delete(`https://642c1eca208dfe2547288b56.mockapi.io/cart/${findItem.id}`);
      } else {
        axios.post('https://642c1eca208dfe2547288b56.mockapi.io/cart', obj);
        setCartItems((prev) => [...prev, obj]);
        // setCartItems([...cartItems, obj]);
      }
    } catch (error) {
      alert("ошибка при добавлении в корзину")
    }

  };

  const onRemoveItem = (id) => {
    axios.delete(`https://642c1eca208dfe2547288b56.mockapi.io/cart/${id}`);
    setCartItems(prev => prev.filter(item => Number(item.id) !== Number(id)))
    // console.log(id)
  }

  const onAddToFavorite = async (obj) => {
    try {
      if (favorites.find(favObj => Number(favObj.id) === Number(obj.id))) {
        axios.delete(`https://642c1eca208dfe2547288b56.mockapi.io/favorites/${obj.id}`);
        setFavorites(prev => prev.filter(item => Number(item.id) !== Number(obj.id)))
      } else {
        const { data } = await axios.post('https://642c1eca208dfe2547288b56.mockapi.io/favorites', obj);
        setFavorites(prev => [...prev, data]);
      }
    } catch (error) {
      alert('Не удалось добавить в избранное')
    }
  }

  const onChangeSearchInput = (event) => {
    setSearchValue(event.target.value);
  }

  const isItemAdded = (id) => {
    // Проверяем, что id существует и cartItems является массивом
    if (!id || !Array.isArray(cartItems)) {
      return false;
    }
    return cartItems.some((obj) => Number(obj.parentId) === Number(id));
  }

  return (
    <AppContext.Provider
      value={{ items, cartItems, favorites, isItemAdded, onAddToCart, onAddToFavorite, setCartOpened, setCartItems, error }}>
      <div className="wrapper clear">

        {/* {cartOpened ? <Drawer onClose={()=> setCartOpened(false)} /> : null}  */}

        {cartOpened && <Drawer
          onClose={() => setCartOpened(false)}
          items={cartItems}
          onRemove={onRemoveItem}
        />}

        <Header onClickCart={() => setCartOpened(true)} />

        {error && (
          <div style={{ color: 'red', textAlign: 'center', padding: '20px' }}>
            {error}
          </div>
        )}

        <Routes>
          <Route exact path={process.env.PUBLIC_URL + '/'}
            element={
              <Home
                searchValue={searchValue}
                setSearchValue={setSearchValue}
                onChangeSearchInput={onChangeSearchInput}
                isLoading={isLoading}
              />
            } />
          <Route exact path={process.env.PUBLIC_URL + '/Favorites'}
            element={
              <Favorites
              // items={favorites}
              // onAddToFavorite={onAddToFavorite}
              />
            } />
          <Route exact path={process.env.PUBLIC_URL + '/Orders'}
            element={
              <Orders
              // items={favorites}
              // onAddToFavorite={onAddToFavorite} 
              />
            } />
          <Route exact path={process.env.PUBLIC_URL + '/debug'}
            element={<Debug />} />
        </Routes>

      </div>
    </AppContext.Provider>

  )
}

export default App;
