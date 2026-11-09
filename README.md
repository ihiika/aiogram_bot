# Concurrent Search Telegram Bot

A Telegram bot built with **aiogram 3** that takes a text query and searches
three public sources at the same time: **Wikipedia**, **GitHub** and
**Stack Overflow**. Results from all sources are merged into one unified
format and sent back to the user. If one source fails, the others still
respond.

## Requirements

- Python 3.12 or newer (developed and tested on Python 3.14)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Features

- Free-text search: send any message to the bot and get results from all sources.
- Three search providers, each in its own module:
  - Wikipedia (MediaWiki API): title and a cleaned text snippet
  - GitHub (repository search): description, stars and main language
  - Stack Overflow (Stack Exchange API): score, number of answers and a mark
    for questions that have an accepted answer
- A unified `SearchResult` dataclass: `title`, `description`, `url`, `source`.
- Concurrent search with `asyncio.gather`, plus a sequential version kept for
  timing comparison.
- Partial failure handling: a failing provider does not break the whole search.
- Timeouts: a slow provider is cut off and reported as unavailable, the others
  still respond.
- Per-source concurrency limits with `asyncio.Semaphore`, so many users at once
  do not flood the external sites.
- Basic input validation (empty messages) and error logging.
- Type hints across the codebase.

## Project structure

```
.
├── bot.py                     # aiogram bot: handlers and entry point
├── config.py                  # timeout constants
├── models.py                  # SearchResult and SearchOutcome dataclasses
├── search_service.py          # search_all (concurrent), search_all_sequential
├── providers/
│   ├── wikipedia.py           # Wikipedia provider
│   ├── github.py              # GitHub provider
│   └── stackoverflow.py       # Stack Overflow provider
├── scripts/
│   ├── benchmark.py           # timing: concurrent vs sequential
│   └── load_test.py           # load test of the per-source semaphores
├── requirements.txt           # dependencies
└── token.env.example          # example of the environment file
```

## Setup

