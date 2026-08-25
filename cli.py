#!/usr/bin/env python3
"""
CLI for Glasgow-Blatchford Bleeding Score (GBS).
Pre-endoscopy risk stratification for upper GI bleeding.
"""
import sys
from glasgow_blatchford import main

if __name__ == "__main__":
    sys.exit(main())
