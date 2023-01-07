FROM image:alpine

# Install python/pip
RUN apk update && apk add --update --no-cache \
  # Install the latest version of python 3
  python3 \
  # Installs pip since it isn't packaged with python
  py3-pip && \
  # Makes 'python' available in path
  ln -sf python3 /usr/bin/python

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
