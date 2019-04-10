import itertools
import sys
import argparse
import io


def extract(data):
    schemas = []
    paths = {}

    def _extract_schema(data):
        for row in data:
            if isinstance(row, list):
                _extract_schema(row)
            elif row["type"] == "section":
                _extract_schema(row["content"])
            elif row["type"] == "code" and row["language"] == "typescript":
                schemas.append(row["lines"])

    def _extract_paths(data):
        prev_request = None
        for row in data:
            if isinstance(row, list):
                _extract_paths(row)  # xxx
            elif row["type"] == "Request":
                prev_request = row
                paths[row["attrs"]["method"]] = {"request": row}
            elif row["type"] == "Response":
                assert prev_request is not None
                paths[prev_request["attrs"]["method"]]["response"] = row
            elif row["type"] == "Notification":
                prev_request = row
                paths[row["attrs"]["method"]] = {"notification": row}
            elif row["type"] == "section":
                _extract_paths(row["content"])

    _extract_schema(data)
    _extract_paths(data)
    return {"components": {"schemas": schemas}, "paths": paths}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=argparse.FileType("r"))
    args = parser.parse_args()
    files = args.files
    if len(files) == 0:
        files = [sys.stdin]

    for f in files:
        from dictknife import loading

        loading.dumpfile(extract(loading.load(f)), format="json")


if __name__ == "__main__":
    main()
