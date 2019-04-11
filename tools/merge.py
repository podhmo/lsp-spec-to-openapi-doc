import argparse
from dictknife import DictWalker
from dictknife import loading


def merge(*, extracted, jsonschema):
    schemas = {}
    paths = extracted["paths"]

    for name, s in jsonschema["definitions"].items():
        if "$ref" in s:
            s["$ref"].replace("#definitions", "#/components/schemas")
            schemas[name] = s
        else:
            schemas[name] = s

    # remove needless title property
    for path, sd in DictWalker(["title"]).walk(schemas):
        if path[-2] == sd["title"]:
            sd.pop("title")

    return {"components": {"schemas": schemas}, "paths": paths}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted", required=True)
    parser.add_argument("--jsonschema", required=True)
    parser.add_argument(
        "-o", "--output-format", default="yaml", choices=["json", "yaml"]
    )
    args = parser.parse_args()
    r = merge(
        extracted=loading.loadfile(args.extracted),
        jsonschema=loading.loadfile(args.jsonschema),
    )
    loading.dumpfile(r, format=args.output_format)


if __name__ == "__main__":
    main()
