# §P. Performance and native feel

Read this before a performance pass, when an app "feels slow / not native", or before a
release. It covers React Native (Hermes, New Architecture) with native Kotlin/Swift owners,
and the services the app talks to. Pair it with `reference/verification.md` (§5) for gates
and with `web-perf-audit` for web pages and server transport.

## P0. Method: measure, verify the claim, fix, re-measure

1. **Baseline in numbers before touching code.** No number, no claim.
   - Android cold start: `adb shell am force-stop <pkg>` then
     `adb shell am start -W -n <pkg>/<activity>`. Use `TotalTime`, at least 3 runs,
     release build, and note the API level and device.
   - Connection reuse on a release build, where `run-as` is unavailable: sample the app's
     sockets with `adb shell cat /proc/net/tcp /proc/net/tcp6`. Filter on the app uid
     (`dumpsys package <pkg> | grep uid`) and remote port `:01BB`. Stable local ports
     across many requests mean reuse. New ports and TIME_WAIT (`06`) rows mean
     per-request handshakes.
   - Handshake cost against the real backend:
     `curl -w "tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}"`.
     Then fetch two URLs in one curl and compare (the second has `tls=0` when reused).
   - Protocol offered: `openssl s_client -alpn h2,http/1.1 -connect host:443` (look at
     `ALPN protocol:`).
2. **Treat every reviewer finding as a hypothesis**, whether it comes from a model or a
   human. Open the cited file:line and the library source it relies on before editing.
   Reviews mix real defects with confident claims that the platform behaves otherwise.
   Example: on Android, `HttpURLConnection.disconnect()` after the body was read to EOF and
   closed does **not** kill keep-alive. The bundled OkHttp has already released the
   connection to the pool, so `disconnect()` cancels nothing. Verify with the socket
   sampling above before "fixing" it.
3. **Get two independent reviews when stakes are high** (two different model families),
   then rank the union by impact ÷ effort. The overlap is usually right; the rest needs
   checking.
4. **Every fix gets a regression test that fails on the old code.** Prove it: stash the
   fix, run the test (red), restore (green).
5. **Re-measure the same way and report before → after.** Report "not measured" when that
   is the truth.

## P1. Transport (usually the largest real-world win)

- **One HTTP client per process (or per account epoch), never one per request.**
  - iOS: a new `URLSession` per request (then `invalidateAndCancel()`) pays TCP + TLS on
    every call. That is about 20 ms on a LAN and about 2 RTT (100–160 ms) on cellular.
  - Use one session with a router delegate keyed by `taskIdentifier`. Keep the per-request
    state object as the logical delegate, and end a request with `task.cancel()`, not
    session teardown.
  - Keep privacy settings on the shared config: `httpShouldSetCookies = false`,
    `httpCookieStorage = nil`, `urlCredentialStorage = nil`, `urlCache = nil`.
  - Refuse callbacks for tasks with no owner.
- Android `HttpURLConnection`: read the body to EOF and close the stream so the
  connection returns to the pool. `disconnect()` is for cancellation or abandoned bodies.
- **Check the server's ALPN before blaming the client.** HTTP/1.1-only servers cap
  parallelism at a handful of connections per host. Enabling h2 is a server change: test
  it against the heaviest real page first, because some stacks refuse streams under
  parallel load.

## P2. Startup

- Keep `Application.onCreate` / `didFinishLaunching` free of directory walks,
  `deleteRecursively`, `SharedPreferences.commit()` and cache sweeps.
  - To delete a whole directory, rename it to a trash sibling (O(1)) and remove it on a
    worker.
  - If a security rule requires synchronous removal, measure before changing anything.
- Lazy-require heavy JS modules (calling/WebRTC, viewers, editors). Keep `inlineRequires`.
- Android: report the real "first content" with `reportFullyDrawn()`. Play vitals flag cold starts ≥ 5 s, warm ≥ 2 s and hot ≥ 1.5 s. Replace init ContentProviders with App Startup or lazy init.
- iOS: do only first-screen work in `didFinishLaunching`. Avoid `+load` and static initialisers, and embed fewer dynamic frameworks. Apple counts main-thread stalls over 250 ms as hangs; under 100 ms is rarely noticed.
- Android: ship an app-generated Baseline Profile plus a Startup Profile. Library-merged profiles are not enough. Google cites about 30 % faster first launch. The gain on RN is unverified, since profiles do not cover Hermes bytecode. Consider a Baseline Profile (`androidx.profileinstaller` + Macrobenchmark
  `BaselineProfileRule`) covering launch and the top two journeys. Measure with
  Macrobenchmark; the gain for an RN host varies.

## P3. Lists and rendering (RN)

- Never leave FlatList windowing at defaults on heavy rows (default `windowSize` 21 keeps
  about 10 screens each side mounted). Rows with gesture handlers or animated styles
  should use `windowSize` 7–11, `initialNumToRender` ≈ one screen, and
  `maxToRenderPerBatch` 8–10. Re-check `scrollToIndex` paths and their
  `onScrollToIndexFailed`.
- Stable `renderItem` and stable `onViewableItemsChanged`. Changing the latter throws.
  Read changing values through refs or per-row subscriptions (`useSyncExternalStore`),
  not closure deps that change on every keystroke or scroll tick.
- Images in recycled cells: remember the measured aspect ratio per image id (number only,
  LRU of a few hundred) so remounts don't jump. Never cache private URIs in JS if a native
  owner manages them.
