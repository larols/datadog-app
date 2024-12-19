import React, { useEffect, useState } from 'react';
import './app.css';

function App() {
    const [viewsData, setViewsData] = useState(null);
    const [uidData, setUidData] = useState(null);
    const [externalData1, setExternalData1] = useState(null);
    const [bitcoinPriceEUR, setBitcoinPriceEUR] = useState(null);
    const [quoteData, setQuoteData] = useState(null);
    const [activeTab, setActiveTab] = useState('home');
    const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
    const [modalContent, setModalContent] = useState(null);
    const [userInput, setUserInput] = useState('');
    const [urlInput, setUrlInput] = useState('');
    const [ssrfResponse, setSsrfResponse] = useState(null);
    const [authenticated, setAuthenticated] = useState(false);

    const USERNAME = 'lars';
    const PASSWORD = 'secret';
    const validAuthHeader = btoa(`${USERNAME}:${PASSWORD}`);

    // Detect if the browser is Firefox
    const isFirefox = typeof navigator !== 'undefined' && navigator.userAgent.includes('Firefox');

    const fetchViewsData = () => {
        fetch('/api/views')
            .then(response => response.json())
            .then(data => {
                setViewsData(data);
                window.DD_LOGS?.logger.info('Fetched data for views', { id: data.id, text: data.text });
            })
            .catch(error => console.error('Error fetching views data:', error));
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
            .catch(error => console.error('Error fetching UID data:', error));
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

    const fetchQuoteData = () => {
        fetch('/api/quotes/random')
            .then(response => response.json())
            .then(data => {
                if (data.quote) {
                    setQuoteData(data);
                    window.DD_LOGS?.logger.info('Fetched random quote', { quote: data.quote, author: data.author });
                } else {
                    console.error('No quote found');
                }
            })
            .catch(error => console.error('Error fetching quote data:', error));
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

    const reloadUidData = () => {
        if (isFirefox) {
            fetch('/api/uid-invalid-url', { method: 'POST' })
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(() => fetchUidData())
                .catch(error => {
                    console.error('Forced fetch failure on Firefox:', error);
                    alert('Reload UID Data failed due to an unsupported operation in Firefox.');
                });
            return;
        }
        
        fetch('/api/uid', { method: 'POST' })
            .then(response => response.json())
            .then(() => fetchUidData())
            .catch(error => console.error('Error generating new UID:', error));
    };

    useEffect(() => {
        fetchViewsData();
        fetchUidData();
        fetchExternalData1();
        fetchBitcoinPriceEUR();
        fetchQuoteData();
    }, []);

    useEffect(() => {
        const intervalId = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000);
        return () => clearInterval(intervalId);
    }, []);

    const authenticateUser = () => {
        const username = prompt('Enter username:');
        const password = prompt('Enter password:');
        
        if (username === USERNAME && password === PASSWORD) {
            setAuthenticated(true);
        } else {
            alert('Authentication failed');
        }
    };

    const logoutUser = () => {
        setAuthenticated(false);
        setActiveTab('home'); // Redirect to home tab
    };  

    const renderContent = () => {
        if (activeTab === 'about') {
            return (
                <div className="about">
                    <h2>About This Application</h2>
                    <p>This app demonstrates modern monitoring, tracing, and logging concepts using Datadog.</p>
                    <p>It showcases real-time data from multiple backends and includes SSRF, XSS, and deserialization vulnerability testing as part of security research.</p>
                    <h3>SSRF Testing</h3>
                    <p>To test SSRF, enter a URL (like <code>https://jsonplaceholder.typicode.com/posts</code>) in the input field on the home page and submit it.</p>
                    <h3>XSS Testing</h3>
                    <p>To test XSS, you can input code like <code>&lt;script&gt;alert("XSS Test")&lt;/script&gt;</code> in the user input field to observe how it is handled.</p>
                </div>
            );
        }


        if (activeTab === 'admin') {
            if (!authenticated) {
                alert('Access Denied: You must log in to access this page.');
                return <p>Access denied. Please authenticate to view this page.</p>;
            }
        
            return (
                <div className="admin">
                    <h2>Admin Panel</h2>
                    <p>Welcome to the admin section. Here you can see and manage protected information.</p>
                    <ul>
                        <li>View sensitive logs</li>
                        <li>Access system settings</li>
                        <li>Manage application state</li>
                    </ul>
                </div>
            );
        }
        
        

        return (
            <div className="tiles-container">
                {tilesData.map(tile => (
                    <div 
                        key={tile.id} 
                        className="tile" 
                        onClick={() => setModalContent(tile.tooltip)}
                    >
                        {tile.text}
                    </div>
                ))}
                <input
                    type="text"
                    placeholder="Enter URL for SSRF test"
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
        );
    };

    const tilesData = [
        { id: 1, text: viewsData ? viewsData.text : 'Loading...', tooltip: "This tile shows the number of visitors." },
        { id: 2, text: uidData ? `Latest UID: ${uidData.uid}, Timestamp: ${uidData.visit_time}` : 'Fetching UID...', tooltip: "This tile shows the latest UID generated." },
        { id: 3, text: `Current Time: ${currentTime}`, tooltip: "This tile shows the current time." },
        { id: 4, text: externalData1 ? `External API 1 Data: ${externalData1.title}` : 'Fetching External Data 1...', tooltip: "This tile shows data fetched from the first external API." },
        { id: 5, text: bitcoinPriceEUR ? `Bitcoin Price (EUR): ${bitcoinPriceEUR} €` : 'Fetching Bitcoin Price...', tooltip: "This tile shows the Bitcoin price in Euros." },
        { id: 6, text: quoteData ? `"${quoteData.quote}" - ${quoteData.author}` : 'Fetching Quote...', tooltip: "This tile displays a random motivational quote from the Quotes service." }
    ];

    return (
        <div className="App">
            <h1>datadog-app</h1>
            <nav className="navbar">
                <button onClick={() => setActiveTab('home')}>Home</button>
                <button onClick={() => setActiveTab('about')}>About</button>
                <button onClick={reloadUidData}>Reload UID Data</button>
                <button onClick={testDeserializeEndpoint}>Test Deserialization</button>
                {authenticated ? (
                    <>
                        <button onClick={() => setActiveTab('admin')}>Admin</button>
                        <button onClick={logoutUser}>Logout</button>
                    </>
                ) : (
                    <button onClick={authenticateUser}>Login</button>
                )}
            </nav>
            {renderContent()}
        </div>
    );
}

export default App;
