

DJANGO

MYSQL


ELASTIC BEANSTALK

ELASTIC FILE SYSTEM

ComSem uses the AWS elastic file system to store audio files. .ebextensions/storage-efs-mountfilesystem.config is the configuration file to automatically mount the file system each time the elastic beanstalk environment in
deployed.

There is an Alias added to the httpd config file (/etc/httpd/conf/httpd.conf) that allows the app to access the
directory /efs which is where the elastic file system instance is mounted.


TO DO
