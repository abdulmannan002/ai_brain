'use client';

import { useState } from 'react';

export default function IdeasPage() {
  const [content, setContent] = useState('');

  const submitIdea = async () => {
    const response = await fetch('/api/ideas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content, source: 'web-form' }),
    });
    if (response.ok) {
        const data = await response.json();
        alert(`Idea submitted with ID: ${data.id}`);
        setContent('');
    } else {
        alert('Failed to submit idea.');
    }
  };

  return (
    <div>
      <h1>Submit an Idea</h1>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="What's on your mind?"
        rows={5}
        style={{ width: '100%', padding: '10px' }}
      />
      <br />
      <button onClick={submitIdea} style={{ marginTop: '10px' }}>Submit Idea</button>
    </div>
  );
} 