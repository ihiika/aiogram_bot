# Concurrent Search Telegram Bot

A Telegram bot built with **aiogram 3** that takes a text query and searches
three public sources at the same time: **Wikipedia**, **GitHub** and
**Stack Overflow**. Results from all sources are merged into one unified
format and sent back to the user.

This is a learning project for a Python backend course. Its main goal is to
practice `asyncio`, working with external HTTP APIs, and handling their
failures.

## Features

- Free-text search: send any message to the bot and get results from all sources.
- Three search providers, each in its own module:
  - Wikipedia (MediaWiki API)
  - GitHub (repository search)
  - Stack Overflow (Stack Exchange API)
- A unified `SearchResult` dataclass: `title`, `description`, `url`, `source`.
- Concurrent search with `asyncio.gather`, plus a sequential version kept for
  timing comparison.
- Basic input validation (empty messages) and error logging.

## Project structure

```
.
├── bot.py                    # aiogram bot: handlers and entry point
├── models.py                 # SearchResult dataclass
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
`asyncio.gather` and returns one flat list. `search_all_sequential(query)` calls
them one after another and exists only for comparison.

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

## Roadmap

- [x] Basic aiogram bot
- [x] Wikipedia provider
- [x] GitHub provider
- [x] Stack Overflow provider
- [x] Concurrent search and timing comparison
- [ ] Partial failures: one source fails, the others still respond
- [ ] Timeouts for each provider
- [ ] Limiting concurrent requests under load (`asyncio.Semaphore`)
- [ ] Optional: queue and workers

## Tech stack

Python, aiogram 3, httpx, asyncio, python-dotenv.
