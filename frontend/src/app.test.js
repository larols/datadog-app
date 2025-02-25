import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './app';

test('renders app title', () => {
    render(<App />);
    const titleElement = screen.getByText(/datadog-app/i);
    expect(titleElement).toBeInTheDocument();
});

test('renders "Reload UID Data" button', () => {
    render(<App />);
    const buttonElement = screen.getByText(/Reload UID Data/i);
    expect(buttonElement).toBeInTheDocument();
});
