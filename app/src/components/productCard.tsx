import "./productCard.css";

const ProductCard: React.FC<ProductInfo> = ({ name, brand, price, imageUrl, storeId }) => {
    return (
        <div className="product-card">
            {imageUrl && <img src={imageUrl} alt={name} className="product-image" />}
            <h3>{name}</h3>
            <span>Brand: {brand}</span>
            <span>Price: ${price.toFixed(2)}</span>
            {storeId && <p>Store: {imageUrl}</p>}
            <button className="add-button">View Details</button>
        </div>
    )
}

export default ProductCard;