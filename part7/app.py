#!/usr/bin/env python3
"""
Part 7 starter CLI.

WHAT'S NEW IN PART 7
C L A S S E S! (🎉): Get rid of all the composite objects and use instances of classes instead!

Where ever we used a dictionary, we will use a constructor of a class (e.g.
LineMatch(idx, line_raw, spans) instead of {"line_no": idx, "text": line_raw, "spans": spans})

Where ever we used key access, we will use dot notation, e.g. with a line match lm: lm.line_no instead of lm["line_no"]
"""

from typing import List
import json
import os
import time
import urllib.request
import urllib.error

from part7.constants import BANNER, HELP, POETRYDB_URL
from part7.models import Sonnet, SearchResult, Configuration, LineMatch

def find_spans(text: str, pattern: str):
    """Return [(start, end), ...] for all (possibly overlapping) matches.
    Inputs should already be lowercased by the caller."""
    spans = []
    if not pattern:
        return spans

    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            spans.append((i, i + len(pattern)))
    return spans


def ansi_highlight(text: str, spans):
    """Return text with ANSI highlight escape codes inserted."""
    if not spans:
        return text

    spans = sorted(spans)
    merged = []

    # Merge overlapping spans
    current_start, current_end = spans[0]
    for s, e in spans[1:]:
        if s <= current_end:
            current_end = max(current_end, e)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = s, e
    merged.append((current_start, current_end))

    # Build highlighted string
    out = []
    i = 0
    for s, e in merged:
        out.append(text[i:s])
        out.append("\033[43m\033[30m")  # yellow background, black text
        out.append(text[s:e])
        out.append("\033[0m")           # reset
        i = e
    out.append(text[i:])
    return "".join(out)

def search_sonnet(sonnet: Sonnet, query: str) -> SearchResult:
    title_raw = str(sonnet["title"])
    lines_raw = sonnet["lines"]  # list[str]

    q = query.lower()
    title_spans = find_spans(title_raw.lower(), q)

    line_matches = []
    for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
        spans = find_spans(line_raw.lower(), q)
        if spans:
            lm = LineMatch(idx, line_raw, spans)
            line_matches.append(lm)

    total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)
    # ToDo 1: Use an instance of class SearchResult
    return SearchResult(
        title=title_raw,
        title_spans=title_spans,
        line_matches=line_matches,
        matches=total
    )


def combine_results(result1: SearchResult, result2: SearchResult) -> SearchResult:
    """Combine two search results."""

    combined = result1.copy()  # shallow copy

    # ToDo 2: Use dot notation instead of keys to access the attributes of the search results

    combined.matches = result1.matches + result2.matches
    combined.title_spans = sorted(result1.title_spans + result2.title_spans)

    # Merge line_matches by line number

    # ToDo 1: Instead of using a dictionary, e.g., dict(lm), copy the line match, e.g., lm.copy()!
    #lines_by_no = {lm.line_no: LineMatch(lm.line_no, lm.text, lm.spans.copy()) for lm in combined.line_matches}
    lines_by_no = {lm.line_no: lm for lm in combined.line_matches}
    for lm in result2.line_matches:
        ln = lm.line_no
        if ln in lines_by_no:
            # extend spans & keep original text
            lines_by_no[ln].spans.extend(lm.spans)
        else:
            #lines_by_no[ln] = LineMatch(lm.line_no, lm.text, lm.spans.copy())
            lines_by_no[ln] = lm.copy()

    combined.line_matches = sorted(lines_by_no.values(), key=lambda lm: lm.line_no)

    return combined


def print_results(
    query: str,
    results: List[SearchResult],
    highlight: bool,
    query_time_ms: float | None = None,
) -> None:
    total_docs = len(results)
    matched = [r for r in results if r.matches > 0]

    line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
    if query_time_ms is not None:
        line += f" Your query took {query_time_ms:.2f}ms."
    print(line)

    for idx, r in enumerate(matched, start=1):
        # ToDo 2: Use dot notation instead of key access of the search result

        title_line = (
            ansi_highlight(r.title, r.title_spans)
            if highlight
            else r.title
        )
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in r.line_matches:
            line_out = (
                ansi_highlight(lm.text, lm.spans)
                if highlight
                else lm.text
            )
            print(f"  [{lm.line_no:2}] {line_out}")


# ---------- Paths & data loading ----------

def module_relative_path(name: str) -> str:
    """Return absolute path for a file next to this module."""
    return os.path.join(os.path.dirname(__file__), name)


