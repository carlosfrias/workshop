# coms-net Hub Server — Docker Image
# 
# Build:  docker build -t coms-net-hub:latest .
# Run:    docker compose up -d
#
# Base: oven/bun (official Bun runtime)

FROM oven/bun:1.2-slim AS base

LABEL org.opencontainers.image.title="coms-net-hub"
LABEL org.opencontainers.image.description="Cross-node pi communication HTTP/SSE hub"

# ---- Build stage ----
FROM base AS build
WORKDIR /build
COPY server/coms-net-server.ts .
# Verify the file compiles (no external deps needed — pure Bun + Node builtins)
RUN bun build --target=bun --outdir=/app coms-net-server.ts

# ---- Production stage ----
FROM base AS production
WORKDIR /app

# Copy compiled server
COPY --from=build /app/coms-net-server.js .

# Create non-root user
RUN groupadd -r comsnet && useradd -r -g comsnet -d /home/comsnet comsnet && \
    mkdir -p /home/comsnet/.pi/coms-net && \
    chown -R comsnet:comsnet /home/comsnet /app

USER comsnet

# State volume (persists across container restarts)
VOLUME ["/home/comsnet/.pi/coms-net"]

# Environment variables (overridable at runtime)
ENV PI_COMS_NET_HOST="0.0.0.0"
ENV PI_COMS_NET_PORT="8080"
ENV PI_COMS_NET_PROJECT="lab"

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD ["bun", "-e", "fetch('http://localhost:8080/health').then(r => r.ok ? process.exit(0) : process.exit(1))"]

ENTRYPOINT ["bun", "run", "coms-net-server.js"]
