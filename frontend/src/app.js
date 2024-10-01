import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null);
    const [externalData1, setExternalData1] = useState(null);  // State for the first external API data
    const [externalData2, setExternalData2] = useState(null);  // State for the second external API data
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

    // Function to fetch data from the first external API
    const fetchExternalData1 = () => {
        fetch('/api/external')
            .then(response => response.json())
            .then(data => {
                setExternalData1(data.data); // Set data for the first external API
                window.DD_LOGS?.logger.info('Fetched data from external API 1', data);
            })
            .catch(error => console.error('Error fetching external API data 1:', error));
    };

    // Function to fetch data from the second external API
    const fetchExternalData2 = () => {
        fetch('/api/external2')
            .then(response => response.json())
            .then(data => {
                setExternalData2(data.data); // Set data for the second external API
                window.DD_LOGS?.logger.info('Fetched data from external API 2', data);
            })
            .catch(error => console.error('Error fetching external API data 2:', error));
    };

    // Fetch data on component mount
    useEffect(() => {
        fetchViewsData();
        fetchUidData();
        fetchExternalData1(); // Fetch data from the first external API
        fetchExternalData2(); // Fetch data from the second external API
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

    // Function to reload UID data and generate a new UID
    const reloadUidData = () => {
        fetch('/api/uid', { method: 'POST' }) // Generate a new UID
            .then(response => response.json())
            .then(() => {
                fetchUidData(); // Fetch the latest UID after generating
            })
            .catch(error => console.error('Error generating new UID:', error));
    };

    // Function to update current time every second
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date().toLocaleTimeString());
        }, 1000);
        return () => clearInterval(timer); // Cleanup on component unmount
    }, []);

    // Updated tiles data including external API responses
    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...', tooltip: "This tile shows the number of visitors." },
        { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...', tooltip: "This tile shows the latest UID generated." },
        { id: 3, text: `Current Time: ${currentTime}` }, // Tile for current time
        { id: 4, text: externalData1 ? `External API 1 Data: ${externalData1.title}` : 'Fetching External Data 1...', tooltip: "This tile shows data fetched from the first external API." },
        { id: 5, text: externalData2 ? `External API 2 Data: ${externalData2.title}` : 'Fetching External Data 2...', tooltip: "This tile shows data fetched from the second external API." }
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
            return <div className="about">This application tracks user visits and displays the latest UID, current time, and data from two different external APIs.</div>;
        }
    };

    return (
        <div className="App">
            <h1>datadog-app</h1>
            <nav className="navbar">
                <button onClick={() => setActiveTab('home')}>Home</button>
                <button onClick={() => setActiveTab('about')}>About</button>
                <button onClick={reloadUidData}>Reload UID Data</button> {/* Reloads UID data */}
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
