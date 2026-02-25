#!/usr/bin/env bash
set -e

# Detect container runtime
if command -v docker >/dev/null 2>&1; then
    RUNTIME="docker"
elif command -v podman >/dev/null 2>&1; then
    RUNTIME="podman"
else
    echo "Error: Neither docker nor podman is installed." >&2
    exit 1
fi

echo "Using container runtime: $RUNTIME"

# Build image
$RUNTIME image build --no-cache -t build-context -f - . <<'EOF'
FROM busybox
WORKDIR /build-context
COPY . .
CMD find .
EOF

# Run container
$RUNTIME container run --rm build-context