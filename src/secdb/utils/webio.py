import configparser
import requests
import re
import sys
import os

from lxml import html
from clint.textui import progress


class WebIO:
    def login(url):

        session = requests.Session()  # create a requests Session
        r = session.get(url)

        # Get token
        tree = html.fromstring(r.content)
        token_value = tree.xpath('//input[@name="_token"]/@value')
        token = str(token_value[0])
        # Form credentials
        parent_path = os.path.abspath(os.path.dirname(__file__))
        cred_filename = os.path.join(parent_path, "../credentials.conf")

        # Load Configuration File
        credentials = configparser.RawConfigParser()
        credentials.read(cred_filename)

        for cred in credentials.sections():
            email = credentials.get(cred, "user")
            password = credentials.get(cred, "password")

            # Create credentials dictionary
        data_credentials = {
            "email": email,
            "password": password,
            "_token": token,
        }

        # Log in to requests session, send post
        session.post(url, data=data_credentials)

        return session

    def download(url, file="", session=requests.Session()):

        # Find the base domain of the url to print
        urlStr = ""
        urlBase = re.search(
            r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)", url
        )
        if urlBase:
            urlStr = urlBase.group(1)

        content = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; \
            rv:64.0) Gecko/20100101 Firefox/64.0"
        }

        download_url = url + file

        # Download content
        try:
            # r = session.get(download_url, stream=True, headers=headers)
            with session.get(download_url, stream=True, headers=headers) as r:

                total_length = r.headers.get("content-length")

                if file == "":
                    disposition_elements = {}
                    # TODO: this should be it's own function to parse content
                    # disposition
                    content_disposition = r.headers.get("content-disposition")
                    if content_disposition is not None:
                        parts = content_disposition.split()

                        for part in parts:
                            if "=" in part:
                                elements = part.split("=")
                                disposition_elements[elements[0]] = elements[1]

                        file = disposition_elements["filename"]

                sys.stderr.write("\n")
                sys.stderr.write("Downloading %s from %s\n" % (file, urlStr))

                # TODO: Find a progress bar package that handles both known and
                # unknown sizes
                if total_length is None:
                    count = 0
                    done = 0
                    for chunk in r.iter_content(chunk_size=1024):
                        count += 1
                        if chunk:

                            content.append(chunk)
                            if count % 32 == 0:
                                done += 1
                                done = done % 32
                                sys.stderr.write(
                                    "\r[%s%s] 0/1 - Unknown Time Remaining"
                                    % ("#" * done, " " * (32 - done))
                                )
                                sys.stderr.flush()

                    sys.stderr.write(
                        "\r[%s] 1/1 - 00:00 Done%s\n" % ("#" * 32, " " * 32)
                    )
                    sys.stderr.flush()

                else:
                    # Show progress bar
                    total_length = int(total_length)
                    for chunk in progress.bar(
                        r.iter_content(chunk_size=1024),
                        expected_size=(total_length / 1024) + 1,
                    ):
                        if chunk:
                            # Append chunk to content list
                            content.append(chunk)

                            # Rejoin the file so it can be parsed
                download = b"".join(content)

        except requests.exceptions.ChunkedEncodingError:
            download = None

        return download
