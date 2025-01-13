/**
 * Price calculator component with rule management.
 */
import React, { useState, useEffect } from 'react';
import { PriceType, PriceCategory, PriceCalculationRule } from '../types';
import { usePriceCalculation } from '../hooks/usePriceCalculation';
import { Button } from './common/Button';
import { Input } from './common/Input';
import { Select } from './common/Select';
import { Spinner } from './common/Spinner';
import { ErrorMessage } from './common/ErrorMessage';
import { formatCurrency } from '../utils/formatters';

interface PriceCalculatorProps {
  companyId: string;
}

export const PriceCalculator: React.FC<PriceCalculatorProps> = ({
  companyId,
}) => {
  const [basePrice, setBasePrice] = useState<string>('');
  const [priceType, setPriceType] = useState<PriceType>(PriceType.SALE);
  const [priceCategory, setPriceCategory] = useState<PriceCategory>(PriceCategory.BILLABLE);
  const [showRules, setShowRules] = useState(false);

  const {
    calculatedPrice,
    rules,
    loading,
    error,
    calculatePrice,
    updateRule,
    createRule,
    deleteRule,
  } = usePriceCalculation(companyId);

  const handleCalculate = async () => {
    if (!basePrice) return;

    try {
      await calculatePrice({
        basePrice: parseFloat(basePrice),
        priceType,
        priceCategory,
      });
    } catch (error) {
      console.error('Failed to calculate price:', error);
    }
  };

  const handleRuleChange = async (rule: PriceCalculationRule) => {
    try {
      await updateRule(rule);
    } catch (error) {
      console.error('Failed to update rule:', error);
    }
  };

  const handleAddRule = async () => {
    try {
      await createRule({
        company_id: companyId,
        rule_name: 'New Rule',
        description: 'New price calculation rule',
        price_type: priceType,
        price_category: priceCategory,
        calculation_formula: 'base_price',
        parameters: {},
        is_active: true,
      });
    } catch (error) {
      console.error('Failed to create rule:', error);
    }
  };

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Price Calculator</h2>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Input
              label="Base Price"
              type="number"
              value={basePrice}
              onChange={(e) => setBasePrice(e.target.value)}
              placeholder="Enter base price"
              min="0"
              step="0.01"
            />
          </div>

          <div>
            <Select
              label="Price Type"
              value={priceType}
              onChange={(e) => setPriceType(e.target.value as PriceType)}
            >
              {Object.values(PriceType).map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <Select
              label="Price Category"
              value={priceCategory}
              onChange={(e) => setPriceCategory(e.target.value as PriceCategory)}
            >
              {Object.values(PriceCategory).map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              variant="primary"
              onClick={handleCalculate}
              disabled={!basePrice}
              className="w-full"
            >
              Calculate
            </Button>
          </div>
        </div>

        {calculatedPrice !== null && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="text-lg font-medium text-gray-700">
              Calculated Price:
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {formatCurrency(calculatedPrice)}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Calculation Rules</h3>
          <Button onClick={() => setShowRules(!showRules)}>
            {showRules ? 'Hide Rules' : 'Show Rules'}
          </Button>
        </div>

        {showRules && (
          <div className="space-y-4">
            {rules.map((rule) => (
              <div
                key={rule.id}
                className="p-4 border rounded-lg hover:border-blue-500 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <Input
                      value={rule.rule_name}
                      onChange={(e) =>
                        handleRuleChange({ ...rule, rule_name: e.target.value })
                      }
                      className="font-medium"
                    />
                    <Input
                      value={rule.description}
                      onChange={(e) =>
                        handleRuleChange({ ...rule, description: e.target.value })
                      }
                      className="text-sm text-gray-600 mt-1"
                    />
                  </div>
                  <Button
                    variant="danger"
                    onClick={() => deleteRule(rule.id)}
                    size="sm"
                  >
                    Delete
                  </Button>
                </div>

                <div className="mt-4">
                  <Input
                    label="Calculation Formula"
                    value={rule.calculation_formula}
                    onChange={(e) =>
                      handleRuleChange({
                        ...rule,
                        calculation_formula: e.target.value,
                      })
                    }
                    placeholder="e.g., base_price * 1.1"
                  />
                </div>

                <div className="mt-4 flex items-center space-x-4">
                  <Select
                    value={rule.price_type}
                    onChange={(e) =>
                      handleRuleChange({
                        ...rule,
                        price_type: e.target.value as PriceType,
                      })
                    }
                  >
                    {Object.values(PriceType).map((type) => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </Select>

                  <Select
                    value={rule.price_category}
                    onChange={(e) =>
                      handleRuleChange({
                        ...rule,
                        price_category: e.target.value as PriceCategory,
                      })
                    }
                  >
                    {Object.values(PriceCategory).map((category) => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </Select>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={rule.is_active}
                      onChange={(e) =>
                        handleRuleChange({
                          ...rule,
                          is_active: e.target.checked,
                        })
                      }
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-600">Active</span>
                  </div>
                </div>
              </div>
            ))}

            <Button onClick={handleAddRule} className="mt-4">
              Add Rule
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
