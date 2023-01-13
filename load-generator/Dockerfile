FROM python:3

ARG sauce_username
ARG sauce_access_key
ENV SAUCE_USERNAME=${sauce_username}
ENV SAUCE_ACCESS_KEY=${sauce_access_key}

WORKDIR /

RUN yes | apt install unzip

RUN sh -c 'curl -L https://saucelabs.github.io/saucectl/install | bash -s -- -b /usr/local/bin'

RUN saucectl configure --username $sauce_username --accessKey $sauce_access_key

COPY . .
COPY ./../common/app_file_names.properties ./

ENTRYPOINT ["python", "-m", "run"]