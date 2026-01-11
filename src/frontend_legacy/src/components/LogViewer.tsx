import { useEffect, useRef, useState } from 'react';

interface LogViewerProps {
    logs: string[];
}

export const LogViewer = ({ logs }: LogViewerProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const bottomRef = useRef<HTMLDivElement>(null);
    const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

    // Handle scroll events to detect if user is at the bottom
    const handleScroll = () => {
        if (containerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
            // Check if user is near the bottom (within 50px)
            const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
            setShouldAutoScroll(isAtBottom);
        }
    };

    // Auto-scroll logic
    useEffect(() => {
        if (shouldAutoScroll && containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [logs, shouldAutoScroll]);

    return (
        <div
            ref={containerRef}
            onScroll={handleScroll}
            style={{
                marginTop: '1rem',
                padding: '0.8rem',
                backgroundColor: '#000',
                border: '1px solid #333',
                borderRadius: '4px',
                height: '150px',
                overflowY: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                color: '#00ff00',
                whiteSpace: 'pre-wrap'
            }}
        >
            {logs.length === 0 && <div style={{ color: '#666' }}>等待日誌 (Waiting for logs)...</div>}
            {logs.map((log, i) => (
                <div key={i}>{log}</div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
};
