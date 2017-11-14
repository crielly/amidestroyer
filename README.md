# amidestroyer
Tool for keeping AMIs and associated snapshots under control

# Usage:
AMIs must bear a specific tag with value True and you must provide that value to amidestroyer. In this case,
my packer-built AMIs are always tagged with `Curate = True`. To perform a dry run and see what will be destroyed:

`python amidestroyer.py tag:Curate --retain=2 --regions=us-west-2,us-east-2 --dryrun`

Then simply do the same without the --dryrun option to actually perform cleanup.
