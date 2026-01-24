/**
 * Model Combobox Component
 *
 * A combobox that allows selecting from predefined models or entering a custom model name.
 * Combines a dropdown with known values and a text input for expert users.
 */

import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface ModelOption {
  value: string;
  label: string;
}

interface ModelComboboxProps {
  value: string;
  onChange: (value: string) => void;
  options: ModelOption[];
  placeholder?: string;
  className?: string;
  id?: string;
}

export default function ModelCombobox({
  value,
  onChange,
  options,
  placeholder = 'Select or type model name...',
  className = '',
  id,
}: ModelComboboxProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value);
  const [filteredOptions, setFilteredOptions] = useState(options);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update input value when prop value changes
  useEffect(() => {
    setInputValue(value);
  }, [value]);

  // Filter options based on input
  useEffect(() => {
    if (inputValue.trim() === '') {
      setFilteredOptions(options);
    } else {
      const filtered = options.filter(
        option =>
          option.value.toLowerCase().includes(inputValue.toLowerCase()) ||
          option.label.toLowerCase().includes(inputValue.toLowerCase())
      );
      setFilteredOptions(filtered);
    }
  }, [inputValue, options]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setIsOpen(true);
    onChange(newValue);
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  const handleOptionSelect = (optionValue: string) => {
    setInputValue(optionValue);
    setIsOpen(false);
    onChange(optionValue);
    inputRef.current?.blur();
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && filteredOptions.length > 0) {
      e.preventDefault();
      handleOptionSelect(filteredOptions[0].value);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  return (
    <div ref={containerRef} className={`model-combobox ${className}`}>
      <div className="model-combobox-input-wrapper">
        <input
          ref={inputRef}
          id={id}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleInputKeyDown}
          placeholder={placeholder}
          className="settings-input model-combobox-input"
        />
        <button
          type="button"
          className="model-combobox-toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle dropdown"
        >
          <ChevronDown size={16} />
        </button>
      </div>
      {isOpen && (
        <div className="model-combobox-dropdown">
          {filteredOptions.length > 0 ? (
            filteredOptions.map(option => (
              <div
                key={option.value}
                className={`model-combobox-option ${value === option.value ? 'selected' : ''}`}
                onClick={() => handleOptionSelect(option.value)}
              >
                {option.label}
              </div>
            ))
          ) : (
            <div className="model-combobox-option no-results">
              No matching models. Type a custom model name.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
