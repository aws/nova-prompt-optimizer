#!/bin/sh

# Docker entrypoint script for frontend container
# Handles environment variable substitution and nginx startup

set -e

# Function to substitute environment variables in files
substitute_env_vars() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "Substituting environment variables in $file"
        
        # Create a temporary file with environment variables substituted
        envsubst '${VITE_API_URL} ${VITE_WS_URL} ${VITE_APP_VERSION}' < "$file" > "${file}.tmp"
        mv "${file}.tmp" "$file"
    fi
}

# Substitute environment variables in JavaScript files
echo "Configuring application with environment variables..."
echo "API_URL: ${VITE_API_URL:-http://localhost:8000}"
echo "WS_URL: ${VITE_WS_URL:-ws://localhost:8000}"
echo "APP_VERSION: ${VITE_APP_VERSION:-1.0.0}"

# Find and process JavaScript files that might contain environment variables
find /usr/share/nginx/html -name "*.js" -type f | while read -r file; do
    # Only process files that contain placeholder patterns
    if grep -q "VITE_API_URL\|VITE_WS_URL\|VITE_APP_VERSION" "$file" 2>/dev/null; then
        substitute_env_vars "$file"
    fi
done

# Create runtime configuration file
cat > /usr/share/nginx/html/config.js << EOF
window.__APP_CONFIG__ = {
  API_URL: '${VITE_API_URL:-http://localhost:8000}',
  WS_URL: '${VITE_WS_URL:-ws://localhost:8000}',
  APP_VERSION: '${VITE_APP_VERSION:-1.0.0}',
  BUILD_TIME: '$(date -u +"%Y-%m-%dT%H:%M:%SZ")'
};
EOF

echo "Configuration complete. Starting nginx..."

# Execute the main command
exec "$@"