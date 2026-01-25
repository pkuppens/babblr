/**
 * Tests for TabBar component.
 *
 * Verifies:
 * - Tab rendering and selection
 * - Keyboard navigation (Arrow keys, Home, End, Enter, Space)
 * - Accessibility attributes
 * - Visual state indication
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TabBar from './TabBar';

describe('TabBar', () => {
  describe('when rendered', () => {
    it('should render all tabs with correct labels', () => {
      const mockOnTabChange = vi.fn();
      // Pass explicit language to ensure English labels
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      expect(screen.getByRole('tab', { name: /home tab/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /vocabulary lessons tab/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /grammar lessons tab/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /conversations tab/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /assessments tab/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /configuration settings tab/i })).toBeInTheDocument();
    });

    it('should highlight the active tab', () => {
      const mockOnTabChange = vi.fn();
      const { rerender } = render(
        <TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />
      );

      const homeTab = screen.getByRole('tab', { name: /home tab/i });
      expect(homeTab).toHaveClass('tab-button-active');
      expect(homeTab).toHaveAttribute('aria-selected', 'true');

      rerender(<TabBar activeTab="conversations" onTabChange={mockOnTabChange} />);
      const conversationsTab = screen.getByRole('tab', { name: /conversations tab/i });
      expect(conversationsTab).toHaveClass('tab-button-active');
      expect(conversationsTab).toHaveAttribute('aria-selected', 'true');
      expect(homeTab).not.toHaveClass('tab-button-active');
    });

    it('should set correct tabIndex for accessibility', () => {
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="vocabulary" onTabChange={mockOnTabChange} language="english" />);

      const activeTab = screen.getByRole('tab', { name: /vocabulary lessons tab/i });
      expect(activeTab).toHaveAttribute('tabIndex', '0');

      const inactiveTabs = screen.getAllByRole('tab').filter(tab => tab !== activeTab);
      inactiveTabs.forEach(tab => {
        expect(tab).toHaveAttribute('tabIndex', '-1');
      });
    });
  });

  describe('when a tab is clicked', () => {
    it('should call onTabChange with the correct tab key', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const conversationsTab = screen.getByRole('tab', { name: /conversations tab/i });
      await user.click(conversationsTab);

      expect(mockOnTabChange).toHaveBeenCalledTimes(1);
      expect(mockOnTabChange).toHaveBeenCalledWith('conversations');
    });
  });

  describe('when using keyboard navigation', () => {
    it('should navigate to the next tab with ArrowRight', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const homeTab = screen.getByRole('tab', { name: /home tab/i });
      homeTab.focus();

      await user.keyboard('{ArrowRight}');

      expect(mockOnTabChange).toHaveBeenCalledWith('vocabulary');
    });

    it('should navigate to the previous tab with ArrowLeft', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="vocabulary" onTabChange={mockOnTabChange} language="english" />);

      const vocabularyTab = screen.getByRole('tab', { name: /vocabulary lessons tab/i });
      vocabularyTab.focus();

      await user.keyboard('{ArrowLeft}');

      expect(mockOnTabChange).toHaveBeenCalledWith('home');
    });

    it('should wrap to the last tab when ArrowLeft is pressed on the first tab', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const homeTab = screen.getByRole('tab', { name: /home tab/i });
      homeTab.focus();

      await user.keyboard('{ArrowLeft}');

      expect(mockOnTabChange).toHaveBeenCalledWith('configuration');
    });

    it('should wrap to the first tab when ArrowRight is pressed on the last tab', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="configuration" onTabChange={mockOnTabChange} language="english" />);

      const configTab = screen.getByRole('tab', { name: /configuration settings tab/i });
      configTab.focus();

      await user.keyboard('{ArrowRight}');

      expect(mockOnTabChange).toHaveBeenCalledWith('home');
    });

    it('should navigate to the first tab with Home key', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="assessments" onTabChange={mockOnTabChange} language="english" />);

      const assessmentsTab = screen.getByRole('tab', { name: /assessments tab/i });
      assessmentsTab.focus();

      await user.keyboard('{Home}');

      expect(mockOnTabChange).toHaveBeenCalledWith('home');
    });

    it('should navigate to the last tab with End key', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const homeTab = screen.getByRole('tab', { name: /home tab/i });
      homeTab.focus();

      await user.keyboard('{End}');

      expect(mockOnTabChange).toHaveBeenCalledWith('configuration');
    });

    it('should activate a tab with Enter key', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const grammarTab = screen.getByRole('tab', { name: /grammar lessons tab/i });
      grammarTab.focus();

      await user.keyboard('{Enter}');

      expect(mockOnTabChange).toHaveBeenCalledWith('grammar');
    });

    it('should activate a tab with Space key', async () => {
      const user = userEvent.setup();
      const mockOnTabChange = vi.fn();
      render(<TabBar activeTab="home" onTabChange={mockOnTabChange} language="english" />);

      const vocabularyTab = screen.getByRole('tab', { name: /vocabulary lessons tab/i });
      vocabularyTab.focus();

      await user.keyboard(' ');

      expect(mockOnTabChange).toHaveBeenCalledWith('vocabulary');
    });
  });
});
