# Why this fork exists

`clix` is a genuinely good terminal client for X: cookie auth, no API keys, and output shaped for humans, scripts and AI agents. It stopped being maintained, and the way it stopped made the source effectively disappear. This fork keeps it working.

## The history

| Date | What happened |
| --- | --- |
| 2026-03-18 → 2026-03-24 | `clix0` 0.4.0 → 0.5.0 published to PyPI (0.4.2 tagged in git). |
| 2026-03-23 | Last functional commit in `dubious-pinetum918/clix`. Everything after it is README edits. |
| 2026-04-02 | `clix0` 0.5.1 published to PyPI — **never committed to git**. |
| 2026-05-01 → 2026-10-14 | Git `main` sits at 0.4.2 while PyPI ships 0.5.1. |
| (discovered) | The repository named in the PyPI metadata, `spideystreet/clix`, returns **404**. |

So the published package and the published source had drifted apart, and the only remaining pointer to the "real" source was dead. For anyone who wanted to fix `clix` rather than wait, 0.5.1 existed as exactly one thing: a wheel on PyPI.

## What this fork is

- `main` starts from the **source reconstructed out of the published `clix0 0.5.1` wheel**, imported as a single commit so the tree matches what people actually run.
- Everything on top of that is maintenance for X's frontend, which does not sit still.

## What broke, and what was fixed

X moved its web frontend from `responsive-web/client-web` bundles to Vite/Relay bundles under `abs.twimg.com/x-web/...`, and then stopped emitting `<script src>` tags for the entry bundle at all — it is now only named inside inline JavaScript as `entryHref="…/entry-client-logged-out-*.js"`. On top of that, X keeps adding required Relay variables to existing GraphQL operations.

Unfixed, that produced: `No JS bundle URLs found in X.com HTML`, a stale or empty endpoint cache, a failing cookie-validation check, `422 GRAPHQL_VALIDATION_FAILED: must be defined`, `followers: 0` on every profile, `trending` returning `[]`, and batch tweet fetches returning a list of GraphQL operation names instead of tweets.

Fixed here:

- **Bundle discovery** — finds the x-web entry from the inline `entryHref` bootstrap, walks the Vite asset graph, and starts the crawl from the entry bundle.
- **Crawl completeness** — the default cap went from 1000 to 7000 bundles. The old cap silently truncated the graph (~378 of ~720 operations) and dropped `BookmarkSearchTimeline` and user-timeline operations, so bookmarks and profiles failed with `Unknown GraphQL operation`.
- **Relay variable self-healing** — on a `must be defined` 422 the client reads the variable name out of the error's `path`, adds it (Relay feature flags as `true`, `rest_id`/`focalTweetId` as the tweet ID) and retries. X rotates these every few weeks; this survives rotations without a code change.
- **Response-shape drift** — profile counts from `relationship_counts`/`tweet_counts`, trends from `trending_explore_mixer_timeline`, and a per-ID `TweetDetail` fallback when the `TweetResultsByRestIds` batch operation is missing from the bundles.
- **Transient backend errors** — X's `Dependency: Unspecified` on jobs/explore is retried instead of raised.
- **MCP on SDK 2.x** — `FastMCP` was renamed to `MCPServer`; `clix mcp` loads again (47 tools).

## Install

```bash
uv tool install --editable git+https://github.com/robertung88/clix
```

Requires Python 3.11+. Cookie auth: `clix auth login`, verify with `clix doctor`.

## How it is maintained

- `pytest` — 249 offline tests, plus 3 live `@pytest.mark.integration` tests that hit X. CI runs the offline set on every push.
- `scripts/smoke_read_paths.sh` — 12 read-only commands end to end (feed, search, tweet, batch, user, user tweets, followers, bookmarks, trending, dm inbox, jobs, doctor).
- A nightly job checks the install, the endpoint cache and every read path. When something breaks it diagnoses the cause, fixes it, requires the tests and the smoke test to pass, and pushes.

Nothing here pretends to be the upstream project. The MIT license and the original copyright notice are untouched, and credit for the design belongs to the original authors.

## Upstream

- `dubious-pinetum918/clix` — frozen at 0.4.2.
- `spideystreet/clix` — named by PyPI, returns 404.
