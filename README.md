- The Stack Overflow description currently contains only the question score.
- Long result lists may exceed Telegram's message length limit (about 4096
  characters).
- `search_all_sequential` does not handle provider failures and returns a plain
  list; it is used only for timing.
- A provider that times out is reported as unavailable; the bot does not tell
  the user whether it failed or was just slow.

## Roadmap

- [x] Basic aiogram bot
- [x] Wikipedia provider
- [x] GitHub provider
- [x] Stack Overflow provider
- [x] Concurrent search and timing comparison
- [x] Partial failures: one source fails, the others still respond
- [x] Timeouts for each provider
- [ ] Limiting concurrent requests under load (`asyncio.Semaphore`)
- [ ] Richer results (GitHub stars and language, Stack Overflow answer count)
- [ ] Optional: queue and workers

## Tech stack

Python, aiogram 3, httpx, asyncio, python-dotenv.
