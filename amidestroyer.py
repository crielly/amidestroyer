"""Destroy unused AMIs in your AWS account.

Usage:
    ami_destroyer.py <requiredtag> [options]

Arguments:
    <requiredtag>               Tag required for an AMI to be cleaned up in the form tag:NameOfTag

Options:
    --retain=<retain>           Number of images to retain, sorted newest to latest [default: 2]
    --regions=<regions>         A comma-separated list of AWS Regions to run against [default: us-east-1]
    --help                      Show this help string
    --dryrun                    List the AMIs that'll be destroyed by this script
"""
import sys
import logging
from operator import itemgetter
from docopt import docopt
import boto3
import botocore.exceptions as botoex

_LOGGER = logging.Logger("ami-destroyer")

def setup_logging():
    _LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)

def get_account_id():
    acctid = sts.get_caller_identity().get('Account')
    _LOGGER.info("Retrieving Account ID: {}".format(acctid))
    return acctid

def get_curated_images(tagname, accountid):
    _LOGGER.info("Retrieving AMIs with {}".format(tagname))
    return ec2.images.filter(
        Owners=[accountid],
        Filters=[
            {
                'Name':tagname,
                'Values':['True']
            }
        ]
)

def sort_curated_images(curatedimages):
    _LOGGER.info("Sorting tagged AMIs into a nice dictionary of lists of dictionaries")
    sortedimages = {}
    for i in curatedimages:
        for tag in i.tags:
            if tag['Key'] == 'Name':
                iname = tag['Value']
                break
            else:
                iname = "nonametag"
        if iname not in sortedimages:
            sortedimages[iname] = []
        sortedimages[iname].append({
            'creation_date': i.creation_date,
            'ami_id': i.image_id,
            'snapshot_id': i.block_device_mappings[0]['Ebs']['SnapshotId']
        })
        _LOGGER.info(
            "Appending {} to {} dict".format(
                i.image_id, iname
            )
        )
        sortedimages[iname] = sorted(
            sortedimages[iname],
            key=itemgetter('creation_date'),
            reverse=True
        )
    return sortedimages

def prune_sorted_images(images, retain):
    for family in images:
        _LOGGER.info(
            "Found {} tagged images for type {}. Retaining the latest {}".format(
                len(images[family]),
                family,
                retain
            )
        )
        images[family] = images[family][retain:]
        if not images[family]:
            _LOGGER.info("No images to prune for {}".format(family))
    return images

def destroy_ami(ami_id, family, dryrun):
    try:
        ec2.Image(ami_id).deregister(DryRun=dryrun)
        _LOGGER.info("Family: {} - Deregistered {}".format(family, ami_id))
    except botoex.ClientError as e:
        _LOGGER.warning("{} - {}".format(ami_id, e))

def destroy_snapshot(snapshot_id, family, dryrun):
    try:
        ec2.Snapshot(snapshot_id).delete(DryRun=dryrun)
        _LOGGER.info("Family: {} - Deleted {}".format(family, snapshot_id))
    except botoex.ClientError as e:
        _LOGGER.warning("{} - {}".format(snapshot_id, e))

def run(tag, retain, dryrun):
    acctid = get_account_id()
    curatedimages = get_curated_images(tag, acctid)
    sortedimages = sort_curated_images(curatedimages)
    if sortedimages:
        prunedimages = prune_sorted_images(sortedimages, numretain)

        for family in prunedimages:
            if prunedimages[family]:
                for ami in prunedimages[family]:
                    destroy_ami(ami['ami_id'], family, dryrun)
                    destroy_snapshot(ami['snapshot_id'], family, dryrun)
    else:
        _LOGGER.error("No tagged images to prune")

if __name__ == '__main__':
    args = docopt(__doc__)
    requiredtag = args['<requiredtag>']
    dryrun = args['--dryrun']
    numretain = int(args['--retain'])
    regions = args['--regions']
    setup_logging()

    for r in regions.split(','):
        _LOGGER.info("Running cleanup for region {}".format(r))
        ec2 = boto3.resource('ec2', region_name=r)
        sts = boto3.client('sts')

        run(requiredtag, numretain, dryrun)
