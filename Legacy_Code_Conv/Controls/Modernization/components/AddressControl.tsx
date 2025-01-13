/**
 * Address control component.
 */
import React, { useState, useEffect } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { AddressType, Address, ValidationResult } from '../types';
import { MapComponent } from './MapComponent';

interface AddressControlProps {
  initialValue?: Address;
  onValidated?: (address: Address) => void;
  onChange?: (address: Address) => void;
  readOnly?: boolean;
  showMap?: boolean;
}

const validationSchema = Yup.object({
  street1: Yup.string().required('Street address is required'),
  street2: Yup.string(),
  city: Yup.string().required('City is required'),
  state: Yup.string()
    .required('State is required')
    .matches(/^[A-Z]{2}$/, 'Invalid state format'),
  zipCode: Yup.string()
    .required('ZIP code is required')
    .matches(/^\d{5}(-\d{4})?$/, 'Invalid ZIP code format'),
  type: Yup.string().oneOf(Object.values(AddressType)),
  isPrimary: Yup.boolean(),
});

export const AddressControl: React.FC<AddressControlProps> = ({
  initialValue,
  onValidated,
  onChange,
  readOnly = false,
  showMap = true,
}) => {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [coordinates, setCoordinates] = useState<{lat: number; lng: number} | null>(null);

  const formik = useFormik({
    initialValues: initialValue || {
      street1: '',
      street2: '',
      city: '',
      state: '',
      zipCode: '',
      type: AddressType.HOME,
      isPrimary: false,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        // Validate address
        const response = await fetch('/api/controls/address/validate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(values),
        });
        
        const result = await response.json();
        setValidationResult(result);
        
        if (result.isValid) {
          // Get coordinates
          const coordResponse = await fetch('/api/controls/address/coordinates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(values),
          });
          
          const coords = await coordResponse.json();
          setCoordinates(coords);
          
          if (onValidated) {
            onValidated({
              ...values,
              latitude: coords.latitude,
              longitude: coords.longitude,
              validated: true,
              validationDate: new Date(),
            });
          }
        }
      } catch (error) {
        console.error('Address validation failed:', error);
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
        {/* Street Address 1 */}
        <div>
          <label htmlFor="street1" className="block text-sm font-medium text-gray-700">
            Street Address
          </label>
          <input
            type="text"
            id="street1"
            {...formik.getFieldProps('street1')}
            readOnly={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          />
          {formik.touched.street1 && formik.errors.street1 && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.street1}</p>
          )}
        </div>

        {/* Street Address 2 */}
        <div>
          <label htmlFor="street2" className="block text-sm font-medium text-gray-700">
            Street Address 2
          </label>
          <input
            type="text"
            id="street2"
            {...formik.getFieldProps('street2')}
            readOnly={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          />
        </div>

        {/* City, State, ZIP */}
        <div className="grid grid-cols-6 gap-4">
          <div className="col-span-3">
            <label htmlFor="city" className="block text-sm font-medium text-gray-700">
              City
            </label>
            <input
              type="text"
              id="city"
              {...formik.getFieldProps('city')}
              readOnly={readOnly}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                readOnly ? 'bg-gray-100' : ''
              }`}
            />
            {formik.touched.city && formik.errors.city && (
              <p className="mt-1 text-sm text-red-600">{formik.errors.city}</p>
            )}
          </div>

          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700">
              State
            </label>
            <input
              type="text"
              id="state"
              {...formik.getFieldProps('state')}
              readOnly={readOnly}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                readOnly ? 'bg-gray-100' : ''
              }`}
            />
            {formik.touched.state && formik.errors.state && (
              <p className="mt-1 text-sm text-red-600">{formik.errors.state}</p>
            )}
          </div>

          <div className="col-span-2">
            <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700">
              ZIP Code
            </label>
            <input
              type="text"
              id="zipCode"
              {...formik.getFieldProps('zipCode')}
              readOnly={readOnly}
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                readOnly ? 'bg-gray-100' : ''
              }`}
            />
            {formik.touched.zipCode && formik.errors.zipCode && (
              <p className="mt-1 text-sm text-red-600">{formik.errors.zipCode}</p>
            )}
          </div>
        </div>

        {/* Address Type */}
        <div>
          <label htmlFor="type" className="block text-sm font-medium text-gray-700">
            Address Type
          </label>
          <select
            id="type"
            {...formik.getFieldProps('type')}
            disabled={readOnly}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              readOnly ? 'bg-gray-100' : ''
            }`}
          >
            {Object.values(AddressType).map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Primary Address */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="isPrimary"
            {...formik.getFieldProps('isPrimary')}
            disabled={readOnly}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="isPrimary" className="ml-2 block text-sm text-gray-700">
            Primary Address
          </label>
        </div>

        {!readOnly && (
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Validate Address
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
                {validationResult.isValid ? 'Address Validated' : 'Validation Failed'}
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

      {/* Map */}
      {showMap && coordinates && (
        <div className="mt-4 h-64">
          <MapComponent
            center={coordinates}
            zoom={15}
            markers={[{ position: coordinates, title: 'Selected Address' }]}
          />
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
