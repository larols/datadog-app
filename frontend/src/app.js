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
        fetch('/api/uid/latest') // Update to the new endpoint
            .then(response => response.json())
            .then(data => {
                if (data.uid) {
                    setUidData(data); // Set the latest UID and timestamp
                    window.DD_LOGS?.logger.info('Fetched latest UID', { uid: data.uid, visit_time: data.visit_time });
                } else {
                    console.error('No UID found');
                }
            })
            .catch(error => console.error('Error fetching latest UID data:', error));
    }, []);

const uidLoading = !uidData;

const tilesData = [
    { id: 1, text: viewsData ? viewsData.text : 'Loading...' },
    { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...' },
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