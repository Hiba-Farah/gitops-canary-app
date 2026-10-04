from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest
import os
import random
import socket
import time

app = FastAPI()

VERSION = os.getenv("APP_VERSION", "v1")
FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))
HOSTNAME = socket.gethostname()

REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency")

THEMES = {
    "v1": {"accent": "#3b82f6", "glow": "rgba(59,130,246,0.35)", "label": "Stable"},
    "v2": {"accent": "#10b981", "glow": "rgba(16,185,129,0.35)", "label": "Canary"},
}

CUBE_SVG = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M36 6L64 21V51L36 66L8 51V21L36 6Z" stroke="{accent}" stroke-width="2" fill="{accent}" fill-opacity="0.08"/>
<path d="M36 6V36M36 36L64 21M36 36L8 21M36 36V66" stroke="{accent}" stroke-width="2"/>
</svg>
"""

def render_page():
    t = THEMES.get(VERSION, THEMES["v1"])
    cube = CUBE_SVG.format(accent=t["accent"])
    return f"""
    <html>
    <head>
        <title>Canary Demo — {VERSION}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #0a0e1a;
                background-image: radial-gradient({t['glow']} 0%, transparent 60%);
                background-position: center -100px;
                font-family: 'SF Mono', 'Segoe UI', monospace, sans-serif;
                color: #e2e8f0;
            }}
            .card {{
                background: #11162664;
                border: 1px solid #1e293b;
                border-radius: 16px;
                padding: 44px 52px;
                max-width: 420px;
                width: 90%;
                text-align: center;
                box-shadow: 0 0 0 1px #ffffff08, 0 20px 50px rgba(0,0,0,0.5);
            }}
            .status-row {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-bottom: 24px;
            }}
            .dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {t['accent']};
                box-shadow: 0 0 8px {t['accent']};
            }}
            .status-text {{
                font-size: 0.75rem;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: {t['accent']};
                font-weight: 600;
            }}
            h1 {{
                font-size: 3rem;
                font-weight: 700;
                margin: 16px 0 4px;
                letter-spacing: -1px;
                color: #f8fafc;
            }}
            p.sub {{
                color: #64748b;
                font-size: 0.9rem;
                margin-bottom: 28px;
            }}
            .divider {{
                height: 1px;
                background: #1e293b;
                margin: 24px 0;
            }}
            .meta {{
                display: flex;
                flex-direction: column;
                gap: 10px;
                text-align: left;
            }}
            .meta-row {{
                display: flex;
                justify-content: space-between;
                font-size: 0.8rem;
            }}
            .meta-label {{
                color: #64748b;
            }}
            .meta-value {{
                color: #e2e8f0;
                font-weight: 600;
                max-width: 220px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            {cube}
            <div class="status-row" style="margin-top:20px">
                <div class="dot"></div>
                <div class="status-text">{t['label']} · running</div>
            </div>
            <h1>{VERSION.upper()}</h1>
            <p class="sub">gitops-canary-app</p>
            <div class="divider"></div>
            <div class="meta">
                <div class="meta-row">
                    <span class="meta-label">Served by pod</span>
                    <span class="meta-value">{HOSTNAME}</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Deployment strategy</span>
                    <span class="meta-value">Argo Rollouts</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Traffic managed by</span>
                    <span class="meta-value">NGINX Ingress</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/")
def root():
    start = time.time()
    if random.random() < FAIL_RATE:
        REQUEST_COUNT.labels(status="500").inc()
        REQUEST_LATENCY.observe(time.time() - start)
        return Response(content="Internal error", status_code=500)

    REQUEST_COUNT.labels(status="200").inc()
    REQUEST_LATENCY.observe(time.time() - start)
    return Response(content=render_page(), media_type="text/html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")# trigger Sat Oct  3 23:36:01 +00 2026
# retest Sat Oct  3 23:50:45 +00 2026
# retest with relaxed threshold Sun Oct  4 00:10:39 +00 2026
# retest with 20pct initial weight Sun Oct  4 00:27:29 +00 2026
# retest with traffic confirmed Sun Oct  4 09:37:58 +00 2026
