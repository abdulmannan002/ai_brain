'use client';

import { useState, useEffect } from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';
import Link from 'next/link';

interface Idea {
  id: number;
  content: string;
  source: string;
  timestamp: string;
  project?: string;
  theme?: string;
  emotion?: string;
  transformed_output?: string;
}

export default function IdeasPage() {
  const { user, isLoading } = useUser();
  const [content, setContent] = useState('');
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterProject, setFilterProject] = useState('');
  const [filterTheme, setFilterTheme] = useState('');
  const [filterEmotion, setFilterEmotion] = useState('');

  useEffect(() => {
    if (user) {
      fetchIdeas();
    }
  }, [user]);

  const fetchIdeas = async () => {
    try {
      const response = await fetch('/api/ideas', {
        headers: {
          'Authorization': `Bearer ${user?.accessToken}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setIdeas(data);
      }
    } catch (error) {
      console.error('Error fetching ideas:', error);
    }
  };

  const submitIdea = async () => {
    if (!content.trim()) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/ideas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.accessToken}`,
        },
        body: JSON.stringify({ content, source: 'web-form' }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setIdeas([data, ...ideas]);
        setContent('');
        alert('Idea submitted successfully!');
      } else {
        alert('Failed to submit idea.');
      }
    } catch (error) {
      console.error('Error submitting idea:', error);
      alert('Error submitting idea.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVoiceInput = async () => {
    if (!isRecording) {
      setIsRecording(true);
      // In a real implementation, this would record audio and send to backend
      setTimeout(() => {
        setIsRecording(false);
        // Simulate voice input
        setContent('Voice input simulation: This is a test idea from voice recording.');
      }, 3000);
    }
  };

  const transformIdea = async (ideaId: number, outputType: string) => {
    try {
      const response = await fetch('/api/transform', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.accessToken}`,
        },
        body: JSON.stringify({
          idea_id: ideaId,
          output_type: outputType,
          user_id: user?.sub,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        // Update the idea with transformation
        setIdeas(ideas.map(idea => 
          idea.id === ideaId 
            ? { ...idea, transformed_output: data.transformed_content }
            : idea
        ));
        alert(`${outputType} generated successfully!`);
      } else {
        alert('Failed to transform idea.');
      }
    } catch (error) {
      console.error('Error transforming idea:', error);
      alert('Error transforming idea.');
    }
  };

  const searchIdeas = async () => {
    if (!searchQuery.trim()) {
      fetchIdeas();
      return;
    }
    
    try {
      const response = await fetch(`/api/ideas/search?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${user?.accessToken}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setIdeas(data);
      }
    } catch (error) {
      console.error('Error searching ideas:', error);
    }
  };

  const filteredIdeas = ideas.filter(idea => {
    if (filterProject && idea.project !== filterProject) return false;
    if (filterTheme && idea.theme !== filterTheme) return false;
    if (filterEmotion && idea.emotion !== filterEmotion) return false;
    return true;
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to access your ideas</h1>
          <Link href="/api/auth/login" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-bold text-gray-900">AI Brain Vault</Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-700 hover:text-gray-900">Dashboard</Link>
              <Link href="/ideas" className="text-blue-600 font-medium">Ideas</Link>
              <Link href="/transform" className="text-gray-700 hover:text-gray-900">Transform</Link>
              <Link href="/api/auth/logout" className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
                Logout
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Ideas</h1>
          <p className="text-gray-600">Capture and organize your thoughts</p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Add New Idea</h2>
          <div className="space-y-4">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What's on your mind? Share your idea..."
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div className="flex space-x-4">
              <button
                onClick={submitIdea}
                disabled={isSubmitting || !content.trim()}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Idea'}
              </button>
              <button
                onClick={handleVoiceInput}
                disabled={isRecording}
                className={`px-6 py-2 rounded-md font-medium ${
                  isRecording 
                    ? 'bg-red-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {isRecording ? 'Recording...' : '🎤 Voice Input'}
              </button>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Search & Filter</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <input
                type="text"
                placeholder="Search ideas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <select
                value={filterProject}
                onChange={(e) => setFilterProject(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">All Projects</option>
                <option value="Startup Ideas">Startup Ideas</option>
                <option value="Blog Content">Blog Content</option>
                <option value="Product Features">Product Features</option>
                <option value="Research Notes">Research Notes</option>
              </select>
            </div>
            <div>
              <select
                value={filterTheme}
                onChange={(e) => setFilterTheme(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">All Themes</option>
                <option value="tech">Tech</option>
                <option value="business">Business</option>
                <option value="creativity">Creativity</option>
                <option value="general">General</option>
              </select>
            </div>
            <div>
              <select
                value={filterEmotion}
                onChange={(e) => setFilterEmotion(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">All Emotions</option>
                <option value="excited">Excited</option>
                <option value="curious">Curious</option>
                <option value="neutral">Neutral</option>
                <option value="concerned">Concerned</option>
              </select>
            </div>
            <div>
              <button
                onClick={searchIdeas}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Search
              </button>
            </div>
          </div>
        </div>

        {/* Ideas List */}
        <div className="space-y-4">
          {filteredIdeas.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No ideas found. Start by adding your first idea!</p>
            </div>
          ) : (
            filteredIdeas.map((idea) => (
              <div key={idea.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <p className="text-gray-900 text-lg mb-2">{idea.content}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Source: {idea.source}</span>
                      <span>•</span>
                      <span>{new Date(idea.timestamp).toLocaleDateString()}</span>
                      {idea.project && (
                        <>
                          <span>•</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Project: {idea.project}</span>
                        </>
                      )}
                      {idea.theme && (
                        <>
                          <span>•</span>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Theme: {idea.theme}</span>
                        </>
                      )}
                      {idea.emotion && (
                        <>
                          <span>•</span>
                          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">Emotion: {idea.emotion}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => transformIdea(idea.id, 'content')}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      Blog Post
                    </button>
                    <button
                      onClick={() => transformIdea(idea.id, 'ip')}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      IP Summary
                    </button>
                    <button
                      onClick={() => transformIdea(idea.id, 'tasks')}
                      className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700"
                    >
                      Tasks
                    </button>
                  </div>
                </div>
                
                {idea.transformed_output && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-md">
                    <h4 className="font-semibold mb-2">Transformation:</h4>
                    <p className="text-gray-700">{idea.transformed_output}</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}