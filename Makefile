GITSHA=`git rev-parse --short HEAD`

.DEFAULT_GOAL: build

build:
	docker build -t amidestroyer -f Dockerfile .
	docker tag amidestroyer:latest starseed/amidestroyer:$(GITSHA)
	docker tag amidestroyer:latest starseed/amidestroyer:latest

publish:
	docker push starseed/amidestroyer:latest
	docker push starseed/amidestroyer:$(GITSHA)
