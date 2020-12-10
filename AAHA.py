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
    """
    Save to .json file for debugging
    """
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

    # Make a list of removed  and changed concepts from the 2018 update
    retiredConcepts = []
    retired = updateRelease['refsetReleaseFile']['conceptRefset']['retiredConceptMembers']['retiredConceptMember']
    for concept in retired:
        retiredConcepts.append(concept['conceptMember']['concept']['@conceptId'])
    updateChanged = updateRelease['refsetReleaseFile']['conceptRefset']['changedConceptMembers']['conceptMember']
    for concept in updateChanged:
        retiredConcepts.append(concept['concept']['@conceptId'])
    logging.info("Found " + str(len(retiredConcepts)) + " concepts to INACTIVATED because they are retired or updated.")

    # Remove any concepts that are retired in the updated release file by conceptId
    deactivated = 0
    fullConcepts = fullRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember']
    logging.info("Ready to purge: starting with " + str(len(fullConcepts)) + " active concepts.")
    for count, concept in enumerate(fullConcepts):
        if concept['concept']['@conceptId'] in retiredConcepts:
            fullConcepts.pop(count)
            deactivated += 1
            logging.info("Deactivated " + concept['@displayTerm'])
    logging.info("DEACTIVATED " + str(deactivated) + " we now have " + str(count) + " active terms.")

    # Add any concepts to full release that were in the update
    updateAdded = updateRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember']
    for count, concept in enumerate(updateAdded):
        fullRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember'].append(concept)
        logging.info("ADDED " + concept['@displayTerm'] + " new concepts to the fullRelease dictionary.")
    logging.info(str(count) + " concepts to the active full release dictionary")

    ## Update "changed" concepts from the update file
    # First remove anything changed
    changed = updateRelease['refsetReleaseFile']['conceptRefset']['changedConceptMembers']['conceptMember']
    for count, concept in enumerate(changed):
        fullRelease['refsetReleaseFile']['conceptRefset']['addedConceptMembers']['conceptMember'].append(concept)
        logging.info("Added " + concept['@displayTerm'] + " to the fullRelease.")
    logging.info(str(count) + " concepts UPDATED in the full release dictionary")

    # Export updated file as json
    saveJson(fullRelease, "AAHA_Terms.json")

if __name__ == "__main__":
    main()
