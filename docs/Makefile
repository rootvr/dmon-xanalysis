.PHONY: gen
gen: clean
	pandoc -s README.md -o README.pandoc.html --metadata title="README"
	grip README.md --export README.grip.html

.PHONY: dev
dev:
	grip README.md

.PHONY: clean
clean:
	rm -f ./README.*.html
