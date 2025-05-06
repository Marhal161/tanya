import React, { useEffect } from 'react';
import Card from '../components/Card'
import AppContext from '../context';


function Home({
  // items,
  searchValue,
  setSearchValue,
  onChangeSearchInput,
  // onAddToCart,
  // onAddToFavorite,
  isLoading }) {

  const { items, onAddToCart, onAddToFavorite } = React.useContext(AppContext)
  
  useEffect(() => {
    if (items && items.length > 0) {
      console.log('Home items array:', items);
      console.log('First item details:', items[0]);
    }
  }, [items]);

  const renderItems = () => {
    // Проверяем, является ли items массивом
    const itemsArray = Array.isArray(items) ? items : [];

    // Фильтруем только если есть что фильтровать
    const filtredItems = searchValue 
      ? itemsArray.filter((item) => item.title.toLowerCase().includes(searchValue.toLowerCase()))
      : itemsArray;
      
    console.log('Rendering items count:', filtredItems.length);
    
    if (filtredItems.length > 0) {
      console.log('Sample item for rendering:', filtredItems[0]);
    }

    return (isLoading ? [...Array(12)] : filtredItems)
      .map((item, idx) => (
        <Card
          key={idx}
          // title={item.title}
          // price={item.price}
          // imageUrl={item.imageUrl}
          onClickAdd={(obj) => onAddToCart(obj)}
          onFavorite={(obj) => onAddToFavorite(obj)}
          // added={isItemAdded(item && item.id)}
          {...item}
          // favorited
          loading={isLoading}
        />
      ))
  }

  return (
    <div className='content p-40 '>

      <div className='d-flex align-center justify-between mb-40'>
        <h1 >{searchValue ? `Поиск по запросу: "${searchValue}"` : 'Все кроссовки'}</h1>
        <div className='search-block d-flex align-center'>
          <img src='img/search.svg' alt='Search' onClick={() => setSearchValue('')} />
          <input onChange={onChangeSearchInput} value={searchValue} placeholder='Поиск...' />
        </div>
      </div>
      {/* {console.log(cartItems, items)} */}
      <div className='sneakers d-flex justify-center'>
        {renderItems()}
      </div>
    </div>
  )
}


export default Home;