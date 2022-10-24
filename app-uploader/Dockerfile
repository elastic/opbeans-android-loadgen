FROM androidsdk/android-31

ARG sauce_username
ARG sauce_access_key
ARG opbeans_endpoint
ARG firebase_app_id
ARG opbeans_auth_token=None
ARG exporter_endpoint=https://c7af8dcb537d47d29c34e0d5233df782.apm.us-west2.gcp.elastic-cloud.com:443
ARG exporter_auth_token=MJkZnP1f7iMVSaTJIg
ENV EXPORTER_AUTH_TOKEN=${exporter_auth_token}
ENV EXPORTER_ENDPOINT=${exporter_endpoint}
ENV OPBEANS_AUTH_TOKEN=${opbeans_auth_token}
ENV OPBEANS_ENDPOINT=${opbeans_endpoint}
ENV SAUCE_USERNAME=${sauce_username}
ENV SAUCE_ACCESS_KEY=${sauce_access_key}
ENV OPBEANS_APP_ID=${firebase_app_id}
ENV GOOGLE_APPLICATION_CREDENTIALS=/script/assets/opbeans-android-key.json

WORKDIR /

RUN apt update
RUN yes | apt install python3-pip
RUN yes | apt install zip

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./run.py ./
COPY ./opbeans-android-key.json $GOOGLE_APPLICATION_CREDENTIALS

CMD python3 -m run --exporter-endpoint ${EXPORTER_ENDPOINT} --exporter-auth-token ${EXPORTER_AUTH_TOKEN} --opbeans-endpoint ${OPBEANS_ENDPOINT} --opbeans-auth-token ${OPBEANS_AUTH_TOKEN}