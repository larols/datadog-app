import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null);
    const [externalData1, setExternalData1] = useState(null);
    const [bitcoinPriceEUR, setBitcoinPriceEUR] = useState(null);
    const [activeTab, setActiveTab] = useState('home');
    const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
    const [modalContent, setModalContent] = useState(null);
    const [userInput, setUserInput] = useState('');
    const [urlInput, setUrlInput] = useState('');
    const [ssrfResponse, setSsrfResponse] = useState(null);

    // Detect if the browser is Firefox
    const isFirefox = typeof navigator !== 'undefined' && navigator.userAgent.includes('Firefox');

    const fetchViewsData = () => {
        fetch('/api/views')
            .then(response => response.json())
            .then(data => {
                setViewsData(data);
                window.DD_LOGS?.logger.info('Fetched data for views', { id: data.id, text: data.text });
            })
            .catch(error => console.error('Error fetching data:', error));
    };

    const testDeserializeEndpoint = () => {
        const payload = JSON.stringify({
            py: "O:system('echo Unsafe command executed')"
        });

        fetch('/api/deserialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: payload
        })
            .then(response => response.json())
            .then(data => console.log('Deserialization response:', data))
            .catch(error => console.error('Error testing deserialization:', error));
    };

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

    const fetchExternalData1 = () => {
        fetch('/api/external')
            .then(response => response.json())
            .then(data => {
                setExternalData1(data.data);
                window.DD_LOGS?.logger.info('Fetched data from external API 1', data);
            })
            .catch(error => console.error('Error fetching external API data 1:', error));
    };

    const fetchBitcoinPriceEUR = () => {
        fetch('/api/external2')
            .then(response => response.json())
            .then(data => {
                const eurRate = data.data.bpi.EUR.rate;
                setBitcoinPriceEUR(eurRate);
                window.DD_LOGS?.logger.info('Fetched Bitcoin price in EUR', { rate: eurRate });
            })
            .catch(error => console.error('Error fetching Bitcoin price in EUR:', error));
    };

    const testSsrEndpoint = () => {
        fetch('/api/uid/ssrf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput })
        })
        .then(response => response.json())
        .then(data => {
            setSsrfResponse(data.data);
            window.DD_LOGS?.logger.info('SSRF response received', data);
        })
        .catch(error => console.error('Error fetching SSRF:', error));
    };

    useEffect(() => {
        fetchViewsData();
        fetchUidData();
        fetchExternalData1();
        fetchBitcoinPriceEUR();
    }, []);

    useEffect(() => {
        fetch('/api/uid', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Visit recorded:', data.uid);
            })
            .catch(error => console.error('Error recording visit:', error));
    }, []);

    // Modified reloadUidData function to simulate failure on Firefox
    const reloadUidData = () => {
        if (isFirefox) {
            // Trigger a failure by using an invalid URL
            fetch('/api/uid-invalid-url', { method: 'POST' })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(() => {
                    fetchUidData();
                })
                .catch(error => {
                    console.error('Forced fetch failure on Firefox:', error);
                    alert('Reload UID Data failed due to an unsupported operation in Firefox.');
                });
            return;
        }
        
        fetch('/api/uid', { method: 'POST' })
            .then(response => response.json())
            .then(() => {
                fetchUidData();
            })
            .catch(error => console.error('Error generating new UID:', error));
    };

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date().toLocaleTimeString());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...', tooltip: "This tile shows the number of visitors." },
        { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...', tooltip: "This tile shows the latest UID generated." },
        { id: 3, text: `Current Time: ${currentTime}`, tooltip: "This tile shows the current time." },
        { id: 4, text: externalData1 ? `External API 1 Data: ${externalData1.title}` : 'Fetching External Data 1...', tooltip: "This tile shows data fetched from the first external API." },
        { id: 5, text: bitcoinPriceEUR ? `Bitcoin Price (EUR): ${bitcoinPriceEUR} €` : 'Fetching Bitcoin Price...', tooltip: "This tile shows the Bitcoin price in Euros." },
        { id: 6, text: `User Input: ${userInput}`, tooltip: "This tile displays user input and is vulnerable to XSS.", inputField: true }
    ];

    const renderContent = () => {
        if (activeTab === 'home') {
            return (
                <div className="tiles-container">
                    {tilesData.map(tile => (
                        <div 
                            key={tile.id} 
                            className="tile" 
                            onClick={() => setModalContent(tile.tooltip)}
                        >
                            {tile.inputField ? (
                                <div dangerouslySetInnerHTML={{ __html: userInput }} />
                            ) : (
                                tile.text
                            )}
                        </div>
                    ))}
                    <div>
                        <input
                            type="text"
                            placeholder="Enter URL for SSRF test or XSS"
                            value={urlInput}
                            onChange={e => setUrlInput(e.target.value)}
                        />
                        <button onClick={testSsrEndpoint}>Submit</button>
                        {ssrfResponse && (
                            <div>
                                <h3>SSRF Response:</h3>
                                <pre>{ssrfResponse}</pre>
                            </div>
                        )}
                    </div>
                </div>
            );
        } else if (activeTab === 'about') {
            return (
                <div className="about">
                    <p>This application tracks user visits and displays various data.</p>
                    <p>For testing purposes:</p>
                    <p>Use <code>https://jsonplaceholder.typicode.com/posts</code> for SSRF testing.</p>
                    <p>Use <code>&lt;script&gt;alert("XSS Test")&lt;/script&gt;</code> for XSS testing.</p>
                </div>
            );
        }
    };

    return (
        <div className="App">
            <h1>datadog-app</h1>
            <nav className="navbar">
                <button onClick={() => setActiveTab('home')}>Home</button>
                <button onClick={() => setActiveTab('about')}>About</button>
                <button onClick={reloadUidData}>Reload UID Data</button>
                <button onClick={testDeserializeEndpoint}>Test Deserialization</button>
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
