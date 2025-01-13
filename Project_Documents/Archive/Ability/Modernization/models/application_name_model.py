"""
ApplicationName Enum Module
This module defines the ApplicationName enum for the application.
Modernized from C# enum in DMEWorks.Ability.Common namespace.
"""
from enum import Enum

class ApplicationName(str, Enum):
    """
    Enumeration of valid application names.
    Inherits from str to ensure proper serialization.
    Equivalent to the C# enum with XmlType attribute.
    """
    DDE = "DDE"
    PPTN = "PPTN"
    CSI = "CSI"

    @classmethod
    def values(cls) -> list:
        """Returns a list of all valid application names"""
        return [member.value for member in cls]
