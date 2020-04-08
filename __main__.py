import pulumi
import pulumi_aws as aws

# Define some variables to use in the stack
size = "t2.micro"
vpc_id = "vpc-e8bfa78d"
subnet_id = "subnet-a135ded7"
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCnyvPtE6dXGtPj8xwuvI54ULkfbnAjAFP3UWZC5WXc3ag/IGCuxLbMvbRRUsn9ytnb5JYDR6tPYqYRrWWjhp8sRqWlxe8Vm6X8iSUSvswKsgKRFKJtgkmHm+qx+3o+r7Mmcf+oxGDlajqAMk1vgX0aUtNMerKjd6KLa5hV3f4MjLEFwzIKUDvdLywCVSWoBsAvY6H9QvbUxMJL1+nMbBusqvV8Wv6RPpEH5T5BFJWf5Krl++olGg9PAD0eCgINLoXgnCjgtH2oYH3GGAgtRs1uErKSRXaJ8Twknq8cTCIW2vLHxd1h/yeGVpaA4ypdeFDtef0fHhds2z5wy+D65E0N gordon@picard"
user_data = """#!/bin/bash
sudo apt update
sudo apt install apache2 -y
echo 'Hello World!' > /var/www/html/index.html"""

# Get the AMI ID of the latest Ubuntu 18.04 version from Canonical
ami = aws.get_ami(
    most_recent="true",
    owners=["099720109477"],
    filters=[
        {
            "name": "name",
            "values": ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"],
        }
    ],
)

# Create an AWS Key Pair
keypair = aws.ec2.KeyPair(
    "keypair-pulumi",
    key_name="keypair-pulumi",
    public_key=public_key,
    tags={"Name": "keypair-pulumi"},
)

# Create an AWS Security group with ingress and egress rules
group = aws.ec2.SecurityGroup(
    "securitygroup-pulumi",
    description="Enable access",
    vpc_id=vpc_id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={"Name": "securitygroup-pulumi"},
)

# Create the webserver EC2 instance
server = aws.ec2.Instance(
    "webserver-pulumi",
    instance_type=size,
    vpc_security_group_ids=[group.id],
    user_data=user_data,
    ami=ami.id,
    key_name=keypair.key_name,
    subnet_id=subnet_id,
    tags={"Name": "webserver-pulumi"},
)

# Show the Public IP address of the webserver EC2 instance
pulumi.export("publicIp", server.public_ip)
