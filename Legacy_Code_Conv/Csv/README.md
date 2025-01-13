# AriesOne CSV Module

A high-performance CSV processing module with validation, caching, and profiling capabilities.

## Features

- Efficient CSV file processing with streaming support
- Robust validation system with customizable rules
- Memory-efficient caching mechanism
- Performance profiling and monitoring
- Comprehensive error handling
- Async/await support
- Thread-safe operations

## Installation

```bash
pip install ariesone-csv
```

## Quick Start

```python
from csv_reader import CSVReader
from csv_validator import CSVValidator, ValidationRule, is_numeric
from csv_profiler import CSVProfiler

# Create validator with rules
validator = CSVValidator()
validator.add_rule(ValidationRule(
    field_name='id',
    validator=is_numeric,
    error_message='ID must be numeric'
))

# Create profiler
profiler = CSVProfiler()

# Create reader with validation and profiling
reader = CSVReader(
    validator=validator,
    profiler=profiler,
    chunk_size=1000
)

# Read and process CSV file
df = reader.read_file('data.csv')

# Get performance metrics
metrics = profiler.get_metrics('read_file')
print(f"Processed {metrics.rows_processed} rows in {metrics.duration_seconds:.2f} seconds")
```

## Documentation

- [User Guide](docs/user_guide.md)
- [API Reference](docs/api.md)
- [Deployment Guide](deployment/README.md)
- [Test Documentation](tests/README.md)

## Requirements

- Python 3.8+
- pandas 2.0.3+
- numpy 1.24.3+
- psutil 5.9.5+

## Development

```bash
# Clone repository
git clone https://github.com/ariesone/csv-module.git
cd csv-module

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact [support@ariesone.com](mailto:support@ariesone.com) or open an issue on GitHub.
