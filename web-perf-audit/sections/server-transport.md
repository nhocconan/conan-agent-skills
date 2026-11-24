# Server transport

Measure from the client's side before changing code. These checks also apply to API backends that native apps call.
- **Handshake cost and reuse**: `curl -w "tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}" URL URL`. The second URL on the same connection should show `tls=0`; if it doesn't, keep-alive is off.
- **Protocol**: `openssl s_client -alpn h2,http/1.1 -connect host:443` → `ALPN protocol:`. HTTP/1.1-only limits a page to about 6 parallel requests per host. Before enabling h2 on a stack that serves many small bundles, load-test it with the heaviest real page, since some backends refuse streams under parallel load.
- **Compression**: compare `curl -sI -H 'Accept-Encoding: br, gzip'` against the raw size. Serve brotli (or zstd where clients support it) for text assets; precompress static files at build time.
- **Caching**: hashed static assets get `Cache-Control: public, max-age=31536000, immutable`. HTML and API responses get validators (`ETag`/`Last-Modified`), never a long max-age.
- **Payload weight**: find assets of 1 MB or more on the critical path (for example a full UI framework CSS when only a login form renders). Remove them from that page.
- Record before and after numbers for each change, and keep a rollback of the server config. A transport change affects every client at once.
