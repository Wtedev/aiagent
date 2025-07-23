import json, itertools, pathlib

sample_path = pathlib.Path("data/cases.jsonl")
with sample_path.open(encoding="utf8") as f:
    first = next(itertools.islice(f, 0, 1))   # أول سطر
    print(json.loads(first))