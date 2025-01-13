/**
 * Name control component.
 */
import React, { useState, useEffect } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { NameFormat, ValidationResult } from '../types';

interface NameControlProps {
  initialValue?: NameFormat;
  onValidated?: (name: NameFormat) => void;
  onChange?: (name: NameFormat) => void;
  readOnly?: boolean;
}

const validationSchema = Yup.object({
  firstName: Yup.string().required('First name is required'),
  middleName: Yup.string(),
  lastName: Yup.string().required('Last name is required'),
  suffix: Yup.string(),
  prefix: Yup.string(),
});

export const NameControl: React.FC<NameControlProps> = ({
  initialValue,
  onValidated,
  onChange,
  readOnly = false,
}) => {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  const formik = useFormik({
    initialValues: initialValue || {
      firstName: '',
      middleName: '',
      lastName: '',
      suffix: '',
      prefix: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        // Validate name
        const response = await fetch('/api/controls/name/validate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(values),
        });
        
        const result = await response.json();
        setValidationResult(result);
        
        if (result.isValid) {
          // Standardize name
          const standardizeResponse = await fetch('/api/controls/name/standardize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(values),
          });
          
          const standardizedName = await standardizeResponse.json();
          formik.setValues(standardizedName);
          
          if (onValidated) {
            onValidated(standardizedName);
          }
        }
      } catch (error) {
        console.error('Name validation failed:', error);
      }
    },
  });

  useEffect(() => {
    if (onChange) {
      onChange(formik.values);
    }
  }, [formik.values]);

  return (
    <div className="space-y-4">
      <form onSubmit={formik.handleSubmit} className="space-y-4">
        {/* Prefix */}
        <div>
          <label htmlFor="prefix" className="block text-sm font-medium text-gray-700">
            Prefix
          </label>
          <select
            id="prefix"
            {...formik.getFieldProps('prefix')}
            disabled={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          >
            <option value="">None</option>
            <option value="Mr.">Mr.</option>
            <option value="Mrs.">Mrs.</option>
            <option value="Ms.">Ms.</option>
            <option value="Dr.">Dr.</option>
            <option value="Prof.">Prof.</option>
          </select>
        </div>

        {/* First Name */}
        <div>
          <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
            First Name
          </label>
          <input
            type="text"
            id="firstName"
            {...formik.getFieldProps('firstName')}
            readOnly={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          />
          {formik.touched.firstName && formik.errors.firstName && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.firstName}</p>
          )}
        </div>

        {/* Middle Name */}
        <div>
          <label htmlFor="middleName" className="block text-sm font-medium text-gray-700">
            Middle Name
          </label>
          <input
            type="text"
            id="middleName"
            {...formik.getFieldProps('middleName')}
            readOnly={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          />
        </div>

        {/* Last Name */}
        <div>
          <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
            Last Name
          </label>
          <input
            type="text"
            id="lastName"
            {...formik.getFieldProps('lastName')}
            readOnly={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          />
          {formik.touched.lastName && formik.errors.lastName && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.lastName}</p>
          )}
        </div>

        {/* Suffix */}
        <div>
          <label htmlFor="suffix" className="block text-sm font-medium text-gray-700">
            Suffix
          </label>
          <select
            id="suffix"
            {...formik.getFieldProps('suffix')}
            disabled={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          >
            <option value="">None</option>
            <option value="Jr.">Jr.</option>
            <option value="Sr.">Sr.</option>
            <option value="II">II</option>
            <option value="III">III</option>
            <option value="IV">IV</option>
          </select>
        </div>

        {!readOnly && (
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Validate & Standardize
          </button>
        )}
      </form>

      {/* Validation Results */}
      {validationResult && (
        <div className={`mt-4 rounded-md p-4 ${
          validationResult.isValid ? 'bg-green-50' : 'bg-red-50'
        }`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {validationResult.isValid ? (
                <CheckCircleIcon className="h-5 w-5 text-green-400" />
              ) : (
                <XCircleIcon className="h-5 w-5 text-red-400" />
              )}
            </div>
            <div className="ml-3">
              <h3 className={`text-sm font-medium ${
                validationResult.isValid ? 'text-green-800' : 'text-red-800'
              }`}>
                {validationResult.isValid ? 'Name Validated' : 'Validation Failed'}
              </h3>
              {validationResult.errors.length > 0 && (
                <div className="mt-2 text-sm text-red-700">
                  <ul className="list-disc pl-5 space-y-1">
                    {validationResult.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              {validationResult.warnings.length > 0 && (
                <div className="mt-2 text-sm text-yellow-700">
                  <ul className="list-disc pl-5 space-y-1">
                    {validationResult.warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Icons
const CheckCircleIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const XCircleIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);
