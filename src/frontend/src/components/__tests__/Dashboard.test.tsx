import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';

// 1. Mock the Child Component (ChatAssistant)
vi.mock('../ChatAssistant', () => ({
    default: () => <div data-testid="mock-chat">Chat Assistant</div>
}));

// 2. Mock Axios to prevent real network calls
vi.mock('axios');

describe('Clinical Dashboard', () => {

    // Clear mocks before each test
    beforeEach(() => {
        vi.resetAllMocks();
    });

    it('renders the main title correctly', async () => {
        // Setup Fake Response
        (axios.get as any).mockResolvedValue({
            data: { data: [] }
        });

        render(<Dashboard />);

        // Assert static text
        expect(screen.getByText(/BioStream Sentinel/i)).toBeInTheDocument();
        expect(screen.getByText(/Clinical Monitoring Dashboard/i)).toBeInTheDocument();

        // FIX: Wait for the axios call to resolve. 
        // This absorbs the "act" warning by ensuring the cycle is complete.
        await waitFor(() => {
            expect(axios.get).toHaveBeenCalledTimes(1);
        });
    });

    it('renders the KPI cards', async () => {
        // Setup Fake Response
        (axios.get as any).mockResolvedValue({
            data: { data: [] }
        });

        render(<Dashboard />);

        expect(screen.getByText(/System Status/i)).toBeInTheDocument();
        expect(screen.getByText(/Monitored Devices/i)).toBeInTheDocument();

        // FIX: Wait for the effect to finish here too
        await waitFor(() => {
            expect(axios.get).toHaveBeenCalledTimes(1);
        });
    });
});