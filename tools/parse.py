import itertools
import sys
import argparse
import io

from dictknife import loading


def parse(itr: io.TextIOBase):
    def _in_code():
        buf = []
        for line in itr:
            if line.lstrip(" ").startswith("```"):
                break
            buf.append(line)
        return buf

    def _in_types():
        nonlocal itr
        buf = []
        for line in itr:
            if line.lstrip("").startswith("*"):
                buf.append([x.strip("' ,") for x in line.strip("* \n").split(":", 1)])
                continue
            itr = itertools.chain([line], itr)
            break
        return dict(buf)

    def _in_section(r, *, current_level):
        nonlocal itr
        buf = {"content": []}
        while True:
            for line in itr:
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    if level == current_level:
                        if buf["content"]:
                            r.append(buf)
                        buf = {"type": "section", "title": line.strip(), "content": []}
                    elif level < current_level:
                        if buf:
                            r.append(buf)
                        itr = itertools.chain([line], itr)
                        return r
                    else:  # level > current_level:
                        itr = itertools.chain([line], itr)
                        child = _in_section([], current_level=level)
                        if child:
                            buf["content"].append(child)
                        break
                elif line.lstrip(" ").startswith("_") and line.rstrip(" :\n").endswith(
                    "_"
                ):
                    buf["content"].append(
                        {"type": line.strip(" _:\n"), "attrs": _in_types()}
                    )
                    break
                elif line.lstrip(" ").startswith("```"):
                    language = line.strip(" \t\n`")
                    lines = _in_code()
                    buf["content"].append(
                        {"type": "code", "language": language, "lines": lines}
                    )

            else:
                break
            continue
        if buf["content"]:
            r.append(buf)
        return r

    return _in_section([], current_level=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=argparse.FileType("r"))
    args = parser.parse_args()
    files = args.files
    if len(files) == 0:
        files = [sys.stdin]

    r = []
    for f in files:
        loading.dumpfile(parse(f), format="json")


if __name__ == "__main__":
    main()
