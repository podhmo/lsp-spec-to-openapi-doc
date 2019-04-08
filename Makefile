SPEC_URL := https://github.com/Microsoft/language-server-protocol/raw/master/versions/protocol-2-x.md

src/interfaces.json: src/spec.md
	python tools/parse.py src/spec.md | tee $@
src/spec.md:
	wget ${SPEC_URL} -O $@
