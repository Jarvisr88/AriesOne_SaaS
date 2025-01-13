import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import {
  CheckedIcon,
  UncheckedIcon,
  IndeterminateIcon,
  ReloadIcon,
  Reload2Icon,
} from '../../components/IconLibrary';

describe('IconLibrary Components', () => {
  describe('CheckedIcon', () => {
    it('renders with default props', () => {
      render(<CheckedIcon data-testid="checked-icon" />);
      const icon = screen.getByTestId('checked-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.tagName.toLowerCase()).toBe('svg');
      expect(icon).toHaveAttribute('width', '24');
      expect(icon).toHaveAttribute('height', '24');
    });

    it('applies custom size', () => {
      render(<CheckedIcon size={32} data-testid="checked-icon" />);
      const icon = screen.getByTestId('checked-icon');
      expect(icon).toHaveAttribute('width', '32');
      expect(icon).toHaveAttribute('height', '32');
    });

    it('applies custom className', () => {
      render(<CheckedIcon className="custom-class" data-testid="checked-icon" />);
      const icon = screen.getByTestId('checked-icon');
      expect(icon).toHaveClass('custom-class');
    });
  });

  describe('UncheckedIcon', () => {
    it('renders with default props', () => {
      render(<UncheckedIcon data-testid="unchecked-icon" />);
      const icon = screen.getByTestId('unchecked-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.tagName.toLowerCase()).toBe('svg');
    });
  });

  describe('IndeterminateIcon', () => {
    it('renders with default props', () => {
      render(<IndeterminateIcon data-testid="indeterminate-icon" />);
      const icon = screen.getByTestId('indeterminate-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.tagName.toLowerCase()).toBe('svg');
    });
  });

  describe('ReloadIcon', () => {
    it('renders with default props', () => {
      render(<ReloadIcon data-testid="reload-icon" />);
      const icon = screen.getByTestId('reload-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.tagName.toLowerCase()).toBe('svg');
    });
  });

  describe('Reload2Icon', () => {
    it('renders with default props', () => {
      render(<Reload2Icon data-testid="reload2-icon" />);
      const icon = screen.getByTestId('reload2-icon');
      expect(icon).toBeInTheDocument();
      expect(icon.tagName.toLowerCase()).toBe('svg');
    });
  });
});
