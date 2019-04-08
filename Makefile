SPEC_URL := https://github.com/Microsoft/language-server-protocol/raw/master/versions/protocol-2-x.md

src/spec.md:
	wget ${SPEC_URL} -O $@