def fetch_sonnets_from_api() -> List[Sonnet]:
    """
    Call the PoetryDB API (POETRYDB_URL), decode the JSON response and
    convert it into a list of dicts.

    - Use only the standard library (urllib.request).
    - PoetryDB returns a list of poems.
    - You can add error handling: raise a RuntimeError (or print a helpful message) if something goes wrong.
    """
    # ToDo 0: Copy your solution from Part 6

    # POETRYDB_URL already contains the URL
    with urllib.request.urlopen(POETRYDB_URL) as response:
        mydata = response.read().decode("utf-8")
        my_sonnets = json.loads(mydata)
        if not isinstance(my_sonnets, list):
            raise RuntimeError("Unexpected API response format: expected a list of poems")
        return my_sonnets


def load_sonnets() -> List[Sonnet]:
    """
    Load Shakespeare's sonnets with caching.

    Behaviour:
      1. If 'sonnets.json' already exists:
           - Print: "Loaded sonnets from cache."
           - Return the data.
      2. Otherwise:
           - Call fetch_sonnets_from_api() to load the data.
           - Print: "Downloaded sonnets from PoetryDB."
           - Save the data (pretty-printed) to CACHE_FILENAME.
           - Return the data.
    """
    # ToDo 0: Copy your implementation from Part 6
    cache_file = module_relative_path("sonnets.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            sonnets_json = json.load(f)
        print("Loaded sonnets from cache.")
        return sonnets_json
    # Default implementation: Load from the API always
    CACHE_FILENAME = fetch_sonnets_from_api()
    print("Downloaded sonnets from PoetryDB.")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(CACHE_FILENAME, f, indent=2, ensure_ascii=False)
    return CACHE_FILENAME


# ---------- Config handling (carry over from Part 5) ----------

DEFAULT_CONFIG = Configuration()

def load_config() -> Configuration:
    """ToDo 0:
    Copy your working implementation from Part 5.
    """
    config_file_path = module_relative_path("config.json")

    cfg = DEFAULT_CONFIG.copy()

    try:
        if os.path.exists(config_file_path):
            with open(config_file_path) as config_file:
                cfg.update(json.load(config_file))
    except FileNotFoundError:
        # File simply doesn't exist yet → quiet, just use defaults
        print("No config.json found. Using default configuration.")
        return cfg
    except json.JSONDecodeError:
        # File exists but is not valid JSON
        print("config.json is invalid. Using default configuration.")
        return cfg
    except OSError:
        # Any other OS / IO problem (permissions, disk issues, etc.)
        print("Could not read config.json. Using default configuration.")
        return cfg

    return cfg

def save_config(cfg: Configuration) -> None:
    """ToDo 0:
    Copy your working implementation from Part 5.
    """
    config_file_path = module_relative_path("config.json")
    try:
        with open(config_file_path, "w") as config_file:
            json.dump(cfg.__dict__, config_file, indent=4)
    except OSError:
        print(f"Writing config.json failed.")

# ---------- CLI loop ----------

def main() -> None:
    print(BANNER)
    config = load_config()

    # Load sonnets (from cache or API)
    # ToDo 0: Time how long loading the sonnets take and print it to the console (copy from Part 6)
    start = time.perf_counter()
    sonnets = load_sonnets()
    end = time.perf_counter()
    elapsed = (end - start) * 1000
    print(f"Loaded {len(sonnets)} sonnets. \nIt took {elapsed:.2f} ms.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config.highlight = parts[1].lower() == "on"
                    print("Highlighting", "ON" if config.highlight else "OFF")
                    save_config(config)
                else:
                    print("Usage: :highlight on|off")
                continue

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config.search_mode = parts[1].upper()
                    print("Search mode set to", config.search_mode)
                    save_config(config)
                else:
                    print("Usage: :search-mode AND|OR")
                continue

            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        # ToDo 0: Time how the execution of the user query takes (copy from Part 6)
        start = time.perf_counter()
        # query
        combined_results = []

        words = raw.split()

        for word in words:
            # Searching for the word in all sonnets
            results = [search_sonnet(s, word) for s in sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    # ToDo 2: Use dot notation instead of key access of the search result

                    if config.search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            combined_results[i] = combine_results(combined_result, result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif config.search_mode == "OR":
                        combined_results[i] = combine_results(combined_result, result)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000

        print_results(raw, combined_results, config.highlight, elapsed_ms)


if __name__ == "__main__":
    main()
