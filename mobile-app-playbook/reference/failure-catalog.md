## §9. Failure catalog — generalized scars (why half these rules exist)

| Failure (real, generalized) | Rule it produced |
| --- | --- |
| Six "green" build stages; nothing had compiled (SDK missing; exit code was `tail`'s) | §5.1 never pipe builds; check exit code + positive marker |
| JVM tests green, iOS won't link (`java.lang.*` in shared code) | §1.2 iOS link task in every stage gate |
| CMP iOS app crashed at launch (missing frame-duration plist key) | §1.2 iOS host minimum |
| Play rejection: Families ad-format violation after audience declaration drifted from ad config | §4.2 declaration ⇔ code ⇔ rating must agree, decided up front |
| Every real token payment rejected: code assumed 9 decimals, asset had 6 | §4.3 verify decimals against the authoritative source |
| Paying users couldn't restore after account-system migration (v1 rows not mapped to v2) | §4.3 restore matrix includes schema-migration case |
| Interstitial covered the result screen on the same frame | §2.2 ad never races result UI |
| Daily challenge unfair: obstacle IDs differed between two runs of the same engine | §5.5 determinism is a CI assertion |
| "Impossible" levels shipped; players stuck at median-death-zero | §5.4 bot-verified difficulty invariants |
| Docs gave store-console menu paths from memory; console had been redesigned | §6 verify nav against current docs + deep link + search fallback |
| Declared a policy URL "dead, needs infra work" after curling the wrong host | §6 curl the URL actually declared in the console |
| Screenshots grabbed mid-entrance-animation looked broken | §5.3 behavior checks wait for settle; know your UI's timing |

---
