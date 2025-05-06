import React, { useEffect } from "react";
import styles from "./Card.module.scss"
import ContentLoader from "react-content-loader"
import AppContext from '../../context';


function Card({
  id,
  price,
  title,
  imageUrl,
  image_url,
  onFavorite,
  onClickAdd,
  loading = false,
  favorited = false,
  ...props
}) {

  // Проверяем наличие значений и устанавливаем дефолтные, если нужно
  const safeId = id || '';
  const safeTitle = title || 'Название кроссовок';
  const safePrice = price || 0;
  
  // Проверяем разные варианты имен поля с URL изображения
  const safeImageUrl = imageUrl || image_url || props.image || 'img/placeholder.png';
  
  useEffect(() => {
    // Логирование props только один раз при монтировании
    if (!loading) {
      console.log('Card FULL props:', props);
      console.log('Card props:', { id, price, title, imageUrl, image_url });
      console.log('Using image URL:', safeImageUrl);
      
      // Выводим все ключи объекта для отладки
      const allProps = { id, price, title, imageUrl, image_url, ...props };
      console.log('All prop keys:', Object.keys(allProps));
      
      // Проверяем, есть ли в props другие поля, которые могут содержать URL изображения
      const possibleImageFields = ['imageUrl', 'image_url', 'image', 'img', 'thumbnail', 'photo'];
      possibleImageFields.forEach(field => {
        if (allProps[field]) {
          console.log(`Found image field '${field}':`, allProps[field]);
        }
      });
    }
  }, [id, price, title, imageUrl, image_url, loading, safeImageUrl, props]);

  // const [isAdded, setIsAdded] = useState(added);
  const [isFavorite, setisFavorite] = React.useState(favorited);
  const { isItemAdded } = React.useContext(AppContext);
  const obj = { id: safeId, parentId: safeId, title: safeTitle, imageUrl: safeImageUrl, price: safePrice };

  const onClickPlus = () => {
    if (onClickAdd) {
      onClickAdd(obj);
    }
    // setIsAdded(!isAdded);
  }


  const onClickFavorite = () => {
    if (onFavorite) {
      onFavorite(obj);
      setisFavorite(!isFavorite);
    }
  }
  // useEffect(() => {
  //   console.log('Переменная  изменилась')
  // }, [isAdded]);

  return (
    <div className={styles.card}>
      {loading ? (
        <ContentLoader
          speed={2}
          width={180}
          height={240}
          viewBox="0 0 150 270"
          backgroundColor="#f3f3f3"
        // foregroundColor="#ecebeb"
        >
          <rect x="96" y="94" rx="0" ry="0" width="2" height="2" />
          <rect x="23" y="138" rx="0" ry="0" width="108" height="31" />
          <rect x="0" y="14" rx="10" ry="10" width="150" height="155" />
          <rect x="0" y="181" rx="6" ry="6" width="150" height="15" />
          <rect x="0" y="202" rx="6" ry="6" width="100" height="15" />
          <rect x="0" y="234" rx="6" ry="6" width="80" height="35" />
          <rect x="118" y="237" rx="6" ry="6" width="32" height="32" />
        </ContentLoader>
      ) : (
        <>
         {onFavorite && (
             <div className={styles.favorite} onClick={onClickFavorite}>
            <img src={isFavorite ? 'img/heart-liked.svg' : 'img/heart-unliked.svg'} alt='Unliked' />
          </div>
          )}
        
          <img width="100%" height={160} src={safeImageUrl} alt='Sneakers' 
            onError={(e) => {
              console.error('Image loading error:', e);
              e.target.src = 'img/placeholder.png';
            }}
          />
          <h5>{safeTitle}</h5>
          <div className='d-flex justify-between align-center'>
            <div className='d-flex flex-column'>
              <span>Цена:</span>
              <b>{safePrice} руб.</b>
            </div>
            {onClickAdd && (
            <img
              className={styles.plus}
        
              src={isItemAdded && safeId && isItemAdded(safeId) ? 'img/btn-checked.svg' : 'img/btn-plus.svg'}
              alt='Plus'
              onClick={onClickPlus}
              />
            )}
         
          </div>
        </>)
      }
    </div>
  )
}

export default Card;