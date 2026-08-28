## Fast verification recipes

Run these against the repo before submitting (paths are examples; adapt):

```bash
# 2.1 / 5.1.1 — collect EVERY url in the listing/review-notes copy, then curl
# each as an anonymous visitor. Any non-200 (404, redirect-to-login, private repo)
# is a blocker. Run from the repo root.
grep -rhoE 'https?://[^ )"`>]+' appstore/ docs/APPSTORE*.md \
  | grep -vE 'developer\.apple\.com|apps\.apple\.com/account|archive\.org|microsoft|googleapis' \
  | sort -u | while read -r u; do
      code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 10 "$u")
      printf '%-55s %s\n' "$code" "$u"; done
#   → every line must be 200. Re-check the LIVE App Store Connect value too;
#     repo files and ASC drift apart after manual edits.
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

# 5.1 — claims "no data collected" but talks to the network?
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
