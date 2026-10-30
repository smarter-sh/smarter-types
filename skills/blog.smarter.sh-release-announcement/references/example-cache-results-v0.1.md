# cache-results v0.1 Release: Smarter's Caching Decorator, Now on PyPI

October 25, 2026 · The Smarter Project

Smarter has always cached the expensive parts of an AI platform (database reads on every request, calls to slow and billable third-party APIs) with one decorator, `@cache_results()`. Until today, the only way to use it was to run Smarter. As of this morning, it's a package of its own on PyPI, under the MIT license, and any Django project can install it:

```bash
pip install cache-results
```

This is the first release of cache-results, and the first time a piece of Smarter's own framework has been published for projects that have nothing to do with Smarter. It depends only on Django and asgiref, and it works with any Django cache backend. With Redis, cached results survive restarts and deployments, and every process on every server shares them.

| What you get                     | In one sentence                                                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Keys you don't have to write** | The key is the function's module and qualified name, plus a hash of its arguments bound to its signature.                             |
| **Safe keys, or no caching**     | An argument that can't be part of a safe key, such as a model instance, runs the function uncached instead of being keyed by `str()`. |
| **`.invalidate()`**              | Every decorated function can clear the entry of any arguments, however the call was written.                                          |
| **async functions**              | Their results are cached, not their coroutines, without blocking the event loop.                                                      |
| **Safe at startup**              | A function called before Django is ready runs uncached, rather than initialize the cache framework too early.                         |
| **One setting**                  | `CACHE_RESULTS` configures the cache, the default timeout, key versioning and logging.                                                |

The rest of this post shows how to use it, what changed on the way out of Smarter, and how the package is built and released.

---

## Using it

Decorate a function whose result is expensive to compute and depends only on its arguments:

```python
from cache_results import cache_results


@cache_results(timeout=600)
def get_book(book_id: int) -> dict:
    return Book.objects.values().get(pk=book_id)


get_book(42)             # computed and cached
get_book(42)             # served from the cache
get_book.invalidate(42)  # clears that entry
```

There's nothing to add to `INSTALLED_APPS`. Results go to your `default` cache unless you name another one, and every setting is optional.

- **Pass plain values.** Arguments are the key, so pass `book.pk`, not `book`. Strings, numbers, booleans, `None`, and lists, tuples, dicts and sets of them all work, as do datetimes, Decimals, UUIDs, classes and dataclasses. To allow another type, subclass `CacheKeyEncoder` and name your subclass in the `KEY_ENCODER` setting.
- **One call, many spellings.** `search("django")`, `search("django", 10)` and `search(query="django", limit=10)` share one entry when `limit` defaults to 10, so `invalidate()` finds the entry however the original call was written.
- **`None` is a result.** A function that returns `None` is cached like any other, instead of being recomputed on every call.
- **Classmethods** are cached per class, so a subclass doesn't read its parent's entries. Instance methods are refused when the class is defined, because `self` can't be part of a safe key.
- **Concurrent misses.** When several threads of one process miss the same key at once, the first computes it and the others wait for its result.
- **Abandon everything at once.** Change `CACHE_RESULTS["VERSION"]` after a deploy that changes what your functions return, and every cached result becomes a miss, without touching sessions or anything else in the same cache.

```python
# settings.py: every entry is optional
CACHE_RESULTS = {
    "CACHE_ALIAS": "default",
    "TIMEOUT": 3600,
    "VERSION": 2,
    "LOGGING_ENABLED": "myapp.cache.cache_logging_enabled",
}
```

Logging is off by default, and when it's on, it never writes a cached result to your logs: only the function's name and the result's type. A project can tie it to its own switch through a hook, e.g. a feature flag. That's how Smarter turns cache logging on and off.

