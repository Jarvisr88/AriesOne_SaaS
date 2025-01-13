"""
LineOfBusiness Enum Module
This module defines the LineOfBusiness enum for the application.
Modernized from C# enum in DMEWorks.Ability.Common namespace.
"""
from enum import Enum
from typing import List, Dict

class LineOfBusiness(str, Enum):
    """
    Enumeration of valid lines of business in the Medicare/Healthcare system.
    Inherits from str to ensure proper serialization.
    
    Attributes:
        PART_A: Medicare Part A services (hospital insurance)
        HHH: Home Health and Hospice services
        PART_B: Medicare Part B services (medical insurance)
        DME: Durable Medical Equipment services
        RURAL_HEALTH: Rural Health services
        FQHC: Federally Qualified Health Center services
        SECTION_1011: Emergency health services for undocumented aliens
        MUTUAL: Mutual of Omaha insurance services
        INDIAN_HEALTH: Indian Health Services
    """
    PART_A = "PartA"
    HHH = "HHH"
    PART_B = "PartB"
    DME = "DME"
    RURAL_HEALTH = "RuralHealth"
    FQHC = "FQHC"
    SECTION_1011 = "Section1011"
    MUTUAL = "Mutual"
    INDIAN_HEALTH = "IndianHealth"

    @classmethod
    def values(cls) -> List[str]:
        """
        Get all valid line of business values.
        
        Returns:
            List[str]: List of valid line of business values
        """
        return [member.value for member in cls]

    @classmethod
    def descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all lines of business.
        
        Returns:
            Dict[str, str]: Mapping of line of business values to descriptions
        """
        return {
            cls.PART_A.value: "Medicare Part A (Hospital Insurance)",
            cls.HHH.value: "Home Health and Hospice Services",
            cls.PART_B.value: "Medicare Part B (Medical Insurance)",
            cls.DME.value: "Durable Medical Equipment Services",
            cls.RURAL_HEALTH.value: "Rural Health Services",
            cls.FQHC.value: "Federally Qualified Health Centers",
            cls.SECTION_1011.value: "Emergency Health Services (Section 1011)",
            cls.MUTUAL.value: "Mutual of Omaha Insurance Services",
            cls.INDIAN_HEALTH.value: "Indian Health Services"
        }

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the line of business
        """
        return f"<LineOfBusiness>{self.value}</LineOfBusiness>"

    @classmethod
    def from_xml(cls, xml_str: str) -> "LineOfBusiness":
        """
        Create LineOfBusiness from XML string.
        
        Args:
            xml_str (str): XML representation of line of business
            
        Returns:
            LineOfBusiness: New line of business instance
            
        Raises:
            ValueError: If XML is invalid or value is not a valid line of business
        """
        try:
            # Simple parsing since format is known
            value = xml_str.replace("<LineOfBusiness>", "").replace("</LineOfBusiness>", "")
            return cls(value.strip())
        except ValueError as e:
            raise ValueError(f"Invalid line of business XML: {e}")
