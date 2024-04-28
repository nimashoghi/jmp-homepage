FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Install pixi
RUN curl -fsSL https://pixi.sh/install.sh | bash

# Copy over the current dependencies and install them
COPY pyproject.toml ./
COPY pixi.lock ./
RUN /root/.pixi/bin/pixi install

# Copy over the rest of the files
COPY . .

# Run the application
CMD /root/.pixi/bin/pixi run python -m jmphome.tsne