For how the decorator works inside, and why each of these rules exists, read [How Smarter's @cache_results() Decorator Works](https://blog.smarter.sh/2026/10/25/smarter-cache-results/).

📖 [cache-results documentation](https://docs.cache-results.smarter.sh/)

---

## What changed on the way out of Smarter

Publishing a decorator for strangers is a higher bar than running it inside your own platform, so before this release it got a review aimed at exactly that question: would this be safe in someone else's project? The answer was "not quite yet", and the gaps it found were fixed in Smarter first, then carried into the package.

- **No more `str()` keys.** Smarter's version used to key an argument it didn't recognize by its `str()`. Two model rows with the same name then shared one cache entry, and an object without its own `__str__` (`<Book object at 0x...>`) got a new key in every process, so its entries were never read and piled up in Redis. Now such a call runs uncached, and logs an error naming the function and the argument's type, once per process. The review also found Smarter's own call sites that relied on `str()`, and changed them to pass ids.
- **async functions are cached properly.** Previously, the decorator cached the coroutine rather than the result. It now caches the result, and reads and writes the cache without holding up the event loop. Django's default async cache methods run every call on one shared thread, so the decorator uses a backend's own async methods when it has them, and a worker thread otherwise.
- **Startup is safe.** A decorated function called before Django's apps were ready used to crash. Django's cache is now initialized lazily, and such a call simply runs uncached.
- **Results stay out of the logs.** Verbose cache logging used to write cached results to the log. Now it writes their type.
- **Nothing project-specific.** Everything that was Smarter's own (its settings, colored logs, feature flags and Pydantic support) became a hook that a project plugs in through `CACHE_RESULTS`. Smarter now configures the package the same way any other project would.

---

## Built to be depended on

A caching layer sits under everything else, so the package is held to the standards of a dependency, not a script:

- **Tested on every pair of Python and Django versions it supports**, from Python 3.10 with Django 4.2 to Python 3.14 with Django 6.0, and against a real Redis server, on every push and pull request. Coverage is 99%, reported on [Codecov](https://codecov.io/gh/smarter-sh/cache-results).
- **Typed.** The package ships `py.typed`, so your type checker and editor read its annotations, which are checked with mypy and django-stubs.
- **Your cached entries survive upgrades.** The key format and the stored value of `None` are part of the public interface. Changing either would empty every user's cache at once, so it can only happen in a new major version.
- **Released by a workflow, not a laptop.** One GitHub Actions run tests the release, tags it, rehearses the upload on TestPyPI, installs it back, then publishes to PyPI and installs that back too. It uses PyPI's trusted publishing, so no PyPI token exists anywhere, and PyPI keeps a signed provenance attestation that each file was built from this repository by that workflow.
- **Documented.** [docs.cache-results.smarter.sh](https://docs.cache-results.smarter.sh/) has an installation guide, a quickstart, a user guide (arguments and keys, invalidation, async, methods, settings, logging, and testing code that uses the decorator), an API reference generated from the code, and the project's architecture decision records: 18 short notes on why it's built the way it is.

---

## Try it, and tell people about it

This is a 0.1, so this is the moment when your feedback shapes it most:

- **Install it** in a project that has a slow query or a slow API call, and decorate it: `pip install cache-results`.
- **Star the repository** at [github.com/smarter-sh/cache-results](https://github.com/smarter-sh/cache-results), so that other Django developers can find it.
- **Open an issue** for a bug, a cache backend that misbehaves, or an argument type you need. Pull requests are welcome too: `make init` sets up everything, and the [contributing guide](https://docs.cache-results.smarter.sh/project/contributing.html) explains the rules.
- **Look at Smarter**, the open-source platform that cache-results came from, for building and running AI applications in Django: [smarter.sh](https://smarter.sh).

---

## What's next

- **Smarter switches to the package.** Smarter still runs its own copy of the code, kept identical to the package. Its next step is to install cache-results from PyPI like any other project, and keep only its hooks.
- **More backends in CI.** The tests run against Django's local-memory cache and Redis. Memcached and the database cache are not tested yet.

The changelog is on [GitHub](https://github.com/smarter-sh/cache-results/blob/main/CHANGELOG.md), with the [v0.1.0 release](https://github.com/smarter-sh/cache-results/releases/tag/v0.1.0). The package is on [PyPI](https://pypi.org/project/cache-results/), the docs are at [docs.cache-results.smarter.sh](https://docs.cache-results.smarter.sh/), and the source is at [github.com/smarter-sh/cache-results](https://github.com/smarter-sh/cache-results).
