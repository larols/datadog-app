import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);

    useEffect(() => {
        fetch('/api/views')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setViewsData(data);
                if (window.DD_LOGS) {
                    try {
                        window.DD_LOGS.logger.info('Fetched data for views', { id: data.id, text: data.text });
                    } catch (logError) {
                        console.error('Logging error:', logError);
                    }
                } else {
                    console.warn('Datadog Logs SDK not initialized');
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...' },
        { id: 2, text: 'Tile 2: Dummy Data' },
        { id: 3, text: 'Tile 3: Dummy Data' },
        { id: 4, text: 'Tile 4: Dummy Data' },
    ];

    return (
        <div className="App">
            <h1>datadog-app</h1>
            <div className="tiles-container">
                {tilesData.map(tile => (
                    <div key={tile.id} className="tile">
                        {tile.text}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;