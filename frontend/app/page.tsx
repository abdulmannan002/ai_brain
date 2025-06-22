'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import Link from 'next/link';
import { useState } from 'react';

export default function HomePage() {
  const { user, isLoading } = useUser();
  const [isRecording, setIsRecording] = useState(false);

  const handleVoiceInput = async () => {
    if (!isRecording) {
      setIsRecording(true);
      // Voice recording logic would go here
      setTimeout(() => setIsRecording(false), 3000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">AI Brain Vault</h1>
            </div>
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <Link href="/dashboard" className="text-gray-700 hover:text-gray-900">
                    Dashboard
                  </Link>
                  <Link href="/ideas" className="text-gray-700 hover:text-gray-900">
                    Ideas
                  </Link>
                  <Link href="/transform" className="text-gray-700 hover:text-gray-900">
                    Transform
                  </Link>
                  <Link href="/api/auth/logout" className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
                    Logout
                  </Link>
                </>
              ) : (
                <Link href="/api/auth/login" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  Login
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl font-bold sm:text-6xl mb-6">
              Your Second Brain for Ideas
            </h1>
            <p className="text-xl mb-8 max-w-3xl mx-auto">
              Capture, organize, and transform your ideas into actionable content, intellectual property, and tasks using AI.
            </p>
            {user ? (
              <div className="space-y-4">
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={handleVoiceInput}
                    className={`px-6 py-3 rounded-lg font-medium ${
                      isRecording 
                        ? 'bg-red-600 hover:bg-red-700' 
                        : 'bg-white text-blue-600 hover:bg-gray-100'
                    }`}
                  >
                    {isRecording ? 'Recording...' : '🎤 Voice Input'}
                  </button>
                  <Link href="/ideas" className="px-6 py-3 bg-white text-blue-600 rounded-lg font-medium hover:bg-gray-100">
                    ✍️ Text Input
                  </Link>
                </div>
                <p className="text-sm opacity-90">Welcome back, {user.name || user.email}!</p>
              </div>
            ) : (
              <Link href="/api/auth/login" className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100">
                Get Started Free
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Transform Ideas Into Value
            </h2>
            <p className="text-xl text-gray-600">
              Our AI-powered platform helps you never lose another great idea
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart Capture</h3>
              <p className="text-gray-600">
                Capture ideas from text, voice, tweets, and emails. Our AI automatically organizes them by project, theme, and emotion.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🧠</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Organization</h3>
              <p className="text-gray-600">
                NLP-powered sorting and clustering helps you find patterns and connections across your ideas.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Instant Transformation</h3>
              <p className="text-gray-600">
                Transform ideas into blog posts, patent summaries, or actionable tasks with one click.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Simple Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Start free, upgrade when you need more
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-sm border">
              <h3 className="text-2xl font-bold mb-4">Free</h3>
              <p className="text-4xl font-bold mb-6">$0<span className="text-lg text-gray-600">/month</span></p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  50 ideas per month
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Basic sorting
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Text input only
                </li>
              </ul>
              <Link href="/api/auth/login" className="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700 text-center block">
                Get Started
              </Link>
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-lg border-2 border-blue-500">
              <h3 className="text-2xl font-bold mb-4">Premium</h3>
              <p className="text-4xl font-bold mb-6">$15<span className="text-lg text-gray-600">/month</span></p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Unlimited ideas
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Voice input
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Team collaboration
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Advanced AI features
                </li>
              </ul>
              <Link href="/api/auth/login" className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 text-center block">
                Start Premium
              </Link>
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-sm border">
              <h3 className="text-2xl font-bold mb-4">Enterprise</h3>
              <p className="text-4xl font-bold mb-6">$100<span className="text-lg text-gray-600">/month</span></p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Everything in Premium
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Custom integrations
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Priority support
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  API access
                </li>
              </ul>
              <Link href="/api/auth/login" className="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700 text-center block">
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 