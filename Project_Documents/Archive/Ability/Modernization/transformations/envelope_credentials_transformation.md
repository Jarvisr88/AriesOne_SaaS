# EnvelopeCredentials Transformation Rules

## Overview
This document defines the transformation rules for converting the C# `EnvelopeCredentials` class to Python.

## Source (C#)
```csharp
namespace DMEWorks.Ability
{
    [XmlType(AnonymousType=true)]
    public class EnvelopeCredentials
    {
        [XmlElement("sender-id")]
        public string SenderId { get; set; }

        [XmlElement("username")]
        public string Username { get; set; }

        [XmlElement("password")]
        public string Password { get; set; }
    }
}
```

## Target (Python)
```python
class EnvelopeCredentials(Credentials):
    sender_id: str = Field(..., alias="sender-id")
```

## Field Mappings

### SenderId
- Source: `SenderId` (string)
- Target: `sender_id` (str)
- XML: `sender-id`
- Validation:
  - Min length: 3
  - Max length: 50
  - Pattern: `^[A-Za-z0-9_-]+$`
- Transformation:
  - Strip whitespace
  - Validate against pattern
  - Raise ValueError if invalid

### Inherited Fields
- Username and Password inherited from base Credentials class
- Same validation and transformation rules apply

## XML Transformation

### C# to Python
```python
def transform_cs_to_python(xml_str: str) -> EnvelopeCredentials:
    root = ET.fromstring(xml_str)
    return EnvelopeCredentials(
        sender_id=root.find("sender-id").text,
        username=root.find("username").text,
        password=root.find("password").text
    )
```

### Python to C#
```python
def transform_python_to_cs(credentials: EnvelopeCredentials) -> str:
    root = ET.Element("EnvelopeCredentials")
    sender_id = ET.SubElement(root, "sender-id")
    sender_id.text = credentials.sender_id
    username = ET.SubElement(root, "username")
    username.text = credentials.username
    password = ET.SubElement(root, "password")
    password.text = credentials.password.get_secret_value()
    return ET.tostring(root, encoding="unicode")
```

## Security Considerations
1. Inherits security features from base Credentials
2. Sender ID validation prevents injection
3. XML serialization handles special characters
4. Input validation enforces security

## Error Handling
1. Invalid sender ID format: Raise ValueError with description
2. Inherited error handling from Credentials
3. XML parsing errors: Raise ValueError with details
4. Missing required fields: Raise ValidationError

## Usage Example
```python
# Create envelope credentials
credentials = EnvelopeCredentials(
    sender_id="org-123",
    username="john.doe",
    password="SecurePass123!"
)

# XML serialization
xml_str = credentials.to_xml()

# XML deserialization
loaded = EnvelopeCredentials.from_xml(xml_str)
```
