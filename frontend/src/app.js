import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null);
    const [activeTab, setActiveTab] = useState('home'); // Track the active tab
    const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString()); // State for current time
    const [modalContent, setModalContent] = useState(null); // State for modal content

    // Function to fetch views data
    const fetchViewsData = () => {
        fetch('/api/views')
            .then(response => response.json())
            .then(data => {
                setViewsData(data);
                window.DD_LOGS?.logger.info('Fetched data for views', { id: data.id, text: data.text });
            })
            .catch(error => console.error('Error fetching data:', error));
    };

    // Function to fetch UID data
    const fetchUidData = () => {
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
    };

    // Fetch data on component mount
    useEffect(() => {
        fetchViewsData();
        fetchUidData();
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

    // Function to reload UID data only
    const reloadUidData = () => {
        fetchUidData();
    };

    // Function to update current time every second
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date().toLocaleTimeString());
        }, 1000);
        return () => clearInterval(timer); // Cleanup on component unmount
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...', tooltip: "This tile shows the number of visitors." },
        { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...', tooltip: "This tile shows the latest UID generated." },
        { id: 3, text: `Current Time: ${currentTime}` }, // Tile for current time
    ];

    const renderContent = () => {
        if (activeTab === 'home') {
            return (
                <div className="tiles-container">
                    {tilesData.map(tile => (
                        <div 
                            key={tile.id} 
                            className="tile" 
                            onClick={() => setModalContent(tile.tooltip)} // Show tooltip on click
                        >
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
                <button onClick={reloadUidData}>Reload UID Data</button> {/* Reloads only UID data */}
            </nav>
            {renderContent()}
            {modalContent && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close" onClick={() => setModalContent(null)}>&times;</span>
                        <p>{modalContent}</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;