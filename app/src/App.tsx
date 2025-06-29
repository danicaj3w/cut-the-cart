// https://tailwindcss.com/docs/installation/using-vite
import './App.css'
import { useState } from 'react';
import axios from 'axios';
import SearchBar from "./components/searchBar"
import ProductCard from "./components/productCard"

interface LambdaPayload {
  query: string;
}

function App() {
  const [searchResults, setSearchResults] = useState<ProductInfo[]>([]);
  const [feedbackMessage, setFeedbackMessage] = useState<string>('');

  const callLambdaFunction = async (userQuery: string): Promise<LambdaResponse | void> => {
    const lambdaEndpoint = 'https://erafsmvwp4b63h7r3bcgvg4aru0wdfdx.lambda-url.us-west-1.on.aws/';

    try {
      const payload: LambdaPayload = { query: userQuery };
      const response = await axios.post<LambdaResponse>(lambdaEndpoint, payload, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const products: ProductInfo[] = response.data.products.map((product: string) => {
        try {
          const parsedProduct = typeof product === 'string' ? JSON.parse(product) : product;

          const productObject: ProductInfo = {
            productId: parsedProduct.productId,
            name: parsedProduct.name,
            brand: parsedProduct.brand,
            price: Number(parsedProduct.price) || 0.00,
            imageUrl: parsedProduct.imageUrl ?? '',
            storeId: parsedProduct.storeId
          };

          return productObject;
        } catch (err) {
          return {
            productId: '0000000000000',
            name: 'No Product',
            brand: 'Unknown',
            price: 0.00,
            storeId: '00000000'
          };
        }
      });

      setSearchResults(products || []);
      setFeedbackMessage(response.data.message || '');

      return response.data;
    } catch (error: any) {
      console.error('Error invoking Lambda:', error);
      setSearchResults([]);
      setFeedbackMessage('Error fetching results.');
      throw new Error(error.response?.data?.message || 'Failed to connect to search service.');
    }
  }

  return (
    <div className="homepage">
      <h1>Cut the Cart</h1>
      <h2>Find cheaper prices!</h2>

      <SearchBar onSearch={callLambdaFunction} />

      {feedbackMessage && <p>{feedbackMessage}</p>}

      {searchResults.length > 0 && (
        <div className="product-grid">
          {searchResults.map((product, index) => (
            <ProductCard key={product.productId || index}
              productId={product.productId}
              name={product.name}
              brand={product.brand}
              price={product.price}
              imageUrl={product.imageUrl}
              storeId={product.storeId}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default App
