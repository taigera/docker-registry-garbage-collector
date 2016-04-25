# docker-registry-garbage-collector
Garbage Collector for Docker Registry

## Introduction
Manifests are a type of file that describe images. They reference a list of layers and hold metadata about the described image. Manifests can also share layers. Tags, which are labels applied to images, point to manifests. You can reference an image by tag or directly by the hash of the manifest. If you purposefully delete one of those manifests and the image layers referenced by that manifest become orphaned, then they can be removed during the garbage collection job. 

Users may want to remove an image for several reasons. Examples include:
* The image is outdated and there is a new version.
* The image is no longer used.

If a user removes the manifest of an image using the DELETE operation of the Registry API, then it is called a soft deletion. Users won’t be able to access that image, although physically, it it still in the repository, wasting disk space in the server. This script will address this problem, deleting the unreferenced images from the file system and preserving the consistency state of the Registry as it cannot remove manifests that are being used by other layers while the system is online. Also, this script is necessary to be implemented at every server that hosts a Docker Registry because it will free the server disk space, as the API does not allow users to call an operation implemented that deletes images from the file system directly. 

## Dependencies
You need to satisfy the following dependencies in order to compile and run the project 

* A working v2 Docker Registry.  
* Python 2.7 with [pip](https://pip.pypa.io/en/stable/) tool installed.
* Python module installed: [pycurl](http://pycurl.io).
* [delete_docker_registry_image tool](https://github.com/burnettk/delete-docker-registry-image) and [jq](https://stedolan.github.io/jq/download/) installed.
* [PyInstaller](http://www.pyinstaller.org) 3.1.1 or greater

## Install
Follow these instructions to compile and install docker-registry-tool.

1. Clone this repository. 
2. Check that you have satisfied all dependencies by executing the command (use an administrator account or sudo) `python docker_registry_garbage_collector.py` . If the previous command does not return any error, then proceed to the next step.
3. Install PyInstaller as explained [here](http://pythonhosted.org/PyInstaller/)
4. Use PyInstaller to get a binary from the source files. `pyinstaller --onefile docker_registry_garbage_collector.py`
5. You will get the binary file in the dist folder.

## Configuration
The script configuration is made in the `docker_registry_garbage_collector.conf` file. You can open and modify it with a plain text editor. This file must be in the same path where the Garbage Collector script is stored. 

## Run
To run this script, you must execute the binary file using an administrator account with full privilegies (root). Otherwise, you can run it directly from the source file, executing this command using an administrator account with full privilegies (root) `python docker_registry_garbage_collector.py`. The script will delete all images that does not have any tag or reference.

You can make a cronjob in GNU/Linux like this one to repeat the execution of the Garbage Collector at certain hours. Make sure that the binary has executable permissions by issuing `chmod +x docker_registry_garbage_collector`, execute the command `sudo crontab -e` and add the following (make sure to change it according to the path where you stored the script):
```
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h  dom mon dow   command
30 9 * * * /usr/bin/docker_registry_garbage_collector
30 14 * * * /usr/bin/docker_registry_garbage_collector
30 19 * * * /usr/bin/docker_registry_garbage_collector
30 0 * * * /usr/bin/docker_registry_garbage_collector
30 5 * * * /usr/bin/docker_registry_garbage_collector
```


## Users
 * The company [Taiger](http://www.taiger.com) uses this tool in their development processes and infrastructures.

## Greetings
Performed as part of the LPS-BIGGER project, funded by the [Centre for the Development of Industrial Technology (CDTI)](http://www.cienlpsbigger.es)
![CDTI](http://www.cienlpsbigger.es/images/cdti.png)

## Reporting issues
Issues can be reported via the [Github issue tracker](https://github.com/taigers/docker-registry-garbage-collector/issues).

Please take the time to review existing issues before submitting your own to prevent duplicates. Incorrect or poorly formed reports are wasteful and are subject to deletion.

## Submitting fixes and improvements
Fixes and improvements are submitted as pull requests via Github. 

## Related projects
 * [docker-registry-tool](https://github.com/taigers/docker-registry-tool)
 * [docker-registry-manager](https://github.com/taigers/docker-registry-manager)
