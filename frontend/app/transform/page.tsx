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

export default function TransformPage() {
  const { user, isLoading } = useUser();
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);
  const [outputType, setOutputType] = useState<'content' | 'ip' | 'tasks'>('content');
  const [isTransforming, setIsTransforming] = useState(false);
  const [transformedContent, setTransformedContent] = useState('');

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

  const transformIdea = async () => {
    if (!selectedIdea) return;
    
    setIsTransforming(true);
    try {
      const response = await fetch('/api/transform', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.accessToken}`,
        },
        body: JSON.stringify({
          idea_id: selectedIdea.id,
          output_type: outputType,
          user_id: user?.sub,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setTransformedContent(data.transformed_content);
        
        // Update the idea in the list
        setIdeas(ideas.map(idea => 
          idea.id === selectedIdea.id 
            ? { ...idea, transformed_output: data.transformed_content }
            : idea
        ));
        
        alert('Transformation completed successfully!');
      } else {
        alert('Failed to transform idea.');
      }
    } catch (error) {
      console.error('Error transforming idea:', error);
      alert('Error transforming idea.');
    } finally {
      setIsTransforming(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(transformedContent);
    alert('Copied to clipboard!');
  };

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
          <h1 className="text-2xl font-bold mb-4">Please log in to access transformations</h1>
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
              <Link href="/ideas" className="text-gray-700 hover:text-gray-900">Ideas</Link>
              <Link href="/transform" className="text-blue-600 font-medium">Transform</Link>
              <Link href="/api/auth/logout" className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
                Logout
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Transform Ideas</h1>
          <p className="text-gray-600">Convert your ideas into actionable content, intellectual property, or tasks</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Panel - Idea Selection */}
          <div className="space-y-6">
            {/* Output Type Selection */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">Choose Output Type</h2>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => setOutputType('content')}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    outputType === 'content'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">📝</div>
                  <div className="font-medium">Blog Post</div>
                  <div className="text-sm text-gray-600">Generate content</div>
                </button>
                
                <button
                  onClick={() => setOutputType('ip')}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    outputType === 'ip'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">💡</div>
                  <div className="font-medium">IP Summary</div>
                  <div className="text-sm text-gray-600">Patent-like outline</div>
                </button>
                
                <button
                  onClick={() => setOutputType('tasks')}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    outputType === 'tasks'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">✅</div>
                  <div className="font-medium">Tasks</div>
                  <div className="text-sm text-gray-600">Actionable items</div>
                </button>
              </div>
            </div>

            {/* Idea Selection */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">Select an Idea</h2>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {ideas.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No ideas found. Add some ideas first!</p>
                ) : (
                  ideas.map((idea) => (
                    <div
                      key={idea.id}
                      onClick={() => setSelectedIdea(idea)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                        selectedIdea?.id === idea.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <p className="text-gray-900 mb-2 line-clamp-2">{idea.content}</p>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>{new Date(idea.timestamp).toLocaleDateString()}</span>
                        <div className="flex space-x-2">
                          {idea.project && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                              {idea.project}
                            </span>
                          )}
                          {idea.emotion && (
                            <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                              {idea.emotion}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Transform Button */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <button
                onClick={transformIdea}
                disabled={!selectedIdea || isTransforming}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isTransforming ? 'Transforming...' : `Transform to ${outputType}`}
              </button>
            </div>
          </div>

          {/* Right Panel - Output */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Generated Output</h2>
              {transformedContent && (
                <button
                  onClick={copyToClipboard}
                  className="bg-gray-600 text-white px-4 py-2 rounded text-sm hover:bg-gray-700"
                >
                  Copy
                </button>
              )}
            </div>
            
            {!selectedIdea ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">🎯</div>
                <p className="text-gray-500">Select an idea to transform</p>
              </div>
            ) : !transformedContent ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">⚡</div>
                <p className="text-gray-500">Click transform to generate output</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Original Idea:</h3>
                  <p className="text-gray-700">{selectedIdea.content}</p>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Generated {outputType}:</h3>
                  <div className="whitespace-pre-wrap text-gray-700">{transformedContent}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Examples */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-4">Transformation Examples</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold mb-2">📝 Blog Post</h3>
              <p className="text-sm text-gray-600 mb-2">Transform ideas into engaging blog content with proper structure and SEO optimization.</p>
              <div className="text-xs text-gray-500">
                Example: "How AI is Revolutionizing Idea Management"
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold mb-2">💡 IP Summary</h3>
              <p className="text-sm text-gray-600 mb-2">Create patent-like summaries highlighting unique aspects and potential applications.</p>
              <div className="text-xs text-gray-500">
                Example: "Novel method for intelligent idea clustering using NLP"
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold mb-2">✅ Tasks</h3>
              <p className="text-sm text-gray-600 mb-2">Break down ideas into actionable tasks with priorities and deadlines.</p>
              <div className="text-xs text-gray-500">
                Example: "Research market size, create MVP, validate with users"
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}