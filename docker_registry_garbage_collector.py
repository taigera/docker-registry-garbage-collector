#!/usr/bin/python

import json
import os
from io import BytesIO
from subprocess import call
from ConfigParser import SafeConfigParser

import pycurl


def main():
    """ This function executes the necessary tasks in order to delete the unreferenced images from the file system """
    if not check_configuration():
        return  # The script cannot start if the configuration file is incomplete.
    images_list = get_images_name()
    images_to_be_deleted_list = []
    for image in images_list:
        if get_image_tags(image) is None:
            images_to_be_deleted_list.append(image)
    if len(images_to_be_deleted_list) > 0:
        shutdown_registry()
        for image in images_to_be_deleted_list:
            delete_image(image)
        start_registry()
        print '[INFO] GC execution finished.'


def check_configuration():
    """ Checks if the settings written in 'docker_registry_garbage_collector.conf' are valid or not.
    :return: true if the settings are OK, otherwise returns false.
    """
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_directory = parser.get('docker_registry_garbage_collector', 'RegistryDirectory')
    registry_container_id = parser.get('docker_registry_garbage_collector', 'RegistryContainerId')
    registry_address = parser.get('docker_registry_garbage_collector', 'RegistryAddress')
    registry_port = parser.get('docker_registry_garbage_collector', 'RegistryPort')
    nginx_container_id = parser.get('docker_registry_garbage_collector', 'NginxContainerId')
    registry_username = parser.get('docker_registry_garbage_collector', 'RegistryUsername')
    registry_password = parser.get('docker_registry_garbage_collector', 'RegistryPassword')

    if not registry_directory:
        print '[ERROR] RegistryDirectory variable is empty in the configuration file. The script will not run until ' \
              'you configure the script properly'
        return False
    if not registry_container_id:
        print '[ERROR] RegistryContainerId variable is empty in the configuration file. The script will not run until' \
              ' you configure the script properly'
        return False
    if not registry_address:
        print '[ERROR] RegistryAddress variable is empty in the configuration file. The script will not run until' \
              ' you configure the script properly'
        return False
    if not registry_port:
        print '[ERROR] RegistryPort variable is empty in the configuration file. The script will not run until' \
              ' you configure the script properly'
        return False
    if not nginx_container_id:
        print '[WARNING] NginxContainerId variable is empty in the configuration file.'
    if not registry_username:
        print '[WARNING] RegistryUsername variable is empty in the configuration file.'
    if not registry_password:
        print '[WARNING] RegistryPassword variable is empty in the configuration file.'
    return True


def get_images_name():
    """Get all images from the Docker Registry, returning their names as a list."""
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_address = parser.get('docker_registry_garbage_collector', 'RegistryAddress')
    registry_port = parser.get('docker_registry_garbage_collector', 'RegistryPort')
    registry_username = parser.get('docker_registry_garbage_collector', 'RegistryUsername')
    registry_password = parser.get('docker_registry_garbage_collector', 'RegistryPassword')
    curl = pycurl.Curl()
    data = BytesIO()
    curl.setopt(pycurl.URL, registry_address + ':' + registry_port + '/v2/_catalog')
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    if registry_username and registry_password:
        curl.setopt(pycurl.USERPWD, "%s:%s" % (registry_username, registry_password))
    curl.perform()
    dictionary = json.loads(data.getvalue())
    return dictionary['repositories']


def get_image_tags(image):
    """Get all tags as a list from a Docker Registry Image. If the image does not have any tag,
    then return None
    :param image: input image stored in the Registry"""
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_address = parser.get('docker_registry_garbage_collector', 'RegistryAddress')
    registry_port = parser.get('docker_registry_garbage_collector', 'RegistryPort')
    registry_username = parser.get('docker_registry_garbage_collector', 'RegistryUsername')
    registry_password = parser.get('docker_registry_garbage_collector', 'RegistryPassword')
    curl = pycurl.Curl()
    data = BytesIO()
    curl.setopt(pycurl.URL, registry_address + ':' + registry_port + '/v2/' + image + '/tags/list')
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    if registry_username and registry_password:
        curl.setopt(pycurl.USERPWD, "%s:%s" % (registry_username, registry_password))
    curl.perform()
    dictionary = json.loads(data.getvalue())
    return dictionary['tags']


def shutdown_registry():
    """This function stops the Docker Registry container"""
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_container_id = parser.get('docker_registry_garbage_collector', 'RegistryContainerId')
    nginx_container_id = parser.get('docker_registry_garbage_collector', 'NginxContainerId')
    call(['docker', 'stop', registry_container_id])
    if nginx_container_id:
        call(['docker', 'stop', nginx_container_id])


def start_registry():
    """This function starts the Docker Registry container"""
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_container_id = parser.get('docker_registry_garbage_collector', 'RegistryContainerId')
    nginx_container_id = parser.get('docker_registry_garbage_collector', 'NginxContainerId')
    call(['docker', 'start', registry_container_id])
    if nginx_container_id:
        call(['docker', 'start', nginx_container_id])


def delete_image(image):
    """Delete a image from the Registry by indicating its name
    (see https://github.com/burnettk/delete-docker-registry-image for installing the required system command
    delete_docker_registry_image and https://stedolan.github.io/jq/download/ for installing the required dependency)
    :param image: input image stored in the Registry"""
    parser = SafeConfigParser()
    parser.read('docker_registry_garbage_collector.conf')
    registry_directory = parser.get('docker_registry_garbage_collector', 'RegistryDirectory')
    os.environ["REGISTRY_DATA_DIR"] = registry_directory
    call(['delete_docker_registry_image', '--force', '--image', image])


if __name__ == "__main__":
    main()
