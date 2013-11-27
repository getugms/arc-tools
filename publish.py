"""

A script for publishing map services to ArcGIS Server 10.1.

Author: David Walk
Created: 4/24/13
Deployed: ?
Version: 1.0

Parameters: none yet

Exceptions: Generic exception on service publish failure

Required non-standard library modules:
- arcpy
- gsg_util

"""

import os
import json
import arcpy
import logging
import gsg_util
import shutil
from logging import handlers

wrkspc = 'D:/arc-tools'
wrkspc2 = 'E:/MXD'

logger = logging.getLogger()
# Change logging level here (CRITICAL, ERROR, WARNING, INFO or DEBUG)
logger.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Logging variables
MAX_BYTES = 250000 
BACKUP_COUNT = 1 # Max number appended to log files when MAX_BYTES reached
log_file = wrkspc + '/log.txt'

fh = logging.handlers.RotatingFileHandler(log_file, 'a', MAX_BYTES, BACKUP_COUNT)
# Change logging level here for log file (CRITICAL, ERROR, WARNING, INFO or DEBUG)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Uncomment this block if you would like to log to the console.
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('***BEGINNING SCRIPT***')

conn = wrkspc + '/192.168.32.181.ags'
services_file = wrkspc + '/services_rda.json'

services = json.loads(open(services_file).read())

logger.info(('Services to publish: %d') % len(services))

error_list = []
success_list = []

for service in services:
    folder = service['directory']
    summary = service['summary']
    tags = service['tags']
    mxd_path = wrkspc2 + '/' + service['mxd']
    service = service['service']
    mxd = arcpy.mapping.MapDocument(mxd_path)
    sd_draft = wrkspc + '/' + service + '.sddraft'
    sd = wrkspc + '/service_definitions/' + service + '.sd'
    
    # Creating the service definition draft to analyze against
    logger.info('Creating service definition draft for %s...' % (service))
    with gsg_util.Timer() as t:
        arcpy.mapping.CreateMapSDDraft(mxd,
                                       sd_draft,
                                       service,
                                       'ARCGIS_SERVER',
                                       conn,
                                       True,
                                       folder,
                                       summary,
                                       tags)
    logger.info('Created %s service definition in %.3f seconds.' % (sd_draft, t.elapsed_secs))

    logger.debug('Analyzing service definition')
    analysis = arcpy.mapping.AnalyzeForSD(sd_draft)

    errors = analysis['errors']
    shutil.copyfile(sd_draft, sd)
    if errors:
        logger.error('There were errors!')
        for ((message, code), layerlist) in errors.iteritems():
            logger.error(code + ':' + message)
            logger.error('applies to: ')
            for layer in layerlist:
                logger.error(layer.name)
        error_list.append(service)
    else:
        logger.info('No errors, so publishing now...')
        logger.info('Creating service definition...')
        # Delete the service definition if it already exists
        if (sd):
            os.remove(sd)            
        try:
            with gsg_util.Timer() as t:
                arcpy.StageService_server(sd_draft, sd)
                logger.info('Publishing service!')            
                arcpy.UploadServiceDefinition_server(sd, conn)
            logger.info('Published %s service successfully in %.3f seconds.' % (service, t.elapsed_secs))
            success_list.append(service)
        except Exception as err:
            logger.error('Error for some reason!')
            logger.error(err)       

logger.info('***SCRIPT COMPLETED***')
logger.info(('%d services published: %s') % (len(success_list), str(success_list)))
if error_list:
    logger.info(('%d services could not be published: %s') % (len(error_list), str(error_list)))