1. Clone the repository and create a virtual environment:

   ```bash
   git clone https://github.com/ihiika/aiogram_bot.git
   cd aiogram_bot
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a bot with [@BotFather](https://t.me/BotFather) and put its token into
   a file named `token.env` (copy `token.env.example`):

   ```
   BOT_TOKEN=your-token-here
   ```

   `token.env` is listed in `.gitignore`. **Never commit a real token.**

4. Run the bot:

   ```bash
   python bot.py
   ```

Send the bot any text, for example `git`, and it replies with results from
Wikipedia, GitHub and Stack Overflow.

## How it works

Each provider is an `async` function that takes a query string and returns a
list of `SearchResult` objects. It sends an HTTP request with `httpx`, checks
the response, cleans the data (for example, HTML tags in Wikipedia snippets) and
maps it to `SearchResult`.

Source-specific extra data (GitHub stars and language, Stack Overflow score,
answer count and the accepted-answer mark) is built by the provider itself and
put into the `description` text, so the bot does not need to know anything about
individual sources. Fields that the API does not return are simply left out:
no `None` or empty separators appear in the reply.

The providers are registered in the `DICT_OF_SOURCES` dictionary in
`search_service.py` (source name -> provider function). To add a source, write a
new provider and add it to the dictionary.

`search_service.search_all(query)` starts all registered providers at once with
`asyncio.gather` and returns a `SearchOutcome`:

- `results`: a flat list of `SearchResult` from the providers that responded;
- `failed_sources`: names of the providers that raised an error;
- `total_sources`: how many providers were queried;
- `all_failed`: a property, `True` when every provider failed.

`search_all_sequential(query)` calls the three providers one after another and
exists only for timing comparison. It lists the providers by hand and does not
use `DICT_OF_SOURCES`.

## Handling failures

`asyncio.gather` is called with `return_exceptions=True`, so an exception in one
provider is returned as a value instead of cancelling the others. Each failure
is logged with the provider name and the error. The bot then answers depending
on the situation:

| Situation | Bot reply |
|---|---|
| Results found, all sources responded | The results |
| Results found, some sources failed | The results and an `Unavailable: ...` line |
| No results, some sources failed | A note that nothing was found and which sources are unavailable |
| No results, all sources responded | `No results found` |
| All sources failed | `All sources failed. Try again later` |

## Timeouts

A slow source must not delay the others, so there are two layers of limits.
All values live in `config.py`:

- **`httpx.Timeout`** in every provider: explicit `connect` and `read` limits
  (plus a default for `write` and `pool`). When one fires, `httpx` raises a
  specific error (for example `ReadTimeout`), so the log shows which phase of
  the request was slow.
- **`asyncio.wait_for`** around each provider call in `search_all`
  (`PROVIDER_TIMEOUT`). It is a hard cap on the whole provider call and acts as
  a safety net, for example when a server sends data very slowly and the
  `httpx` limits never fire.

The `httpx` limits are lower than `PROVIDER_TIMEOUT`, so the more informative
`httpx` error normally fires first. The log line for a timeout contains the
exception itself: `ReadTimeout` means an `httpx` limit fired, a bare
`TimeoutError` means the `wait_for` cap fired. The cap is applied to each provider
separately, not to the whole `gather`: if one provider times out, the results
of the others are kept. A provider that timed out is logged and listed in
`Unavailable: ...` like any other failed source.

## Concurrency limits (Semaphore)

Many users can search at the same time, and every search sends one request to
each source. Without a limit, 100 simultaneous users would send 100 requests to
every site at once. The sources, not the bot, are the bottleneck, so the limit
is applied **per source**, around the provider call.

- The limits live in `config.py` as a dictionary (source name -> number).
- `search_service.py` builds one `asyncio.Semaphore` per source at import time,
  so all users share the same semaphores.
- `search_with_limit` takes a place in the source's semaphore first and only
  then starts `asyncio.wait_for`. Time spent waiting in the queue therefore does
  **not** count against `PROVIDER_TIMEOUT`: a request that waits for a free
  place is not reported as timed out.

Current limits: Wikipedia 5, GitHub 3, Stack Overflow 10 simultaneous requests.
These are starting values, not measured optimums.

A semaphore limits how many requests run **at the same time**. It does not
enforce a rate such as GitHub's "requests per minute".

### Load test

`scripts/load_test.py` replaces the real providers with fakes that sleep for
0.3 s and count how many of them run at the same moment. It then starts 100
searches at once. No real site is contacted.

```bash
python -m scripts.load_test
```

Result with 100 simultaneous searches:

| Setup | Max simultaneous (Wikipedia / GitHub / Stack Overflow) | Total time |
|---|---|---|
| Limits 5 / 3 / 10 | 5 / 3 / 10 | 10.25 s |
| No effective limit (1000 each) | 100 / 100 / 100 | 0.31 s |

The limits are respected exactly. The price is waiting: the strictest source
(GitHub, 3 at a time) needs about 100 / 3 x 0.3 s = 10 s for 100 searches.
There were no failed searches in either run.

## Benchmark: concurrent vs sequential

`scripts/benchmark.py` measures how long each version takes for the same query.
Run it from the project root:

```bash
python -m scripts.benchmark
```

The `-m` form is needed so that imports like `from search_service import ...`
resolve from the project root.

Measured on a local machine, query `"python"`, 5 runs per version:

| Version     | Mean   | Median |
|-------------|--------|--------|
| `gather`    | 0.39 s | 0.34 s |
| sequential  | 0.69 s | 0.68 s |

The script prints the mean and median itself (`statistics` module). In this
series, the concurrent version was about 1.8 times faster by the mean and 2
times faster by the median. An earlier series gave a larger gap (about 2.5
times), so the ratio changes from run to run.

Why: sequentially, total time is roughly the **sum** of the three request
times. With `gather`, the requests wait in parallel, so total time is roughly
the time of the **slowest** request.

Caveats:

- The result depends on network conditions and varies between runs. In earlier,
  manually started runs the difference was smaller, and a single slow provider
  occasionally made `gather` slower than the sequential version.
- The same query was used in every run, so server-side caching may make the
  numbers look better than real usage.
- Five runs per version is a small sample.
- GitHub search without a token allows about 10 requests per minute, so many
  repeated runs can start failing.

## Known limitations

- GitHub search without a token is limited to about 10 requests per minute.
- Wikipedia requires a descriptive `User-Agent` header; requests with a generic
  one are rejected.
- The extra data lives inside the `description` text, not in separate fields,
  so results cannot be sorted or filtered by stars, score or answer count.
- There is no protection against Telegram's message length limit (about 4096
  characters). A typical reply is roughly 3000-3500 characters, but a query with
  long descriptions may exceed the limit, and then Telegram rejects the message.
- `search_all_sequential` does not handle provider failures and returns a plain
  list; it is used only for timing.
- A provider that times out is reported as unavailable; the bot does not tell
  the user whether it failed or was just slow.
- Under heavy load users wait in the semaphore queue; there is no limit on how
  long, and no per-minute rate limiter or cache (GitHub's per-minute limit can
  still be hit).

## Roadmap

- [x] Basic aiogram bot
- [x] Wikipedia provider
- [x] GitHub provider
- [x] Stack Overflow provider
- [x] Concurrent search and timing comparison
- [x] Partial failures: one source fails, the others still respond
- [x] Timeouts for each provider
- [x] Limiting concurrent requests under load (`asyncio.Semaphore`)
- [x] Richer results (GitHub stars and language, Stack Overflow answer count
  and accepted answer)
- [ ] Optional: split or shorten replies that exceed Telegram's length limit
- [ ] Optional: queue and workers

## Tech stack

Python, aiogram 3, httpx, asyncio, python-dotenv.