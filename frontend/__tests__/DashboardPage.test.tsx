import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../app/dashboard/page';

// Mock Auth0
jest.mock('@auth0/nextjs-auth0/client', () => ({
  useUser: () => ({
    user: { email: 'test@example.com', name: 'Test User', sub: 'test_user_123' },
    isLoading: false,
    accessToken: 'mock_token'
  })
}));

// Mock fetch
global.fetch = jest.fn();

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication', () => {
    it('should show login message when user is not authenticated', () => {
      jest.doMock('@auth0/nextjs-auth0/client', () => ({
        useUser: () => ({
          user: null,
          isLoading: false
        })
      }));

      render(<DashboardPage />);
      expect(screen.getByText('Please log in to access your dashboard')).toBeInTheDocument();
    });

    it('should show loading spinner when authentication is loading', () => {
      jest.doMock('@auth0/nextjs-auth0/client', () => ({
        useUser: () => ({
          user: null,
          isLoading: true
        })
      }));

      render(<DashboardPage />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('Dashboard Header', () => {
    it('should display welcome message', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Welcome back, Test User!')).toBeInTheDocument();
    });

    it('should show user email when name is not available', () => {
      jest.doMock('@auth0/nextjs-auth0/client', () => ({
        useUser: () => ({
          user: { email: 'test@example.com', sub: 'test_user_123' },
          isLoading: false,
          accessToken: 'mock_token'
        })
      }));

      render(<DashboardPage />);
      expect(screen.getByText('Welcome back, test@example.com!')).toBeInTheDocument();
    });
  });

  describe('Stats Cards', () => {
    const mockIdeas = [
      {
        id: 1,
        content: 'Test idea 1',
        source: 'web-form',
        timestamp: '2025-01-01T00:00:00Z',
        project: 'Startup Ideas',
        theme: 'tech',
        emotion: 'excited'
      },
      {
        id: 2,
        content: 'Test idea 2',
        source: 'voice',
        timestamp: '2025-01-15T00:00:00Z',
        project: 'Blog Content',
        theme: 'creativity',
        emotion: 'curious'
      },
      {
        id: 3,
        content: 'Test idea 3',
        source: 'web-form',
        timestamp: '2025-01-20T00:00:00Z',
        project: 'Product Features',
        theme: 'business',
        emotion: 'neutral'
      }
    ];

    it('should display stats cards with correct data', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Ideas')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument(); // Total ideas
        
        expect(screen.getByText('This Month')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // Ideas this month (Jan 2025)
        
        expect(screen.getByText('Projects')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument(); // Number of projects
        
        expect(screen.getByText('Themes')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument(); // Number of themes
      });
    });

    it('should display correct icons for stats cards', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('💡')).toBeInTheDocument(); // Total Ideas icon
        expect(screen.getByText('📅')).toBeInTheDocument(); // This Month icon
        expect(screen.getByText('📊')).toBeInTheDocument(); // Projects icon
        expect(screen.getByText('🎯')).toBeInTheDocument(); // Themes icon
      });
    });
  });

  describe('Recent Ideas Section', () => {
    const mockIdeas = [
      {
        id: 1,
        content: 'Latest idea',
        source: 'web-form',
        timestamp: '2025-01-20T00:00:00Z',
        project: 'Startup Ideas',
        theme: 'tech',
        emotion: 'excited'
      },
      {
        id: 2,
        content: 'Second latest idea',
        source: 'voice',
        timestamp: '2025-01-19T00:00:00Z',
        project: 'Blog Content',
        theme: 'creativity',
        emotion: 'curious'
      }
    ];

    it('should display recent ideas', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Recent Ideas')).toBeInTheDocument();
        expect(screen.getByText('Latest idea')).toBeInTheDocument();
        expect(screen.getByText('Second latest idea')).toBeInTheDocument();
      });
    });

    it('should show idea metadata', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('1/20/2025')).toBeInTheDocument();
        expect(screen.getByText('1/19/2025')).toBeInTheDocument();
        expect(screen.getByText('Startup Ideas')).toBeInTheDocument();
        expect(screen.getByText('Blog Content')).toBeInTheDocument();
        expect(screen.getByText('excited')).toBeInTheDocument();
        expect(screen.getByText('curious')).toBeInTheDocument();
      });
    });

    it('should show "View All" link', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('View All →')).toBeInTheDocument();
      });
    });

    it('should show empty state when no ideas', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('No ideas yet. Start by adding your first idea!')).toBeInTheDocument();
      });
    });
  });

  describe('Analytics Section', () => {
    const mockIdeas = [
      {
        id: 1,
        content: 'Startup idea',
        project: 'Startup Ideas',
        theme: 'tech',
        emotion: 'excited'
      },
      {
        id: 2,
        content: 'Blog idea',
        project: 'Blog Content',
        theme: 'creativity',
        emotion: 'curious'
      },
      {
        id: 3,
        content: 'Another startup idea',
        project: 'Startup Ideas',
        theme: 'business',
        emotion: 'excited'
      }
    ];

    it('should display projects breakdown', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument();
        expect(screen.getByText('Startup Ideas')).toBeInTheDocument();
        expect(screen.getByText('Blog Content')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // Startup Ideas count
        expect(screen.getByText('1')).toBeInTheDocument(); // Blog Content count
      });
    });

    it('should display emotions breakdown', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Emotions')).toBeInTheDocument();
        expect(screen.getByText('excited')).toBeInTheDocument();
        expect(screen.getByText('curious')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // excited count
        expect(screen.getByText('1')).toBeInTheDocument(); // curious count
      });
    });

    it('should show empty state for analytics when no data', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('No projects yet')).toBeInTheDocument();
        expect(screen.getByText('No emotions analyzed yet')).toBeInTheDocument();
      });
    });
  });

  describe('Quick Actions', () => {
    it('should display quick action buttons', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
        expect(screen.getByText('✍️')).toBeInTheDocument();
        expect(screen.getByText('Add New Idea')).toBeInTheDocument();
        expect(screen.getByText('⚡')).toBeInTheDocument();
        expect(screen.getByText('Transform Ideas')).toBeInTheDocument();
        expect(screen.getByText('🔍')).toBeInTheDocument();
        expect(screen.getByText('Search Ideas')).toBeInTheDocument();
      });
    });

    it('should have proper links for quick actions', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        const addIdeaLink = screen.getByText('Add New Idea').closest('a');
        expect(addIdeaLink).toHaveAttribute('href', '/ideas');
        
        const transformLink = screen.getByText('Transform Ideas').closest('a');
        expect(transformLink).toHaveAttribute('href', '/transform');
        
        const searchLink = screen.getByText('Search Ideas').closest('a');
        expect(searchLink).toHaveAttribute('href', '/ideas');
      });
    });
  });

  describe('Navigation', () => {
    it('should render navigation links', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('AI Brain Vault')).toBeInTheDocument();
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Ideas')).toBeInTheDocument();
        expect(screen.getByText('Transform')).toBeInTheDocument();
        expect(screen.getByText('Logout')).toBeInTheDocument();
      });
    });

    it('should highlight current page', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        const dashboardLink = screen.getByText('Dashboard');
        expect(dashboardLink).toHaveClass('text-blue-600');
        expect(dashboardLink).toHaveClass('font-medium');
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors gracefully', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching dashboard data:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it('should handle empty response', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => null
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Ideas')).toBeInTheDocument();
        expect(screen.getByText('0')).toBeInTheDocument();
      });
    });
  });

  describe('Data Processing', () => {
    it('should correctly calculate monthly ideas', async () => {
      const mockIdeas = [
        {
          id: 1,
          content: 'This month idea',
          timestamp: '2025-01-15T00:00:00Z'
        },
        {
          id: 2,
          content: 'Last month idea',
          timestamp: '2024-12-15T00:00:00Z'
        }
      ];

      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument(); // This month count
      });
    });

    it('should correctly count unique projects and themes', async () => {
      const mockIdeas = [
        {
          id: 1,
          project: 'Project A',
          theme: 'Theme A'
        },
        {
          id: 2,
          project: 'Project A', // Duplicate project
          theme: 'Theme B'
        },
        {
          id: 3,
          project: 'Project B',
          theme: 'Theme A' // Duplicate theme
        }
      ];

      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('2')).toBeInTheDocument(); // Projects count
        expect(screen.getByText('2')).toBeInTheDocument(); // Themes count
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Dashboard');
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Recent Ideas');
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Projects');
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Emotions');
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Quick Actions');
      });
    });

    it('should have proper ARIA labels', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<DashboardPage />);
      
      await waitFor(() => {
        const quickActionLinks = screen.getAllByRole('link');
        quickActionLinks.forEach(link => {
          expect(link).toHaveAttribute('href');
        });
      });
    });
  });
}); 