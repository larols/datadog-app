import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './app';

test('renders the app title', () => {
    render(<App />);
    expect(screen.getByText(/datadog-app/i)).toBeInTheDocument();
});
