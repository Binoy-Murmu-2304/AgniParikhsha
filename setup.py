import os
import sys
import setuptools

setuptools.setup(
    name="agnipariksha-sdk",
    version="2.0.0",
    author="AgniPariksha Engineering Team - SIH 2026",
    description="Python SDK for ISRO ATE Hardware Ingestion & AgniPariksha Real-Time Reliability API",
    py_modules=["agnipariksha_sdk"],
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
