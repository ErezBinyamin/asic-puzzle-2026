IMAGE_NAME=asicre
DEPS=Dockerfile

.PHONY: all bash
all: .image_build

.image_build: $(DEPS)
	docker build -t $(IMAGE_NAME) .
	touch .image_build

bash: .image_build
	docker run -it --volume $(PWD)/:/puzzle $(IMAGE_NAME) bash
