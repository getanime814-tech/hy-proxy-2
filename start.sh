#!/bin/bash

echo "Starting Cloudflare WARP setup..."

# WARP রেজিস্ট্রেশন এবং প্রক্সি মোডে চালু করা
warp-cli --accept-tos registration new || true
warp-cli --accept-tos mode proxy
warp-cli --accept-tos proxy port 40000
warp-cli --accept-tos connect

echo "Waiting for WARP to establish connection..."
# WARP কানেক্ট হয়েছে কিনা চেক করার লুপ (সর্বোচ্চ ৩০ সেকেন্ড)
for i in {1..15}; do
    if curl -s --socks5-hostname 127.0.0.1:40000 "https://cloudflare.com/cdn-cgi/trace" | grep -qE "warp=(plus|on)"; then
        echo "✅ WARP is active and routing traffic."
        break
    fi
    echo "Waiting for WARP... ($i/15)"
    sleep 2
done

echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
