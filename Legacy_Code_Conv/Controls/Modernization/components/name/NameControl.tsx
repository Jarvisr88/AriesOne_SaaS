import React, { useState } from 'react';
import { useChangeTracker } from '../../hooks/useChangeTracker';
import { FormField } from '../common/FormField';
import type { Name, Courtesy } from '../../types/name';

interface NameControlProps {
  id: string;
  value?: Name;
  onChange?: (name: Name) => void;
  className?: string;
}

const COURTESY_OPTIONS: Courtesy[] = [
  'Mr.',
  'Mrs.',
  'Ms.',
  'Dr.',
  'Prof.',
];

export const NameControl: React.FC<NameControlProps> = ({
  id,
  value,
  onChange,
  className,
}) => {
  const [errors, setErrors] = useState<Partial<Record<keyof Name, string>>>({});
  
  const { trackChange } = useChangeTracker({
    controlId: id,
    controlType: 'NameControl',
    onChanged: changes => {
      console.log('Name changes:', changes);
    },
  });

  const handleFieldChange = (field: keyof Name) => (value: string) => {
    const oldValue = value?.[field];
    trackChange(field, oldValue, value);
    
    onChange?.({
      ...value,
      [field]: value,
    });

    // Clear error when field is modified
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <div className={className}>
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-2">
          <FormField
            id={`${id}-courtesy`}
            label="Title"
            error={errors.courtesy}
          >
            <select
              value={value?.courtesy ?? ''}
              onChange={e => handleFieldChange('courtesy')(e.target.value as Courtesy)}
              className="w-full"
            >
              <option value="">Select...</option>
              {COURTESY_OPTIONS.map(title => (
                <option key={title} value={title}>
                  {title}
                </option>
              ))}
            </select>
          </FormField>
        </div>

        <div className="col-span-4">
          <FormField
            id={`${id}-firstName`}
            label="First Name"
            required
            error={errors.first_name}
          >
            <input
              type="text"
              value={value?.first_name ?? ''}
              onChange={e => handleFieldChange('first_name')(e.target.value)}
              className="w-full"
            />
          </FormField>
        </div>

        <div className="col-span-2">
          <FormField
            id={`${id}-middleName`}
            label="Middle"
            error={errors.middle_name}
          >
            <input
              type="text"
              value={value?.middle_name ?? ''}
              onChange={e => handleFieldChange('middle_name')(e.target.value)}
              className="w-full"
            />
          </FormField>
        </div>

        <div className="col-span-3">
          <FormField
            id={`${id}-lastName`}
            label="Last Name"
            required
            error={errors.last_name}
          >
            <input
              type="text"
              value={value?.last_name ?? ''}
              onChange={e => handleFieldChange('last_name')(e.target.value)}
              className="w-full"
            />
          </FormField>
        </div>

        <div className="col-span-1">
          <FormField
            id={`${id}-suffix`}
            label="Suffix"
            error={errors.suffix}
          >
            <input
              type="text"
              value={value?.suffix ?? ''}
              onChange={e => handleFieldChange('suffix')(e.target.value)}
              className="w-full"
              maxLength={3}
            />
          </FormField>
        </div>
      </div>

      {value && (
        <div className="mt-2 text-sm text-gray-600">
          <div>Full Name: {formatName(value, 'full')}</div>
          <div>Formal Name: {formatName(value, 'formal')}</div>
        </div>
      )}
    </div>
  );
};

const formatName = async (name: Name, format: 'full' | 'formal'): Promise<string> => {
  try {
    const response = await fetch('/api/controls/name/format', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, format_type: format }),
    });
    
    const data = await response.json();
    return data.formatted;
  } catch (error) {
    console.error('Name formatting failed:', error);
    return '';
  }
};
