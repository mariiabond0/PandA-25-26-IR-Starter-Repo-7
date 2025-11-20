# Part 7 — Starter

This part builds on your Part 6 solution. The key goal is to replace composite objects with instanced of classes!
1. We had a `Dict[str, Any]` to represent ane line match of our search result. We now will use instances of class `LineMatch`.
1. We had a `Dict[str, Any]` to represent a result from our search. We are replacing it with instances of class `SearchResult`.
2. We had a `Dict[str, Any]` to represent a sonnet. We are now going to use instances of class `Sonnet` to do that.
3. We had a `Dict[str, Any]` to represent our configuration. Now we will use a class called `Config` to handle our system's configuration.

## Run the app

```bash
python -m part7.app
```

## What to implement (ToDos)

As always, your todos are located in `app.py`, specifically, in `part7/app.py`

0. **Copy** your implementation from part 6: 
  - Loading sonnets from PoetryDB API
  - Caching of the sonnets in a local file named `sonnets.json`
  - Add the timings for sonnets load and query execution.
1. Instead of using **dictionaries** when creating the composite objects, use the corresponding **classes**.
2. Instead of accessing the elements of the dictionaries (e.g., `sonnet["title"]`), use the attribute of the class and dot notation (e.g., `sonnet.title`).
