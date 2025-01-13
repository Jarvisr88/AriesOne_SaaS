# CmnRequestSearchCriteria Mapping

## Source: C#
- **NPI**: string
- **HIC**: string
- **HCPCS**: string
- **MBI**: string
- **MaxResults**: int

## Target: Python (Pydantic)
- **npi**: Optional[str]
- **hic**: Optional[str]
- **hcpcs**: Optional[str]
- **mbi**: Optional[str]
- **max_results**: Optional[int]

## Notes
- The `npi`, `hic`, `hcpcs`, and `mbi` fields are optional strings in Python.
- The `max_results` field is an optional integer in Python.
