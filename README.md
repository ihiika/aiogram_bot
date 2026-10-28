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
  - Wikipedia (MediaWiki API)
  - GitHub (repository search)
  - Stack Overflow (Stack Exchange API)
- A unified `SearchResult` dataclass: `title`, `description`, `url`, `source`.
- Concurrent search with `asyncio.gather`, plus a sequential version kept for
  timing comparison.
- Partial failure handling: a failing provider does not break the whole search.
- Basic input validation (empty messages) and error logging.

## Project structure

```
.
├── bot.py                    # aiogram bot: handlers and entry point
├── models.py                 # SearchResult and SearchOutcome dataclasses
├── search_service.py         # search_all (concurrent), search_all_sequential
├── providers_wikipedia.py    # Wikipedia provider
├── providers_github.py       # GitHub provider
├── providers_stackoverflow.py# Stack Overflow provider
├── benchmark.py              # timing: concurrent vs sequential
├── requirements.txt          # dependencies
└── token.env.example         # example of the environment file
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

`search_service.search_all(query)` starts all three providers at once with
`asyncio.gather` and returns a `SearchOutcome`:

- `results`: a flat list of `SearchResult` from the providers that responded;
- `failed_sources`: names of the providers that raised an error;
- `total_sources`: how many providers were queried;
- `all_failed`: a property, `True` when every provider failed.

`search_all_sequential(query)` calls the providers one after another and exists
only for timing comparison.

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

## Benchmark: concurrent vs sequential

`benchmark.py` measures how long each version takes for the same query.

Measured on a local machine, query `"python"`, 5 runs per version:

| Version     | Mean   | Median |
|-------------|--------|--------|
| `gather`    | 0.45 s | 0.43 s |
| sequential  | 1.11 s | 1.16 s |

In this series, the concurrent version was about 2.5 times faster.

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

## Known limitations

- GitHub search without a token is limited to about 10 requests per minute.
- Wikipedia requires a descriptive `User-Agent` header; requests with a generic
  one are rejected.
- The Stack Overflow description currently contains only the question score.
- Long result lists may exceed Telegram's message length limit (about 4096
  characters).
- `search_all_sequential` does not handle provider failures and returns a plain
  list; it is used only for timing.
- There are no timeouts for providers yet.

## Roadmap

- [x] Basic aiogram bot
- [x] Wikipedia provider
- [x] GitHub provider
- [x] Stack Overflow provider
- [x] Concurrent search and timing comparison
- [x] Partial failures: one source fails, the others still respond
- [ ] Timeouts for each provider
- [ ] Limiting concurrent requests under load (`asyncio.Semaphore`)
- [ ] Optional: queue and workers

## Tech stack

Python, aiogram 3, httpx, asyncio, python-dotenv.
