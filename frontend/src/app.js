import React from 'react';
import './App.css'; // Importing the CSS for styling

function App() {
    const tilesData = [
        { id: 1, text: 'Tile 1: Dummy Data' },
        { id: 2, text: 'Tile 2: Dummy Data' },
        { id: 3, text: 'Tile 3: Dummy Data' },
        { id: 4, text: 'Tile 4: Dummy Data' },
    ];

    return (
        <div className="App">
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