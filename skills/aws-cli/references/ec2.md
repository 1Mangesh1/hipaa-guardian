# AWS EC2 Reference

## Instance Management

```bash
# Launch instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-12345 \
  --subnet-id subnet-12345 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-server}]'

# Describe with filters
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Modify instance type (must be stopped)
aws ec2 stop-instances --instance-ids i-123
aws ec2 wait instance-stopped --instance-ids i-123
aws ec2 modify-instance-attribute --instance-id i-123 --instance-type t3.medium
aws ec2 start-instances --instance-ids i-123

# Terminate
aws ec2 terminate-instances --instance-ids i-123
```

## Security Groups

```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-sg \
  --description "Web server security group" \
  --vpc-id vpc-12345

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress --group-id sg-123 \
  --ip-permissions \
  'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0}]' \
  'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0}]'

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress --group-id sg-123 \
  --protocol tcp --port 22 --cidr 203.0.113.0/32

# List rules
aws ec2 describe-security-groups --group-ids sg-123 \
  --query 'SecurityGroups[].IpPermissions[]'
```

## AMI Management

```bash
# Create AMI from instance
aws ec2 create-image \
  --instance-id i-123 \
  --name "web-server-$(date +%Y%m%d)" \
  --no-reboot

# List AMIs
aws ec2 describe-images --owners self \
  --query 'Images | sort_by(@, &CreationDate) | [-5:].[ImageId,Name,CreationDate]' \
  --output table

# Deregister old AMI
aws ec2 deregister-image --image-id ami-123
```

## Elastic IPs

```bash
# Allocate
aws ec2 allocate-address --domain vpc

# Associate
aws ec2 associate-address --instance-id i-123 --allocation-id eipalloc-123

# Release
aws ec2 release-address --allocation-id eipalloc-123
```

## Volumes

```bash
# Create volume
aws ec2 create-volume --size 100 --volume-type gp3 --availability-zone us-east-1a

# Attach to instance
aws ec2 attach-volume --volume-id vol-123 --instance-id i-123 --device /dev/xvdf

# Create snapshot
aws ec2 create-snapshot --volume-id vol-123 --description "Daily backup"
```
