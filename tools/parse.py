import sys
import argparse
import io


def parse(f: io.TextIOBase):
    def _in_code(itr):
        buf = []
        for line in itr:
            if line.startswith("```"):
                break
            buf.append(line)
        return buf

    for line in f:
        if line.startswith("```"):
            language = line.strip(" \t\n`")
            lines = _in_code(f)
            if lines:
                yield {"language": language, "lines": lines}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=argparse.FileType("r"))
    args = parser.parse_args()
    files = args.files
    if len(files) == 0:
        files = [sys.stdin]

    r = []
    for f in files:
        for d in parse(f):
            if d["language"] == "typescript":
                r.append({**d, "lines": "".join(d["lines"]).strip()})

    import json

    json.dump(r, sys.stdout, indent=2)
    print("")


if __name__ == "__main__":
    main()
