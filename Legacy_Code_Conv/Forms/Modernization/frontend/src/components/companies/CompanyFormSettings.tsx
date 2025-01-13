/**
 * Company form settings component.
 * 
 * This component allows customizing form settings for a company.
 */
import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  Switch,
  VStack,
  useToast,
  Heading,
  Divider,
} from '@chakra-ui/react';
import {
  useCompanyForm,
  useUpdateCompanyForm,
} from '../../hooks/useCompanyQuery';
import { JsonEditor } from '../shared/JsonEditor';


interface CompanyFormSettingsProps {
  companyId: number;
  formId: number;
}

export const CompanyFormSettings: React.FC<CompanyFormSettingsProps> = ({
  companyId,
  formId,
}) => {
  const toast = useToast();
  const { data: companyForm } = useCompanyForm(companyId, formId);
  const updateSettings = useUpdateCompanyForm();
  
  const [settings, setSettings] = React.useState<Record<string, any>>({});
  const [isActive, setIsActive] = React.useState(true);
  
  React.useEffect(() => {
    if (companyForm) {
      setSettings(companyForm.settings || {});
      setIsActive(companyForm.is_active);
    }
  }, [companyForm]);
  
  const handleSave = async () => {
    try {
      await updateSettings.mutateAsync({
        companyId,
        formId,
        data: {
          settings,
          is_active: isActive,
        },
      });
      
      toast({
        title: 'Success',
        description: 'Settings updated successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update settings',
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={4}>
          Form Settings
        </Heading>
        
        <FormControl display="flex" alignItems="center">
          <FormLabel mb="0">
            Form Active
          </FormLabel>
          <Switch
            isChecked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
          />
        </FormControl>
      </Box>
      
      <Divider />
      
      <Box>
        <Heading size="md" mb={4}>
          Custom Settings
        </Heading>
        
        <FormControl>
          <FormLabel>Settings JSON</FormLabel>
          <JsonEditor
            value={settings}
            onChange={setSettings}
          />
          <FormHelperText>
            Customize form behavior for this company
          </FormHelperText>
        </FormControl>
      </Box>
      
      <Button
        colorScheme="blue"
        onClick={handleSave}
        isLoading={updateSettings.isPending}
      >
        Save Settings
      </Button>
    </VStack>
  );
};
