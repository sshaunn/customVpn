FROM alpine:3.19

ARG SS_VERSION=v1.21.2

RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    wget \
    xz

RUN ARCH=$(uname -m) \
    && if [ "$ARCH" = "x86_64" ]; then ARCH="x86_64-unknown-linux-musl"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="aarch64-unknown-linux-musl"; fi \
    && wget -O /tmp/ss.tar.xz "https://github.com/shadowsocks/shadowsocks-rust/releases/download/${SS_VERSION}/shadowsocks-${SS_VERSION}.${ARCH}.tar.xz" \
    && tar -xf /tmp/ss.tar.xz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/ssserver \
    && rm /tmp/ss.tar.xz

RUN adduser -D -s /sbin/nologin -u 1000 shadowsocks \
    && mkdir -p /etc/shadowsocks \
    && chown -R shadowsocks:shadowsocks /etc/shadowsocks

USER shadowsocks

WORKDIR /etc/shadowsocks

EXPOSE 8388

ENTRYPOINT ["/usr/local/bin/ssserver"]
CMD ["-c", "/etc/shadowsocks/config.json"]
