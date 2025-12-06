FROM alpine:3.19

ARG XRAY_VERSION=latest

RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    wget \
    unzip \
    && mkdir -p /var/log/xray /etc/xray

RUN ARCH=$(uname -m) \
    && if [ "$ARCH" = "x86_64" ]; then ARCH="64"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64-v8a"; fi \
    && wget -O /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-${ARCH}.zip" \
    && unzip /tmp/xray.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/xray \
    && rm /tmp/xray.zip

WORKDIR /etc/xray

EXPOSE 443

ENTRYPOINT ["/usr/local/bin/xray"]
CMD ["run", "-config", "/etc/xray/config.json"]