- Typing: one persist per keystroke at most. When several paths persist, skip identical
  snapshots and clear the "last saved" marker on write failure so a retry still happens.
  Debounce only with flushes on send/back/blur/background.
- Native image handle caches: a reused handle may live as long as its backing record stays
  fresh, and never longer. A short default lifetime (for example 60 s) silently
  re-decrypts and re-URIs every image each minute, which misses the platform image cache
  and flashes placeholders.

- Long, heterogeneous lists (feed, chat): consider FlashList v2. Drop the `estimated*` props and use `getItemType` and `useRecyclingState`. Shopify reports up to 50 % less blank area. Migrating is a real change: keep viewability, `maintainVisibleContentPosition` and scroll-to-index behaviour under test.
- React Compiler 1.0 (stable, Oct 2025): pin an exact version and lint with `eslint-plugin-react-hooks`. Components that write refs during render are skipped. Measure before keeping it.
- RN 0.84+ ships Hermes V1 by default. No official numbers have been published, so measure TTI and memory on your app before and after the upgrade.
- Reanimated: animate only `transform` and `opacity`. Keep to about 100 concurrently animated components on low-end Android. Turn on sync-props feature flags only after a measured regression on a release build.
- JS bundle: build a minified bundle with a source map, inspect it with `source-map-explorer`, and remove barrel imports. Record the size before and after.

## P4. Native feel checklist (both platforms)

- Android pull-to-refresh: `RefreshControl` needs `colors` and `progressBackgroundColor`.
  `tintColor` is iOS-only, so without them the spinner is a default arrow, wrong in dark
  mode.
- Android 13+ back with predictive back opted in (RN ≤ 0.83 at target 36):
  `ReactActivity.invokeDefaultOnBackPressed()` disables RN's own back callback and never
  re-enables it. After a root Back only backgrounds the task, the next Back skips JS.
  Register your own `OnBackPressedCallback` after `super.onCreate`; it disables itself
  around the fallback and re-enables in `finally`. Cover it with a host test of the
  callback order.
- iOS status-bar tap-to-top works only when exactly one scroll view in the window has
  `scrollsToTop`. With a custom navigator that keeps layers mounted, set it from focus and
  disable it on horizontal or nested scrollers. Verify on a simulator.
- Ship only the icon fonts you import. `react-native-vector-icons` copies all ~19 (≈ 3.8
  MB):
  - Android: keep only the used `.ttf` in `assets/fonts`.
  - iOS: trim the generated `Pods-<App>-resources*` files in a Podfile `post_integrate`
    hook, and list only used fonts in `UIAppFonts`.
  - Add a test that fails when a new family is imported without its font.
- Gestures that track a finger (image zoom, month swipe, back swipe) belong on the UI
  thread (Gesture Handler + Reanimated worklets). Finish a release using the gesture's
  velocity.

## P5. Platform parity before inventing behaviour

When a feature exists in an official client (read state, notification clearing,
badges), find how that client and its server actually do it: server handlers, the
installed web JS, or a decompiled APK. Prefer the server-side contract the official client
uses over client-side approximations. Example: a "content viewed" endpoint that both
records the view and clears exactly that item's notifications beats matching notification
tags in the app.

## P6. Backend the app depends on (PHP/nginx or similar)

- Compress JSON. nginx defaults are `gzip off` and `gzip_types text/html`. Add `application/json` and check a large authenticated response for `Content-Encoding`. Small bodies under `gzip_min_length` stay plain by design. OkHttp and URLSession decode gzip transparently; brotli needs an OkHttp add-on on Android.
- Use keep-alive to the app server where it is remote: `fastcgi_keep_conn on` plus an upstream `keepalive` block. The gain is small when PHP-FPM is local. Keep OPcache on.
- Transport checks (reuse, ALPN, caching) are in `web-perf-audit` → `sections/server-transport.md`.

## Sources (checked 2026-11; re-verify versions before quoting)

- Callstack agent skills (measure TTI, bundle analysis): https://github.com/callstackincubator/agent-skills
- Vercel agent skills (react-native-skills, react-best-practices): https://github.com/vercel-labs/agent-skills
- Android skills (`performance/r8-analyzer`): https://github.com/android/skills
- Baseline Profiles: https://developer.android.com/topic/performance/baselineprofiles/overview
- Launch time (Android): https://developer.android.com/topic/performance/issues/launch-time
- Hangs (Apple): https://developer.apple.com/documentation/xcode/understanding-hangs-in-your-app
- Launch time (Apple): https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time
- FlashList v2: https://shopify.engineering/flashlist-v2
- React Compiler 1.0: https://react.dev/blog/2025/10/07/react-compiler-1
- RN 0.84 (Hermes V1 default): https://reactnative.dev/blog/2026/02/11/react-native-0.84
- Reanimated performance: https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/
- nginx gzip / fastcgi: https://nginx.org/en/docs/http/ngx_http_gzip_module.html, https://nginx.org/en/docs/http/ngx_http_fastcgi_module.html

## Gate (add to §5.2 for a perf pass)

- [ ] Baseline and after numbers recorded with method, build type and device.
- [ ] Each fix verified against source before editing; rejected claims listed with the
      evidence.
- [ ] Regression test per fix, shown red on the old code.
- [ ] Full test suite, native host checks, and a full compile of both apps at HEAD.
