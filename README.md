# amidestroyer
Tool for keeping AMIs and associated snapshots under control
```
Usage:
    ami_destroyer.py <requiredtag> [options]

Arguments:
    <requiredtag>               Tag required for an AMI to be cleaned up in the form tag:NameOfTag

Options:
    --retain=<retain>           Number of images to retain, sorted newest to latest [default: 2]
    --regions=<regions>         A comma-separated list of AWS Regions to run against [default: us-east-1]
    --help                      Show this help string
    --dryrun                    List the AMIs that'll be destroyed by this script
```
AMIs must bear a specific tag with value True and you must provide that value to amidestroyer. In this case,
my packer-built AMIs are always tagged with `Curate = True`. To perform a dry run and see what will be destroyed:

`python amidestroyer.py tag:Curate --retain=2 --regions=us-west-2,us-east-2 --dryrun`

Then simply do the same without the --dryrun option to actually perform cleanup.
