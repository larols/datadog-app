import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null);
    const [activeTab, setActiveTab] = useState('home'); // Track the active tab

    useEffect(() => {
        fetch('/api/views')
            .then(response => response.json())
            .then(data => {
                setViewsData(data);
                window.DD_LOGS?.logger.info('Fetched data for views', { id: data.id, text: data.text });
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    useEffect(() => {
        fetch('/api/uid', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Visit recorded:', data.uid);
            })
            .catch(error => console.error('Error recording visit:', error));
    }, []);

    useEffect(() => {
        fetch('/api/uid/latest')
            .then(response => response.json())
            .then(data => {
                if (data.uid) {
                    setUidData(data);
                    window.DD_LOGS?.logger.info('Fetched latest UID', { uid: data.uid, visit_time: data.visit_time });
                } else {
                    console.error('No UID found');
                }
            })
            .catch(error => console.error('Error fetching latest UID data:', error));
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...' },
        { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...' },
    ];

    const renderContent = () => {
        if (activeTab === 'home') {
            return (
                <div className="tiles-container">
                    {tilesData.map(tile => (
                        <div key={tile.id} className="tile">
                            {tile.text}
                        </div>
                    ))}
                </div>
            );
        } else if (activeTab === 'about') {
            return <div className="about">This application tracks user visits and displays the latest UID.</div>;
        }
    };

    return (
        <div className="App">
            <h1>datadog-app</h1>
            <nav className="navbar">
                <button onClick={() => setActiveTab('home')}>Home</button>
                <button onClick={() => setActiveTab('about')}>About</button>
            </nav>
            {renderContent()}
        </div>
    );
}

export default App;