"""API tests send requests directly and do not open Chrome.

Shared API fixtures belong in this file. The insufficient-balance test builds
its own headers and params, then calls execute_request.
"""
