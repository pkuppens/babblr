#!/bin/bash
# Prevent direct commits to the main branch

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "main" ]; then
    echo "ERROR: Direct commits to main branch are not allowed."
    echo "Create a feature branch first:"
    echo "  git checkout -b feature/your-feature-name"
    exit 1
fi

exit 0
