import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null); // State for UID data

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

    // Record a visit and generate a new UID
    useEffect(() => {
        fetch('/api/uid', { method: 'POST' }) // Correct endpoint to record a visit
            .then(response => response.json())
            .then(data => {
                console.log('Visit recorded:', data.uid);
            })
            .catch(error => console.error('Error recording visit:', error));
    }, []);

    // Fetch UID data
    useEffect(() => {
        fetch('/api/uid/fetch') // Correct endpoint to fetch UIDs
            .then(response => response.json())
            .then(data => {
                setUidData(data); // Assuming the response is an array of UIDs
                window.DD_LOGS?.logger.info('Fetched data for UIDs', { uids: data.uids });
            })
            .catch(error => console.error('Error fetching UID data:', error));
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...' },
        { id: 2, text: uidData ? `UIDs: ${uidData.uids.join(', ')}` : 'Fetching UIDs...' },
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