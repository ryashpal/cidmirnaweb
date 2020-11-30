import os, time
import logging

from django.conf import settings

def cleanUpTempFiles():
    logging.info('scheduled cron job started')
    tmpPath = os.path.join(settings.BASE_DIR, 'static', 'tmp')
    now = time.time()
    for directory in os.listdir(tmpPath):
        tmpDirectory = os.path.join(tmpPath, directory)
        logging.info('directory: ' + tmpDirectory)
        if os.stat(tmpDirectory).st_mtime < now - 86400:
            logging.info('directory to delete: ' + tmpDirectory)
            if os.path.exists(tmpDirectory):
                for f in os.listdir(tmpDirectory):
                    tmpFile = os.path.join(tmpDirectory, f)
                    logging.info('file: ' + tmpFile)
                    if os.path.isfile(tmpFile):
                        logging.info('cron job cleaning up:' + tmpFile)
                        os.remove(tmpFile)
                os.rmdir(tmpDirectory)
    logging.info('scheduled cron job ended')
