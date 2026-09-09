## Fast verification recipes

Run these against the repo before submitting (paths are examples; adapt):

```bash
# 2.1 / 5.1.1 — collect EVERY URL in listing/review-notes copy and make the
# transport check fail closed. Run from the repo root; adapt the paths/exclusions.
set -euo pipefail
urls=$(mktemp); trap 'rm -f "$urls"' EXIT
rg -No 'https?://[^ )"`>]+' appstore/ docs/APPSTORE*.md \
  | grep -vE 'developer\.apple\.com|apps\.apple\.com/account|archive\.org|microsoft|googleapis' \
  | sort -u > "$urls"
test -s "$urls" || { echo 'FAIL: no listing URLs found; check paths'; exit 1; }

failed=0
while IFS= read -r url; do
  if ! result=$(curl --silent --show-error --fail --location --max-time 10 \
      --output /dev/null \
      --write-out 'status=%{http_code} final=%{url_effective} type=%{content_type}' \
      "$url"); then
    printf 'FAIL transport  %s\n' "$url" >&2; failed=1; continue
  fi
  case "$result" in
    status=2*) printf 'OK transport    %s  source=%s\n' "$result" "$url" ;;
    *)         printf 'FAIL status      %s  source=%s\n' "$result" "$url" >&2; failed=1 ;;
  esac
done < "$urls"
test "$failed" -eq 0
# For EVERY "OK transport" result, open its reported final= URL in a fresh private
# browser session with no account/cookies. Record that the expected public page loads
# anonymously and review its content; a 2xx response can still be a login page, generic
# landing page, or API payload. Re-check the LIVE App Store Connect values as well.
```

```bash
# 3.1.1 — is there a Restore control NOT gated behind purchase state?
grep -rn "Restore purchases\|AppStore.sync\|restorePurchases" ios/ --include="*.swift"
#   → expect a button in Settings gated only on the IAP flag, plus an always-visible paywall section.

# 2.3.1 / 2.5 — every QA/launch-arg hook must be inside #if DEBUG
grep -rn "ProcessInfo.processInfo.arguments\|CommandLine\|-ui[A-Z]" ios/ --include="*.swift"
#   → each must sit within a #if DEBUG ... #endif; the vars they set default to inert.

# entitlements — nothing the app isn't approved for (e.g. AlarmKit, critical alerts, push)
find ios -name "*.entitlements" -not -path "*/build/*" -exec cat {} \;

# 5.1 — inventory possible data flows and third-party SDKs. This is not proof that
# data is "collected"; compare actual behavior, vendor docs, and privacy manifests
# with the App Store Connect answers.
grep -rn "URLSession\|URLRequest\|Alamofire\|analytics\|firebase\|amplitude\|mixpanel" ios/ --include="*.swift" | grep -v build/

# 4.5.4 / background — BG task ids in code must be declared in Info.plist
grep -rn "BGTaskScheduler\|register(forTaskWithIdentifier" ios/ --include="*.swift"
#   → cross-check each id against Info.plist BGTaskSchedulerPermittedIdentifiers + UIBackgroundModes.

# Info.plist — only the usage strings you actually use
plutil -p ios/<AppName>/App/Info.plist | grep -i "UsageDescription\|BackgroundModes\|BGTaskScheduler"
```

For UI affordances, **drive the real states** (don't trust static reads):
fresh install → mid-trial → **post-purchase** → trial-ended. The Restore button
must be visible and working in all four.

---
