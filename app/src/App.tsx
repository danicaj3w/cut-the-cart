// https://tailwindcss.com/docs/installation/using-vite
import './App.css'
import { useState } from 'react';
import axios from 'axios';
import SearchBar from "./components/searchBar"

interface LambdaPayload {
  query: string;
}

// Define the expected response structure from your Lambda
interface LambdaResponse {
  results: string[];
  message?: string;
}

function App() {
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [feedbackMessage, setFeedbackMessage] = useState<string>('');

  const callLambdaFunction = async (userQuery: string): Promise<LambdaResponse | void> => {
    const lambdaEndpoint = 'https://erafsmvwp4b63h7r3bcgvg4aru0wdfdx.lambda-url.us-west-1.on.aws/';

    try {
      const payload: LambdaPayload = { query : userQuery };
      const response = await axios.post<LambdaResponse>(lambdaEndpoint, payload, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      setSearchResults(response.data.results || []);
      setFeedbackMessage(response.data.message || '');

      return response.data;
    } catch (error: any) {
      console.error('Error invoking Lambda:', error);
      setSearchResults([]);
      setFeedbackMessage('Error fetching results.');
      // Handle different error types from Lambda/API Gateway if needed
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
        <div className="results-container">
          <h2>Search Results:</h2>
          <ul>
            {searchResults.map((result, index) => (
              <li key={index}>{result}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
