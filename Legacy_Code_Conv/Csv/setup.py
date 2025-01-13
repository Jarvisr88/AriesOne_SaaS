"""
Setup configuration for CSV module
"""
from setuptools import setup, find_packages

setup(
    name="ariesone-csv",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.3",
        "numpy>=1.24.3",
        "psutil>=5.9.5"
    ],
    extras_require={
        'test': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=4.1.0'
        ],
        'dev': [
            'black>=23.7.0',
            'pylint>=2.17.5',
            'mypy>=1.5.1'
        ]
    },
    python_requires='>=3.8',
    author="OB-1",
    author_email="ob1@ariesone.com",
    description="High-performance CSV processing module with validation and caching",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="csv, data processing, validation, caching",
    url="https://github.com/ariesone/csv-module",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General"
    ],
    entry_points={
        'console_scripts': [
            'csv-validate=csv_validator:main',
            'csv-profile=csv_profiler:main'
        ]
    }
)
