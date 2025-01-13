# Credentials Transformation Rules

## Overview
This document defines the transformation rules for converting the C# `Credentials` class to Python.

## Source (C#)
```csharp
namespace DMEWorks.Ability
{
    [XmlType(AnonymousType=true)]
    public class Credentials
    {
        [XmlElement("username")]
        public string Username { get; set; }

        [XmlElement("password")]
        public string Password { get; set; }
    }
}
```

## Target (Python)
```python
class Credentials(BaseModel):
    username: str = Field(...)
    password: SecretStr = Field(...)
```

## Field Mappings

### Username
- Source: `Username` (string)
- Target: `username` (str)
- Validation:
  - Min length: 3
  - Max length: 50
  - Pattern: `^[A-Za-z0-9_@.-]+$`
- Transformation:
  - Strip whitespace
  - Validate against pattern
  - Raise ValueError if invalid

### Password
- Source: `Password` (string)
- Target: `password` (SecretStr)
- Validation:
  - Min length: 8
  - Must contain: uppercase, lowercase, number, special char
  - Pattern: `^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$`
- Transformation:
  - Convert to SecretStr for security
  - Validate complexity
  - Raise ValueError if invalid

## XML Transformation

### C# to Python
```python
def transform_cs_to_python(xml_str: str) -> Credentials:
    root = ET.fromstring(xml_str)
    return Credentials(
        username=root.find("username").text,
        password=root.find("password").text
    )
```

### Python to C#
```python
def transform_python_to_cs(credentials: Credentials) -> str:
    root = ET.Element("Credentials")
    username = ET.SubElement(root, "username")
    username.text = credentials.username
    password = ET.SubElement(root, "password")
    password.text = credentials.password.get_secret_value()
    return ET.tostring(root, encoding="unicode")
```

## Security Considerations
1. Password is stored as SecretStr to prevent exposure
2. XML serialization removes sensitive data from string representations
3. Input validation prevents injection attacks
4. Password complexity rules enforce security

## Error Handling
1. Invalid username format: Raise ValueError with description
2. Invalid password complexity: Raise ValueError with requirements
3. XML parsing errors: Raise ValueError with details
4. Missing required fields: Raise ValidationError

## Usage Example
```python
# Create credentials
credentials = Credentials(
    username="john.doe",
    password="SecurePass123!"
)

# XML serialization
xml_str = credentials.to_xml()

# XML deserialization
loaded = Credentials.from_xml(xml_str)
```
