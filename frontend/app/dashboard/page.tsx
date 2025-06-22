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

interface DashboardStats {
  totalIdeas: number;
  ideasThisMonth: number;
  projects: { [key: string]: number };
  themes: { [key: string]: number };
  emotions: { [key: string]: number };
  recentIdeas: Idea[];
}

export default function DashboardPage() {
  const { user, isLoading } = useUser();
  const [stats, setStats] = useState<DashboardStats>({
    totalIdeas: 0,
    ideasThisMonth: 0,
    projects: {},
    themes: {},
    emotions: {},
    recentIdeas: []
  });

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/ideas', {
        headers: {
          'Authorization': `Bearer ${user?.accessToken}`,
        },
      });
      
      if (response.ok) {
        const ideas: Idea[] = await response.json();
        
        // Calculate stats
        const now = new Date();
        const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        
        const projects: { [key: string]: number } = {};
        const themes: { [key: string]: number } = {};
        const emotions: { [key: string]: number } = {};
        
        let ideasThisMonth = 0;
        
        ideas.forEach(idea => {
          // Count by project
          if (idea.project) {
            projects[idea.project] = (projects[idea.project] || 0) + 1;
          }
          
          // Count by theme
          if (idea.theme) {
            themes[idea.theme] = (themes[idea.theme] || 0) + 1;
          }
          
          // Count by emotion
          if (idea.emotion) {
            emotions[idea.emotion] = (emotions[idea.emotion] || 0) + 1;
          }
          
          // Count this month's ideas
          const ideaDate = new Date(idea.timestamp);
          if (ideaDate >= thisMonth) {
            ideasThisMonth++;
          }
        });
        
        setStats({
          totalIdeas: ideas.length,
          ideasThisMonth,
          projects,
          themes,
          emotions,
          recentIdeas: ideas.slice(0, 5) // Get 5 most recent
        });
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
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
          <h1 className="text-2xl font-bold mb-4">Please log in to access your dashboard</h1>
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
              <Link href="/dashboard" className="text-blue-600 font-medium">Dashboard</Link>
              <Link href="/ideas" className="text-gray-700 hover:text-gray-900">Ideas</Link>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user.name || user.email}!</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="bg-blue-100 p-3 rounded-full">
                <span className="text-2xl">💡</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Ideas</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalIdeas}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="bg-green-100 p-3 rounded-full">
                <span className="text-2xl">📅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-gray-900">{stats.ideasThisMonth}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="bg-purple-100 p-3 rounded-full">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Projects</p>
                <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.projects).length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="bg-yellow-100 p-3 rounded-full">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Themes</p>
                <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.themes).length}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Ideas */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Recent Ideas</h2>
              <Link href="/ideas" className="text-blue-600 hover:text-blue-700 text-sm">
                View All →
              </Link>
            </div>
            <div className="space-y-4">
              {stats.recentIdeas.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No ideas yet. Start by adding your first idea!</p>
              ) : (
                stats.recentIdeas.map((idea) => (
                  <div key={idea.id} className="border-b border-gray-100 pb-4 last:border-b-0">
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

          {/* Analytics */}
          <div className="space-y-6">
            {/* Projects Breakdown */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">Projects</h2>
              {Object.keys(stats.projects).length === 0 ? (
                <p className="text-gray-500 text-center py-4">No projects yet</p>
              ) : (
                <div className="space-y-3">
                  {Object.entries(stats.projects).map(([project, count]) => (
                    <div key={project} className="flex justify-between items-center">
                      <span className="text-gray-700">{project}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                        {count}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Emotions Breakdown */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">Emotions</h2>
              {Object.keys(stats.emotions).length === 0 ? (
                <p className="text-gray-500 text-center py-4">No emotions analyzed yet</p>
              ) : (
                <div className="space-y-3">
                  {Object.entries(stats.emotions).map(([emotion, count]) => (
                    <div key={emotion} className="flex justify-between items-center">
                      <span className="text-gray-700 capitalize">{emotion}</span>
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm font-medium">
                        {count}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link href="/ideas" className="bg-blue-600 text-white p-4 rounded-lg text-center hover:bg-blue-700 transition-colors">
              <div className="text-2xl mb-2">✍️</div>
              <div className="font-medium">Add New Idea</div>
            </Link>
            <Link href="/transform" className="bg-green-600 text-white p-4 rounded-lg text-center hover:bg-green-700 transition-colors">
              <div className="text-2xl mb-2">⚡</div>
              <div className="font-medium">Transform Ideas</div>
            </Link>
            <Link href="/ideas" className="bg-purple-600 text-white p-4 rounded-lg text-center hover:bg-purple-700 transition-colors">
              <div className="text-2xl mb-2">🔍</div>
              <div className="font-medium">Search Ideas</div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 