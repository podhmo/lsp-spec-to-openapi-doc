SPEC_URL := https://github.com/Microsoft/language-server-protocol/raw/master/versions/protocol-2-x.md

default: src/jsonschema.json

src/spec.md:
	wget ${SPEC_URL} -O $@
src/parsed.json: src/spec.md tools/parse.py
	python tools/parse.py src/spec.md | tee $@
src/extracted.json: src/parsed.json tools/extract.py
	python tools/extract.py src/parsed.json | tee $@
src/interfaces.ts: src/extracted.json
	jqfpy -r '"".join(["".join(code) for code in get("components/schemas")])' src/extracted.json | tee $@
src/jsonschema.json: src/interfaces.ts
	./node_modules/.bin/quicktype src/interfaces.ts -l schema | tee $@
src/swagger.yaml:  src/jsonschema.json src/extracted.json tools/merge.py
	python tools/merge.py --extracted=src/extracted.json --jsonschema=src/jsonschema.json -o yaml | tee $@
