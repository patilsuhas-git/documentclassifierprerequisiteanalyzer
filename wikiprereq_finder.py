from flask import Flask, request, render_template, json, redirect, jsonify
import json
import subprocess, shlex
import sys
import os

with open('title_links.json') as title_link_dict:
    title_links = json.load(title_link_dict)
system_encoding = sys.stdout.encoding

def weights(conceptA, conceptB):
    if (conceptA in title_links[conceptB]):
        return 1
    return 0

def relation(conceptA, conceptB):
    if (conceptB in title_links[conceptA]):
        return 1
    return 0

def ref_distance(conceptA, conceptB):
    total_weightsA, total_weightsB = 0, 0
    ref_dist = 0.0

    for article in title_links:
        total_weightsA += weights(article, conceptA)
        total_weightsB += weights(article, conceptB)

    if total_weightsA == 0:
        total_weightsA += 1
    elif total_weightsB == 0:
        total_weightsB += 1

    for article in title_links:
        ref_dist += relation(article, conceptB)*weights(article, conceptA)/total_weightsA - relation(article, conceptA)*weights(article, conceptB)/total_weightsB
    if (ref_dist != 0):  # how are the print statements working?
        try:
            print ("The distance between", conceptA, "and", conceptB, "is ", ref_dist)
        except:
            print ("Cannot print concept")
    return (ref_dist, conceptB)

def get_concepts(filename):
    # make this platform independent
    cmd = 'gswin64c -q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE -c save -f ps2ascii.ps ' + filename + ' -c quit > output.txt'
    os.system(cmd)
    with open('output.txt') as fp:
        keywords = fp.read().split()
    # future scope -> check bigrams and trigrams and also improve simple word checking using search library
    concepts = [concept for concept in set(keywords) if title_links.get(concept)]
    concept_prereq = {}
    if (concepts != []):
        for concept in concepts:    # find prerequisites for each concept
            concept_prereq[concept] = {}
        sys.stdout.write('\n'+str(concept_prereq)+'\n')
        # simplifying assumption that the links that you have in your page contain the thing that links to you
        # for concept in concept_prereq:
        recursive_concept_fill(concept_prereq, depth=0, all_concepts=concepts)# depth limited recursive concept fetch
        return concept_prereq
    return concepts  # if none exist

def recursive_concept_fill(concept_dict, depth, all_concepts):
    if (depth >= 5):
        return
    for concept in concept_dict:
        # max concept is the prerequisite for that concept
        print ('concept is ', concept, 'with dict', concept_dict)
        if (title_links.get(concept) != None):
            # super rare case
            list_articles = [ref_distance(concept, article) for article in title_links[concept] if title_links.get(article)]
            if list_articles != []:
                max_concept = max(list_articles , key=lambda x: x[0])
                # need to verify the pruning logic
                if (max_concept and max_concept[1] not in str(all_concepts)):
                    all_concepts.append(max_concept[1])   # unique concept that doesn't exist anywhere in the dicitonary
                    concept_dict[concept][max_concept[1]] = {}
                    recursive_concept_fill(concept_dict[concept], depth=depth+1, all_concepts=all_concepts)