import { useState } from 'react';

interface SearchBarProps {
    onSearch: (query: string) => Promise<LambdaResponse | void>;
    // You might pass in an isLoading state or error state if you want to show feedback
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchQuery(e.target.value);
    };

    const handleSearch = async () => {
        setError(null);
        if (searchQuery.trim() === '') {
            console.warn('Search query is empty.');
            return;
        }

        setIsLoading(true);
        try {
            const results = await onSearch(searchQuery);
            // Here you would typically update a parent component's state
            // with the results to display them.
        } catch (err) {
            console.error('Error during search:', err);
            setError('Failed to perform search. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div>
            <h1>Search for Products</h1>
            <input id="productSearch"
                type="search"
                className="w-150 p-1 text-black bg-[white] border-black border rounded-md"
                placeholder="Search for products..."
                value={searchQuery}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                onChange={handleInputChange}
            />
            {error && <p className="text-red-500">{error}</p>}
        </div>
    )
}

export default SearchBar;