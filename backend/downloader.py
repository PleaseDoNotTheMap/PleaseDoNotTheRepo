import os
import subprocess
import threading
import logging

logger = logging.getLogger('landsat.downloader')


class Downloader:
    def __init__(self, s3_urls, destination):
        self.s3_urls = s3_urls
        self.destination = destination
        self.threads = []

    def start(self):
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

        for s3_url in self.s3_urls:
            filename = os.path.basename(s3_url)
            local_path = os.path.join(self.destination, filename)

            thread = threading.Thread(target=self._run, args=(s3_url, local_path))
            thread.start()

            self.threads.append(thread)

        for thread in self.threads:
            thread.join()

    def _run(self, s3_url, local_path):
        command = f"aws s3 cp {s3_url} {local_path} --request-payer requester"
        process = subprocess.Popen(command, shell=True)
        process.communicate()

        if process.returncode != 0:
            logger.debug(f"{s3_url} failed with ret {process.returncode}")


# s3_urls = [
#     "s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2021/029/029/LC08_L2SP_029029_20210429_20210508_02_T1/LC08_L2SP_029029_20210429_20210508_02_T1_thumb_large.jpeg",
#     "s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2021/030/029/LC08_L2SP_030029_20210319_20210328_02_T1/LC08_L2SP_030029_20210319_20210328_02_T1_SR_B4.TIF"
# ]
#
# downloader = Downloader(s3_urls, "data")
# downloader.start()
