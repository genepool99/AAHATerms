#!/usr/bin/env python3

import logging
import json
# from pprint import pprint
import xmltodict
import csv

logging.basicConfig(level=logging.DEBUG)


def saveJson(dict, filename=None):
    jsondump = json.dumps(dict)
    if filename is None:
        filename = "dict.json"
    f = open(filename, "wt")
    f.write(jsondump)
    f.close()


def xmldict(path):
    with open(path, "rb") as file:
        return xmltodict.parse(file)


def findRetired(release):
    """
    Find all the retired and updated concepts and make a list of their
    ID numbers.

    Args:
        release(dictionary): a release

    Returns:
        type: list of IS numbers
    """

    retiredConcepts = []

    retired = (release["refsetReleaseFile"]["conceptRefset"]
               ["retiredConceptMembers"]["retiredConceptMember"])
    for concept in retired:
        retiredConcepts.append(concept["conceptMember"]
                                      ["concept"]["@conceptId"])

    updated = (release["refsetReleaseFile"]["conceptRefset"]
                      ["changedConceptMembers"]["conceptMember"])

    for concept in updated:
        retiredConcepts.append(concept["concept"]["@conceptId"])
    logging.info("Found " + str(len(retiredConcepts))
                 + " concepts that are retired or updated.")
    return retiredConcepts


def removeConcepts(release, ids):
    """
    From a release remove any concepts whos ID matches an ID in the ids list.

    Args:
        release (dictionary): a release dictionary

    Returns:
        type: dictionary
    """

    deactivated = 0
    concepts = (release["refsetReleaseFile"]["conceptRefset"]
                       ["addedConceptMembers"]["conceptMember"])
    logging.info("Removing: " + str(len(concepts)) + " active concepts.")
    for count, concept in enumerate(concepts):
        if concept["concept"]["@conceptId"] in ids:
            concepts.pop(count)
            deactivated += 1
            logging.info("Deactivated " + concept["@displayTerm"])
    logging.info
    (("Removed {deactivated} concepts.").format(deactivated=deactivated))
    logging.info
    (("{count} active concepts.").format(count=count))
    return release


def addConcepts(release, update):
    """
    Add any concepts from the update to the release.

    Args:
        release (dictionary): the release to be updated
        update (dictionary): the release that has the updates

    Returns:
        type: dictionary
    """

    for count, concept in enumerate(update):
        (release["refsetReleaseFile"]["conceptRefset"]
                ["addedConceptMembers"]["conceptMember"].append(concept))
        logging.info("ADDED " + concept["@displayTerm"]
                     + " new concepts to the fullRelease dictionary.")
    logging.info(str(count) + " concepts added.")
    return release


def createCsv(release, filename):
    """
    Create a CSV file with all active concepts in a release. Include conceptID,
    concept display name, and alternitive terms

    Args:
        releasse (dictionary): the concept dictionary to export
        filename (string): the csv filename

    Returns:
        type: description

    """

    with open(filename, mode="w") as csvFile:
        writer = csv.writer(csvFile, delimiter=",",
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["moduleID", "displayTerm", "addedLanguagePref"])
        concepts = (release["refsetReleaseFile"]["conceptRefset"]
                           ["addedConceptMembers"]["conceptMember"])
        for concept in concepts:
            moduleID = concept["concept"]["@conceptId"]
            displayTerm = concept["@displayTerm"]
            addedLanguage = ""
            # if there are added language preferences add them
            if (concept["concept"]["languagePreferences"]
                    ["addedLanguagePreferences"] is not None):
                languagePreferences = (concept["concept"]
                                              ["languagePreferences"]
                                              ["addedLanguagePreferences"]
                                              ["languagePreference"])
                if "description" not in languagePreferences:
                    for preference in languagePreferences:
                        if preference["@designation"] == "Acceptable":
                            term = preference["description"]["@term"]
                            addedLanguage += " " + term

            writer.writerow([moduleID, displayTerm, addedLanguage])


def main():
    """
    Parse AAHA Terms main and update files, reconsile the two, then and output
    a useful CSV file of active concepts and alternitive concept terms.
    """
    # Convert AAHA fulllist and 2018 update xml files to dictionaries
    fullRelease = xmldict("ReleaseFile_full_20181001.xml")
    updateRelease = xmldict("ReleaseFile_20180401to20181001.xml")

    # Make a list of removed and changed concept IDs from the 2018 update
    retiredConcepts = findRetired(updateRelease)

    # Remove any concepts from that are retired or updated in the full release
    # file
    fullRelease = removeConcepts(fullRelease, retiredConcepts)

    # Add any new concepts to full release that were in the update
    updateAdded = (updateRelease["refsetReleaseFile"]["conceptRefset"]
                                ["addedConceptMembers"]["conceptMember"])
    fullRelease = addConcepts(fullRelease, updateAdded)

    # Update "changed" concepts in full release from the update file
    changed = (updateRelease["refsetReleaseFile"]["conceptRefset"]
                            ["changedConceptMembers"]["conceptMember"])
    fullRelease = addConcepts(fullRelease, changed)

    # export updated file as json
    saveJson(fullRelease, "AAHA_Terms.json")

    # Then make an simple CSV
    createCsv(fullRelease, "terms.csv")


if __name__ == "__main__":
    main()
