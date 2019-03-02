import boto3
import click
session=boto3.Session(profile_name='ravi')
ec2=session.resource('ec2')
def filter_instances(project):
    instances=[]
    if project:
        filters = [{'Name':'tag:Project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances
@click.group()
def cli():
    """ Shotty for managing volumes """
@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""
@snapshots.command('list')
@click.option('--project',default=None,
    help="Only instance of project (tag Project:<name>)")
def list_snapshots(project):
    "List Volume Snapshots"
    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(",".join((
                    i.id,
                    v.id,
                    s.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                    )))
@cli.group('volumes')
def volumes():
    """ Commands for volumes """
@volumes.command('list')
@click.option('--project',default=None,
    help="Only instance of project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes"
    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            print(",".join((
                 v.volume_id,
                 i.id,
                 str(v.size) + "GiB",
                 v.state,
                 v.encrypted and "Encrypted" or "Not Encrypted"
                 )))
    return
@cli.group('instances')
def instances():
    """Commands for instances """
@instances.command('list')
@click.option('--project',default=None,
    help="Only instance of project (tag Project:<name>)")
def list_instances(project):
    "List EC2 Instances"
    instances = filter_instances(project)
    for i in instances:
        tags={t['Key']:t['Value'] for t in i.tags or []}
        print(','.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('Project','<no project>')
        )))
    return
@instances.command('stop')
@click.option('--project',default=None,
              help='Only instances for this project')
def stop_instances(project):
    "Stop Instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping the instance -> {0}".format(i))
        i.stop()
    return
@instances.command('start')
@click.option('--project',default=None,
              help='Only instances for this project')
def start_instances(project):
    "Start Instances"
    instances = filter_instances(project)
    for i in instances:
        print("Starting the instance -> {0}".format(i))
        i.start()
    return
@instances.command('snapshot',help='create snapshot for all volumes')
@click.option('--project',default=None,
              help='Only instances for this project')
def create_snapshots(project):
    "Create Snapshots"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping instance for snapshot creation -> {0}".format(i))
        i.stop()
        for v in i.volumes.all():
            print("Creating Snapshot of {0}".format(v))
            v.create_snapshot(Description="Snapshot is created by SnapshotAnaluzer 3000")
    return
if __name__ == '__main__':
    cli()
