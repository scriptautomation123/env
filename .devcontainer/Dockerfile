FROM mcr.microsoft.com/devcontainers/java:1-21-bookworm

# Remove expired Yarn repository to prevent APT errors
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
