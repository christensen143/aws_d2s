# aws_d2s
Convert your AWS dedicated instances to shared (default) instances.

## Case
Previous to 2017 dedicated instances were necessary for HIPAA compliance. Here is a link to the announcement from AWS that dedicated instances were no longer a requirement for HIPAA compliance:

https://aws.amazon.com/blogs/apn/aws-hipaa-program-update-removal-of-dedicated-instance-requirement/

The process for converting an instance from dedicated to shared (default) is fairly straightforward but can be time consuming and error prone. My testing showed that you can do this with about 8-10 minutes of downtime. As with anything that I have to repeat more than twice, I came up with a script to handle this for me.

## Instructions
1. Clone this repo
2. I suggest opening a virtual environment to keep your Python packages clean.
3. Install the required modules:
    $ pip3 install requirements.txt
4. Set the environment variable for your AWS region if it is not already set:
    $ export AWS_DEFAULT_REGION=*your-region*
5. Execute the program with instance id for the instance you want to convert:
    $ python3 app.py *instance_id*

## TODO
1. Make better use of functions.
2. Allow region to be either a command line argument or environment variable.
3. Allow multiple instances.
