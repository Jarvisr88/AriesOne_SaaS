import React, { useState } from 'react';
import { useChangeTracker } from '../../hooks/useChangeTracker';
import { FormField } from '../common/FormField';
import { MapButton } from './MapButton';
import type { Address } from '../../types/address';

interface AddressControlProps {
  id: string;
  value?: Address;
  onChange?: (address: Address) => void;
  onValidate?: (isValid: boolean) => void;
  className?: string;
}

export const AddressControl: React.FC<AddressControlProps> = ({
  id,
  value,
  onChange,
  onValidate,
  className,
}) => {
  const [errors, setErrors] = useState<Partial<Record<keyof Address, string>>>({});
  
  const { trackChange } = useChangeTracker({
    controlId: id,
    controlType: 'AddressControl',
    onChanged: changes => {
      console.log('Address changes:', changes);
    },
  });

  const handleFieldChange = (field: keyof Address) => (value: string) => {
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

  const validateAddress = async () => {
    try {
      const response = await fetch('/api/controls/address/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(value),
      });
      
      const data = await response.json();
      onValidate?.(data.valid);
      
      if (!data.valid) {
        setErrors({
          address1: 'Invalid address',
        });
      }
    } catch (error) {
      console.error('Address validation failed:', error);
      onValidate?.(false);
    }
  };

  return (
    <div className={className}>
      <FormField
        id={`${id}-address1`}
        label="Address Line 1"
        required
        error={errors.address1}
      >
        <input
          type="text"
          value={value?.address1 ?? ''}
          onChange={e => handleFieldChange('address1')(e.target.value)}
          className="w-full"
        />
      </FormField>

      <FormField
        id={`${id}-address2`}
        label="Address Line 2"
        error={errors.address2}
      >
        <input
          type="text"
          value={value?.address2 ?? ''}
          onChange={e => handleFieldChange('address2')(e.target.value)}
          className="w-full"
        />
      </FormField>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-6">
          <FormField
            id={`${id}-city`}
            label="City"
            required
            error={errors.city}
          >
            <input
              type="text"
              value={value?.city ?? ''}
              onChange={e => handleFieldChange('city')(e.target.value)}
              className="w-full"
            />
          </FormField>
        </div>

        <div className="col-span-2">
          <FormField
            id={`${id}-state`}
            label="State"
            required
            error={errors.state}
          >
            <input
              type="text"
              value={value?.state ?? ''}
              onChange={e => handleFieldChange('state')(e.target.value)}
              className="w-full"
              maxLength={2}
            />
          </FormField>
        </div>

        <div className="col-span-4">
          <FormField
            id={`${id}-zip`}
            label="ZIP Code"
            required
            error={errors.zip_code}
          >
            <input
              type="text"
              value={value?.zip_code ?? ''}
              onChange={e => handleFieldChange('zip_code')(e.target.value)}
              className="w-full"
              maxLength={10}
            />
          </FormField>
        </div>
      </div>

      <div className="mt-4 flex justify-end space-x-2">
        <button
          type="button"
          onClick={validateAddress}
          className="btn btn-secondary"
        >
          Validate
        </button>
        <MapButton address={value} />
      </div>
    </div>
  );
};
