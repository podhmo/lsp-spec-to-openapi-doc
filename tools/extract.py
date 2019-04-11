import sys
import re
import argparse
import textwrap
from dictknife import loading


def definition_name_from_method_name(method_name: str, _rx=re.compile(r"/.")) -> str:
    """foo/bar/boo -> fooBarBoo"""
    return _rx.sub(lambda m: m.group(0)[1].upper(), method_name)


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
                if row.get("description"):
                    schemas.append(row["description"])
                schemas.append(row["lines"])

    def _extract_paths(data):
        prev_request = None
        for row in data:
            if isinstance(row, list):
                _extract_paths(row)  # xxx
                continue

            if not row.get("description"):
                row.pop("description", None)

            if row["type"] == "Request":
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

    rx = re.compile(r"`\s*((?:[a-zA-Z0-9\[\]]+\s+\|\s+)*[a-zA-Z0-9\[\]]+)\s*`")
    for name, attrs in paths.items():
        for target in ["request", "notification", "response"]:
            if target in attrs:
                target_attrs = attrs[target]["attrs"]
                for pos in ["params", "result"]:
                    if pos in target_attrs:
                        m = rx.search(target_attrs[pos])
                        if m is not None:
                            expression = m.group(1)
                            if "|" in expression or "[]" in expression:
                                typename = (
                                    definition_name_from_method_name(name)
                                    + attrs[target]["type"]
                                )
                                schemas.append(
                                    textwrap.dedent(
                                        f"""
                                    /** the {attrs[target]["type"]} of {name} */
                                    type {typename} = {expression}
                                    """
                                    )
                                )

                                target_attrs[pos] = {
                                    "$ref": f"#/components/schemas/{typename}"
                                }
                            else:
                                target_attrs[pos] = {
                                    "$ref": f"#/components/schemas/{m.group(1)}"
                                }
    return {"components": {"schemas": schemas}, "paths": paths}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=argparse.FileType("r"))
    args = parser.parse_args()
    files = args.files
    if len(files) == 0:
        files = [sys.stdin]

    for f in files:
        loading.dumpfile(extract(loading.load(f)), format="json")


if __name__ == "__main__":
    main()
