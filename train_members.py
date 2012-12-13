"""
    Run this script from the root of the repo to train the BetaFace API
    with the faces of the current AmI lab members.
"""
import logging
import os

from pybetaface.api import BetaFaceAPI


def get_ami_lab_members():
    """ Get a list of the AmI lab members. For each member, there is a
        subdir in the 'members' folder.

        Returns a list of strings of the form x@ami-lab.ro

    """
    members_folder = 'members'
    return [name for name in os.listdir(members_folder)
            if os.path.isdir(os.path.join(members_folder, name))]

def get_headshots_for_member(member):
    """ Given an AmI lab member, get the available examples for that member.

        Returns a list of relative paths to the available headshots of that
        ami-lab member. The actual headshots are images stored in the
        members/member-name folder as files.

    """
    member_folder = 'members/%s' % member
    return [os.path.join(member_folder, name)\
            for name in os.listdir(member_folder)\
            if os.path.isfile(os.path.join(member_folder, name))]

def train_api_with_members():
    """ Trains the BetaFace API with all the faces of the existing
        AmI lab members. """

    client = BetaFaceAPI()

    members = get_ami_lab_members()
    for member in members:
        member_headshots = get_headshots_for_member(member)
        for headshot in member_headshots:
            client.upload_face(headshot, member)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    train_api_with_members()