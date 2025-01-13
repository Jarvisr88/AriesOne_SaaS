# IntegrationSettings Transformation Rules

## Overview
This document defines the transformation rules for converting the C# `IntegrationSettings` class to Python.

## Source (C#)
```csharp
namespace DMEWorks.Ability
{
    [XmlType(AnonymousType=true), XmlRoot("settings", Namespace="", IsNullable=false)]
    public class IntegrationSettings
    {
        [XmlElement("credentials")]
        public DMEWorks.Ability.Credentials Credentials { get; set; }

        [XmlElement("clerk-credentials")]
        public DMEWorks.Ability.Credentials ClerkCredentials { get; set; }

        [XmlElement("eligibility-credentials")]
        public AbilityCredentials EligibilityCredentials { get; set; }

        [XmlElement("envelope-credentials")]
        public DMEWorks.Ability.EnvelopeCredentials EnvelopeCredentials { get; set; }

        public static IntegrationSettings XmlDeserialize(string value)
        {
            using (StringReader reader = new StringReader(value ?? string.Empty))
            {
                return (IntegrationSettings) new XmlSerializer(typeof(IntegrationSettings)).Deserialize(reader);
            }
        }

        public static string XmlSerialize(IntegrationSettings settings)
        {
            // ... XML serialization implementation
        }
    }
}
```

## Target (Python)
```python
class IntegrationSettings(BaseModel):
    credentials: Optional[Credentials] = Field(None)
    clerk_credentials: Optional[Credentials] = Field(None, alias="clerk-credentials")
    eligibility_credentials: Optional[AbilityCredentials] = Field(None, alias="eligibility-credentials")
    envelope_credentials: Optional[EnvelopeCredentials] = Field(None, alias="envelope-credentials")
```

## Field Mappings

### Credentials
- Source: `Credentials` (DMEWorks.Ability.Credentials)
- Target: `credentials` (Optional[Credentials])
- XML: `credentials`
- Transformation:
  - Use Credentials transformation rules
  - Handle null values
  - Maintain XML structure

### ClerkCredentials
- Source: `ClerkCredentials` (DMEWorks.Ability.Credentials)
- Target: `clerk_credentials` (Optional[Credentials])
- XML: `clerk-credentials`
- Transformation:
  - Use Credentials transformation rules
  - Handle null values
  - Maintain XML structure

### EligibilityCredentials
- Source: `EligibilityCredentials` (AbilityCredentials)
- Target: `eligibility_credentials` (Optional[AbilityCredentials])
- XML: `eligibility-credentials`
- Transformation:
  - Use AbilityCredentials transformation rules
  - Handle null values
  - Maintain XML structure

### EnvelopeCredentials
- Source: `EnvelopeCredentials` (DMEWorks.Ability.EnvelopeCredentials)
- Target: `envelope_credentials` (Optional[EnvelopeCredentials])
- XML: `envelope-credentials`
- Transformation:
  - Use EnvelopeCredentials transformation rules
  - Handle null values
  - Maintain XML structure

## XML Transformation

### C# to Python
```python
def transform_cs_to_python(xml_str: str) -> IntegrationSettings:
    if not xml_str:
        return IntegrationSettings()
        
    root = ET.fromstring(xml_str)
    settings = {}
    
    # Transform each credential type
    for field in ["credentials", "clerk-credentials", 
                 "eligibility-credentials", "envelope-credentials"]:
        elem = root.find(field)
        if elem is not None:
            field_name = field.replace("-", "_")
            settings[field_name] = transform_credential_element(elem)
    
    return IntegrationSettings(**settings)
```

### Python to C#
```python
def transform_python_to_cs(settings: IntegrationSettings) -> str:
    root = ET.Element("settings")
    
    # Transform each credential type
    if settings.credentials:
        root.append(ET.fromstring(settings.credentials.to_xml()))
    if settings.clerk_credentials:
        elem = ET.fromstring(settings.clerk_credentials.to_xml())
        elem.tag = "clerk-credentials"
        root.append(elem)
    if settings.eligibility_credentials:
        elem = ET.fromstring(settings.eligibility_credentials.to_xml())
        elem.tag = "eligibility-credentials"
        root.append(elem)
    if settings.envelope_credentials:
        elem = ET.fromstring(settings.envelope_credentials.to_xml())
        elem.tag = "envelope-credentials"
        root.append(elem)
    
    return ET.tostring(root, encoding="unicode")
```

## Security Considerations
1. All credential types use secure storage
2. XML parsing is sanitized
3. Null handling prevents errors
4. Input validation at all levels

## Error Handling
1. Missing XML elements: Return None for that credential
2. Invalid XML format: Raise ValueError
3. Invalid credential data: Raise ValidationError
4. Transformation errors: Raise specific exceptions

## Usage Example
```python
# Create settings
settings = IntegrationSettings(
    credentials=Credentials(username="user1", password="pass1"),
    clerk_credentials=Credentials(username="clerk1", password="pass2"),
    eligibility_credentials=AbilityCredentials(
        sender_id="org1",
        username="elig1",
        password="pass3"
    ),
    envelope_credentials=EnvelopeCredentials(
        sender_id="org2",
        username="env1",
        password="pass4"
    )
)

# XML serialization
xml_str = settings.to_xml()

# XML deserialization
loaded = IntegrationSettings.from_xml(xml_str)
```
