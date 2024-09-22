import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [calcData, setCalcData] = useState(null); // State for Tile 2

    // Fetch data for Tile 1
    useEffect(() => {
        fetch('/api/views')
            .then(response => response.json())
            .then(data => {
                setViewsData(data);
                window.DD_LOGS?.logger.info('Fetched data for views', { id: data.id, text: data.text });
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    // Fetch data for Tile 2
    useEffect(() => {
        fetch('/api/uid') // Use the correct endpoint for calculations
            .then(response => response.json())
            .then(data => {
                setCalcData(data); // Assuming the response is an array of UIDs
                window.DD_LOGS?.logger.info('Fetched data for UIDs', { uids: data.uids });
            })
            .catch(error => console.error('Error fetching UID data:', error));
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...' },
        { id: 2, text: calcData ? `UIDs: ${calcData.uids.join(', ')}` : 'Fetching UIDs...' }, // Update Tile 2
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