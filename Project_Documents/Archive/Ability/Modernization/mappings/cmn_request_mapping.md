# CmnRequest Mapping

## Source: C#
- **MedicareMainframe**: DMEWorks.Ability.Common.MedicareMainframe
- **SearchCriteria**: CmnRequestSearchCriteria
- **MockResponse**: bool

## Target: Python (Pydantic)
- **medicare_mainframe**: Optional['MedicareMainframe']
- **search_criteria**: Optional[CmnRequestSearchCriteria]
- **mock_response**: Optional[bool]

## Notes
- The `MedicareMainframe` class needs to be defined separately in Python.
- The `search_criteria` field maps to the `CmnRequestSearchCriteria` Pydantic model.
- The `mock_response` field is a direct mapping from C# to Python.
