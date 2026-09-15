"""
AgniPariksha 2.4 — Safe ATE Integration SDK
==========================================
Non-invasive, read-only analytics SDK for semiconductor and aerospace test environments.
"""

from agnipariksha_sdk.client import AgniParikshaClient
from agnipariksha_sdk.schema import SDKMeasurementRecord, SDKAnalysisResult

# Backward compatibility alias
AgniParikshaATESDK = AgniParikshaClient

__version__ = "2.4.0-safe-ate"
__all__ = ["AgniParikshaClient", "AgniParikshaATESDK", "SDKMeasurementRecord", "SDKAnalysisResult"]
