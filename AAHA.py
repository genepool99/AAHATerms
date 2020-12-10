#!/usr/bin/env python3
"""
Script to parse AAHA Terms and update the full list to the latest version
"""

import logging
import json
from pprint import pprint
import xmltodict

logging.basicConfig(level=logging.DEBUG)

def saveJson(dict, filename=None):
'''
    Save to .json file for debugging
'''
    jsondump = json.dumps(dict)
    if filename is None:
        filename = 'dict.json'
    f = open(filename,"wt")
    f.write(jsondump)
    f.close()

def main():
    # Convert AAHA fulllist and 2018 update xml files to dictionaries
    with open('ReleaseFile_full_20181001.xml', 'rb') as file:
        fullRelease = xmltodict.parse(file)
        # saveJson(fullRelease, 'full.json')
    with open('ReleaseFile_20180401to20181001.xml', 'rb') as file:
        updateRelease = xmltodict.parse(file)
        # saveJson(updateRelease, 'update.json')

    # Make a list of removed concepts from the 2018 update
    retiredConcepts = []
    for concept in updateRelease['refsetReleaseFile']['conceptRefset']['retiredConceptMembers']['retiredConceptMember']:
        retiredConcepts.append(concept['conceptMember']['concept']['@conceptId'])
    logging.info("Found " + str(len(retiredConcepts)) + " retired concepts.")

    # Remove any concepts that are retired in the updated release file
    deactivated = 0
    fullConcepts = fullRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember']
    for count, concept in enumerate(fullConcepts):
        if concept['concept']['@conceptId'] in retiredConcepts:
            concept['@active'] = 0
            deactivated += 1
            logging.info("Deactivated " + concept['@displayTerm'])
    logging.info("Deactivated " + str(deactivated) + " of the " + str(count) + " active terms.")

    # Add any concepts to full release that were in the update
    updateAdded = updateRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember']
    for count, concept in enumerate(updateAdded):
        fullRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember'].append(concept)
        logging.info("Added " + concept['@displayTerm'] + " to the fullRelease.")
    logging.info(str(count) + " concepts to the active full release dictionary")

    # Update "changed" concepts from the update file



if __name__ == "__main__":
    main()
