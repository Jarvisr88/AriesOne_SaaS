import React from 'react';
import { useChangeTracker } from '../../hooks/useChangeTracker';
import { cn } from '../../utils/styles';

interface FormFieldProps {
  id: string;
  label: string;
  error?: string;
  required?: boolean;
  className?: string;
  children: React.ReactNode;
  onChange?: (value: any) => void;
}

export const FormField: React.FC<FormFieldProps> = ({
  id,
  label,
  error,
  required,
  className,
  children,
  onChange,
}) => {
  const { trackChange } = useChangeTracker({
    controlId: id,
    controlType: 'FormField',
    onChanged: changes => {
      console.log('Field changes:', changes);
    },
  });

  const handleChange = (value: any) => {
    trackChange(id, children, value);
    onChange?.(value);
  };

  return (
    <div className={cn('form-field', className)}>
      <label 
        htmlFor={id}
        className={cn(
          'block text-sm font-medium text-gray-700',
          required && 'required'
        )}
      >
        {label}
      </label>
      <div className="mt-1">
        {React.Children.map(children, child =>
          React.isValidElement(child)
            ? React.cloneElement(child, {
                id,
                'aria-describedby': error ? `${id}-error` : undefined,
                onChange: handleChange,
                className: cn(
                  child.props.className,
                  error && 'border-red-500'
                ),
              })
            : child
        )}
      </div>
      {error && (
        <p
          className="mt-2 text-sm text-red-600"
          id={`${id}-error`}
        >
          {error}
        </p>
      )}
    </div>
  );
};
