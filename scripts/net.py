"""One HTTP helper for every script: urllib first, curl as a fallback (some hosts fail
Python's certificate store on macOS). Standard library only."""
import subprocess
import urllib.error
import urllib.request

UA = "Stratum/1.0 (https://github.com/ejhong/stratum)"


class HTTPError(Exception):
    def __init__(self, code):
        super().__init__(f"HTTP {code}")
        self.code = code


def fetch(url, accept="application/json", timeout=30, method="GET", tries=4):
    """Return (content_type, body_bytes). Retries politely on 429/503 (APIs rate-limit parallel
    agents); raises HTTPError(code) on other HTTP errors."""
    import time
    for attempt in range(tries):
        try:
            return _fetch(url, accept, timeout, method)
        except HTTPError as e:
            if e.code not in (429, 503) or attempt == tries - 1:
                raise
            time.sleep(3 * 2 ** attempt)


def _fetch(url, accept, timeout, method):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        raise HTTPError(e.code)
    except urllib.error.URLError as e:
        if "CERTIFICATE" not in str(e):
            raise
    head = ["-I"] if method == "HEAD" else []
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", UA, "-H", f"Accept: {accept}",
                          "-w", "\n%{http_code} %{content_type}", *head, url], capture_output=True)
    body, _, tail = out.stdout.rpartition(b"\n")
    code, _, ctype = tail.decode().partition(" ")
    if not code.isdigit() or int(code) >= 400:
        raise HTTPError(int(code) if code.isdigit() else 0)
    return ctype, body
