#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright (c) 2020 ContinualAI                                               #
# Copyrights licensed under the MIT License.                                   #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 1-05-2020                                                              #
# Author(s): Vincenzo Lomonaco                                                 #
# E-mail: contact@continualai.org                                              #
# Website: www.continualai.org                                                 #
################################################################################

""" Simple script to generate the research.rst file loading references from
    a bibtex. """

# Python 2-3 compatible
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import bibtexparser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser
import copy
import os
from pprint import pprint

showbib_template = """
.. |[PAPERID][SECTION]| raw:: html

    <button onclick="[PAPERID][SECTION]Function()" id="[PAPERID][SECTION]_btt">Show Bib</button>
    <p style="background-color: #2980b929;"><span id="[PAPERID][SECTION]_more" style="display: none">
        [BIBTEX]
    </span></p>
    <script>
        function [PAPERID][SECTION]Function() {
          var moreText = document.getElementById("[PAPERID][SECTION]_more");
          var btnText = document.getElementById("[PAPERID][SECTION]_btt");

          if (moreText.style.display === "none") {
            btnText.innerHTML = "Hide Bib";
            moreText.style.display = "inline";
          } else {
            btnText.innerHTML = "Show Bib";
            moreText.style.display = "none";
          }
        }
    </script>
    
"""

def remove_mendeley_notice_from_files(filename):
    with open(filename, 'r') as fin:
        data = fin.read().splitlines(True)

    if data[0].startswith("Automatically generated"):
        with open(filename, 'w') as fout:
            fout.writelines(data[5:])

def extract_bibtex(bib_database, id):

    # print("bib_database.entries: ", bib_database.entries)
    pos = None
    for i, entry in enumerate(bib_database.entries):
        if entry['ID'] == id:
            pos = i
            # print(entry['ID'])

    bib_db = copy.deepcopy(bib_database)
    # print(id)
    # print("pos:", pos)
    del bib_db.entries[pos+1:]
    del bib_db.entries[:pos]
    str = bibtexparser.dumps(bib_db)
    return str

def bibtex_string2html(str, remove_abstract=True):

    lines = str.split("\n")
    n = len(lines)
    final_str = ""
    print(lines)
    for i, line in enumerate(lines):

        if remove_abstract and line.strip().startswith("abstract"):
            continue

        if line == "":
            continue
        if i == 0:
            final_line = line + "<br>"
        else:
            final_line = line + "<br>"

        final_str += final_line

    # print(final_str)
    return final_str

def journal_or_booktitle(item):

    if "journal" in item.keys():
        return "*" + item["journal"] + "*"
    elif "booktitle" in item.keys():
        return "*" + item["booktitle"] + "*"
    elif item["ENTRYTYPE"] == "book":
        return "*" + item["publisher"] + "*"
    else:
        print("WARNING: venue missing!!!")
        return ""

def pages_or_void(item):

    if "pages" in item.keys():
        return ", " + item["pages"]
    else:
        return ""

def get_author(item):

    authors_list = item['author'].split(" and ")
    str = ""
    for i, aut in enumerate(authors_list):
        # print(aut)
        surname, name = aut.split(", ")
        authors_list[i] = name + " " + surname
        if i == len(authors_list) -1:
            str += " and " + name + " " + surname
        elif i == 0:
            str +=  name + " " + surname
        else:
            str +=  ', ' + name + " " + surname

    return str

def get_title(item):

    title = item['title'].replace("{", "").replace("}", "")

    if "url" in item.keys():
        return "`" + title + " <" + item["url"]+ ">`__"
    else:
        return title

# settings ---------------------------------------------------------------------
bibtex_path = "bibtex"
full_bib_db = "Continual Learning Papers.bib"
template_file_path = "research_template.rst"
tag2fill = "<TAG>"
output_filename = "research.rst"
# ------------------------------------------------------------------------------

remove_mendeley_notice_from_files(os.path.join(bibtex_path, full_bib_db))

with open(os.path.join(bibtex_path, full_bib_db)) as bibtex_file:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    full_bib_db = bibtexparser.load(bibtex_file, parser=parser)

str2injcet = ""
rst_end_str = ""
for i, bibfile in enumerate(os.listdir(bibtex_path)):
    if bibfile == "Continual Learning Papers.bib":
        continue

    sec_title = bibfile.split("-")[1][:-4]
    with open(os.path.join(bibtex_path, bibfile)) as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    with open(template_file_path) as rf:
        template_str = rf.read()

    pprint(bib_database.entries[0])

    str2injcet += sec_title + \
                 "\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n"
    for item in bib_database.entries:
        print(item)

        str2injcet += "- " + get_title(item) + \
                      " by " + get_author(item) + \
                      ". "+ journal_or_booktitle(item) + \
                      pages_or_void(item) + \
                      ", " + item['year'] + "." + \
                      " |" + item["ID"] + sec_title.replace(" ", "_") + "|" + \
                      "\n"

        # Add bib file button
        bib_str = showbib_template.replace(
            "[BIBTEX]", bibtex_string2html(
                extract_bibtex(full_bib_db, item["ID"])
            )
        )
        bib_str = bib_str.replace("[PAPERID]", item["ID"])
        bib_str = bib_str.replace("[SECTION]", sec_title.replace(" ", "_"))

        rst_end_str += bib_str

    if i != len(os.listdir(bibtex_path)) -1:
        str2injcet += "\n"
    else:
        str2injcet = str2injcet[:-1]

template_str = template_str.replace(tag2fill, str2injcet) + rst_end_str

with open(output_filename, "w") as wf:
    wf.write(template_str)
