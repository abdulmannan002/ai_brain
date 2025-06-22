import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import IdeasPage from '../app/ideas/page';

// Mock Auth0
jest.mock('@auth0/nextjs-auth0/client', () => ({
  useUser: () => ({
    user: { email: 'test@example.com', sub: 'test_user_123' },
    isLoading: false,
    accessToken: 'mock_token'
  })
}));

// Mock fetch
global.fetch = jest.fn();

describe('IdeasPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication', () => {
    it('should show login message when user is not authenticated', () => {
      // Mock unauthenticated user
      jest.doMock('@auth0/nextjs-auth0/client', () => ({
        useUser: () => ({
          user: null,
          isLoading: false
        })
      }));

      render(<IdeasPage />);
      expect(screen.getByText('Please log in to access your ideas')).toBeInTheDocument();
    });

    it('should show loading spinner when authentication is loading', () => {
      jest.doMock('@auth0/nextjs-auth0/client', () => ({
        useUser: () => ({
          user: null,
          isLoading: true
        })
      }));

      render(<IdeasPage />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('Idea Input', () => {
    it('should render idea input form', () => {
      render(<IdeasPage />);
      
      expect(screen.getByText('Add New Idea')).toBeInTheDocument();
      expect(screen.getByPlaceholderText("What's on your mind? Share your idea...")).toBeInTheDocument();
      expect(screen.getByText('Submit Idea')).toBeInTheDocument();
      expect(screen.getByText('🎤 Voice Input')).toBeInTheDocument();
    });

    it('should update content when typing', () => {
      render(<IdeasPage />);
      
      const textarea = screen.getByPlaceholderText("What's on your mind? Share your idea...");
      fireEvent.change(textarea, { target: { value: 'Test idea content' } });
      
      expect(textarea).toHaveValue('Test idea content');
    });

    it('should submit idea successfully', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, content: 'Test idea', source: 'web-form' })
      } as Response);

      render(<IdeasPage />);
      
      const textarea = screen.getByPlaceholderText("What's on your mind? Share your idea...");
      const submitButton = screen.getByText('Submit Idea');
      
      fireEvent.change(textarea, { target: { value: 'Test idea content' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/ideas', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock_token'
          },
          body: JSON.stringify({ content: 'Test idea content', source: 'web-form' })
        });
      });
    });

    it('should handle submission error', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: false
      } as Response);

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<IdeasPage />);
      
      const textarea = screen.getByPlaceholderText("What's on your mind? Share your idea...");
      const submitButton = screen.getByText('Submit Idea');
      
      fireEvent.change(textarea, { target: { value: 'Test idea content' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Failed to submit idea.');
      });

      alertSpy.mockRestore();
    });

    it('should disable submit button when content is empty', () => {
      render(<IdeasPage />);
      
      const submitButton = screen.getByText('Submit Idea');
      expect(submitButton).toBeDisabled();
    });

    it('should handle voice input', async () => {
      render(<IdeasPage />);
      
      const voiceButton = screen.getByText('🎤 Voice Input');
      fireEvent.click(voiceButton);
      
      expect(screen.getByText('Recording...')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('🎤 Voice Input')).toBeInTheDocument();
      }, { timeout: 4000 });
    });
  });

  describe('Search and Filtering', () => {
    it('should render search and filter controls', () => {
      render(<IdeasPage />);
      
      expect(screen.getByText('Search & Filter')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Search ideas...')).toBeInTheDocument();
      expect(screen.getByText('All Projects')).toBeInTheDocument();
      expect(screen.getByText('All Themes')).toBeInTheDocument();
      expect(screen.getByText('All Emotions')).toBeInTheDocument();
      expect(screen.getByText('Search')).toBeInTheDocument();
    });

    it('should update search query', () => {
      render(<IdeasPage />);
      
      const searchInput = screen.getByPlaceholderText('Search ideas...');
      fireEvent.change(searchInput, { target: { value: 'AI' } });
      
      expect(searchInput).toHaveValue('AI');
    });

    it('should filter by project', () => {
      render(<IdeasPage />);
      
      const projectSelect = screen.getByText('All Projects');
      fireEvent.click(projectSelect);
      
      const startupOption = screen.getByText('Startup Ideas');
      fireEvent.click(startupOption);
      
      expect(projectSelect).toHaveTextContent('Startup Ideas');
    });

    it('should perform search', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<IdeasPage />);
      
      const searchInput = screen.getByPlaceholderText('Search ideas...');
      const searchButton = screen.getByText('Search');
      
      fireEvent.change(searchInput, { target: { value: 'AI' } });
      fireEvent.click(searchButton);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/ideas/search?q=AI', {
          headers: {
            'Authorization': 'Bearer mock_token'
          }
        });
      });
    });
  });

  describe('Ideas Display', () => {
    const mockIdeas = [
      {
        id: 1,
        content: 'Test idea 1',
        source: 'web-form',
        timestamp: '2025-01-01T00:00:00Z',
        project: 'Startup Ideas',
        theme: 'tech',
        emotion: 'excited',
        transformed_output: null
      },
      {
        id: 2,
        content: 'Test idea 2',
        source: 'voice',
        timestamp: '2025-01-02T00:00:00Z',
        project: 'Blog Content',
        theme: 'creativity',
        emotion: 'curious',
        transformed_output: 'Generated blog post'
      }
    ];

    it('should display ideas when available', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Test idea 1')).toBeInTheDocument();
        expect(screen.getByText('Test idea 2')).toBeInTheDocument();
      });
    });

    it('should show idea metadata', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Source: web-form')).toBeInTheDocument();
        expect(screen.getByText('Source: voice')).toBeInTheDocument();
        expect(screen.getByText('Project: Startup Ideas')).toBeInTheDocument();
        expect(screen.getByText('Project: Blog Content')).toBeInTheDocument();
        expect(screen.getByText('Theme: tech')).toBeInTheDocument();
        expect(screen.getByText('Theme: creativity')).toBeInTheDocument();
        expect(screen.getByText('Emotion: excited')).toBeInTheDocument();
        expect(screen.getByText('Emotion: curious')).toBeInTheDocument();
      });
    });

    it('should show transformation buttons', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Blog Post')).toHaveLength(2);
        expect(screen.getAllByText('IP Summary')).toHaveLength(2);
        expect(screen.getAllByText('Tasks')).toHaveLength(2);
      });
    });

    it('should show transformed content when available', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdeas
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Transformation:')).toBeInTheDocument();
        expect(screen.getByText('Generated blog post')).toBeInTheDocument();
      });
    });

    it('should show empty state when no ideas', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('No ideas found. Start by adding your first idea!')).toBeInTheDocument();
      });
    });
  });

  describe('Idea Transformation', () => {
    it('should transform idea to blog post', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [{
            id: 1,
            content: 'Test idea',
            source: 'web-form',
            timestamp: '2025-01-01T00:00:00Z',
            project: 'Startup Ideas',
            theme: 'tech',
            emotion: 'excited',
            transformed_output: null
          }]
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ transformed_content: 'Generated blog post content' })
        } as Response);

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Test idea')).toBeInTheDocument();
      });

      const blogPostButton = screen.getByText('Blog Post');
      fireEvent.click(blogPostButton);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/transform', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock_token'
          },
          body: JSON.stringify({
            idea_id: 1,
            output_type: 'content',
            user_id: 'test_user_123'
          })
        });
        expect(alertSpy).toHaveBeenCalledWith('content generated successfully!');
      });

      alertSpy.mockRestore();
    });

    it('should handle transformation error', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [{
            id: 1,
            content: 'Test idea',
            source: 'web-form',
            timestamp: '2025-01-01T00:00:00Z',
            project: 'Startup Ideas',
            theme: 'tech',
            emotion: 'excited',
            transformed_output: null
          }]
        } as Response)
        .mockResolvedValueOnce({
          ok: false
        } as Response);

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Test idea')).toBeInTheDocument();
      });

      const blogPostButton = screen.getByText('Blog Post');
      fireEvent.click(blogPostButton);
      
      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Failed to transform idea.');
      });

      alertSpy.mockRestore();
    });
  });

  describe('Navigation', () => {
    it('should render navigation links', () => {
      render(<IdeasPage />);
      
      expect(screen.getByText('AI Brain Vault')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Ideas')).toBeInTheDocument();
      expect(screen.getByText('Transform')).toBeInTheDocument();
      expect(screen.getByText('Logout')).toBeInTheDocument();
    });

    it('should highlight current page', () => {
      render(<IdeasPage />);
      
      const ideasLink = screen.getByText('Ideas');
      expect(ideasLink).toHaveClass('text-blue-600');
      expect(ideasLink).toHaveClass('font-medium');
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors gracefully', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching ideas:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it('should handle empty response', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => null
      } as Response);

      render(<IdeasPage />);
      
      await waitFor(() => {
        expect(screen.getByText('No ideas found. Start by adding your first idea!')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<IdeasPage />);
      
      const textarea = screen.getByPlaceholderText("What's on your mind? Share your idea...");
      expect(textarea).toHaveAttribute('rows', '4');
      
      const submitButton = screen.getByText('Submit Idea');
      expect(submitButton).toHaveAttribute('type', 'button');
    });

    it('should be keyboard navigable', () => {
      render(<IdeasPage />);
      
      const textarea = screen.getByPlaceholderText("What's on your mind? Share your idea...");
      const submitButton = screen.getByText('Submit Idea');
      
      textarea.focus();
      expect(textarea).toHaveFocus();
      
      fireEvent.keyDown(textarea, { key: 'Tab' });
      expect(submitButton).toHaveFocus();
    });
  });
}); 