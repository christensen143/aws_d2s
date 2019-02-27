# aws_d2s
Convert your AWS dedicated instances to shared (default) instances.

## Case
Previous to 2017 dedicated instances were necessary for HIPAA compliance. Here is a link to the announcement from AWS that dedicated instances were no longer a requirement for HIPAA compliance:

https://aws.amazon.com/blogs/apn/aws-hipaa-program-update-removal-of-dedicated-instance-requirement/

The process for converting an instance from dedicated to shared (default) is fairly straightforward but can be time consuming and error prone. My testing showed that you can do this with about 8-10 minutes of downtime. As with anything that I have to repeat more than twice, I came up with a script to handle this for me. The script brings downtime down to 2-3 minutes.

## Instructions
1. Clone this repo
2. I suggest opening a virtual environment to keep your Python packages clean.
3. Install the required modules:
    $ pip3 install requirements.txt
4. Execute the program:
    $ python3 app.py -h
    useage: python3 app.py -i <Instance ID> -r <Region Name> -u <Instance Route53 URL (Optional)> -z <Route53 hosted zone name (Optional)>

    Example:
    $ python3 app.py -i *instance_id* -r us-east-1 -u subdomain.domain.com -z domain.com
5. The purpose of providing the instance url and hosted zone name is to change the Route53 resource for your instance. This is necessary if you have Route53 DNS setup for your instance as the script creates a new instance with a new private ip address. If you don't provide these arguments the script will skip DNS changes.

## TODO
1. Make better use of functions.
2. Allow multiple instances.
