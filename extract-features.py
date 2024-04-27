#! /usr/bin/python3

import sys
import pickle
from os import listdir

from xml.dom.minidom import parse

from deptree import *
#import patterns


## ------------------- 
## -- Convert a pair of drugs and their context in a feature vector

def common_root(tree,dditype,common_root_dict):
   for n in tree.get_nodes():
      if "ROOT"== tree.get_rel(n):
         lemma = tree.get_lemma(n)
         if dditype not in common_root_dict:
            common_root_dict[dditype] = set()
            common_root_dict[dditype].add(lemma)
         else:
            common_root_dict[dditype].add(lemma)
   return common_root_dict

def extract_features(tree, entities, e1, e2,common_root_dict) :
   feats = set()
   # get head token for each gold entity
   tkE1 = tree.get_fragment_head(entities[e1]['start'],entities[e1]['end'])
   tkE2 = tree.get_fragment_head(entities[e2]['start'],entities[e2]['end'])
   if tkE1 is not None and tkE2 is not None:
      
      try:
         eib = False
         for tk in range(tkE1+1, tkE2) :
            if tree.is_entity(tk, entities):
               eib = True 
         
         # feature indicating the presence of an entity in between E1 and E2
         feats.add('eib='+ str(eib))

         before_tags, between_tags, after_tags = [], [], []
         for n in tree.get_nodes():
            if "subj" in tree.get_rel(n):
               subj_node = n
               feats.add('wsubj=' + tree.get_word(n))
               feats.add("lsubj=" + tree.get_lemma(n))
               feats.add("tsubj=" + tree.get_tag(n))
            if "ROOT"== tree.get_rel(n):
               root_node = n
               root_lemma = tree.get_lemma(n)
               adv_root, eff_root, int_root, mech_root = ["False"] * 4
               if root_lemma in common_root_dict["advise"]:
                  adv_root = "True"
               if root_lemma in common_root_dict["effect"]:
                  eff_root = "True"
               if root_lemma in common_root_dict["int"]:
                  int_root = "True"
               if root_lemma in common_root_dict["mechanism"]:
                  mech_root = "True"

               feats.add('adv_root=' + adv_root)
               feats.add('eff_root=' + eff_root)
               feats.add('int_root=' + int_root)
               feats.add('mechanism_root=' + mech_root)

               feats.add('wroot=' + tree.get_word(n))
               feats.add("lroot=" + root_lemma)
               feats.add("troot=" + tree.get_tag(n))

            if n < tkE1:
               if tree.tree.nodes[n]["tag"][0] in ['N', 'V', 'J', 'R']:
                  before_tags.append(tree.tree.nodes[n]["tag"][0]) 

            elif tkE1 <= n < tkE2:
               if tree.tree.nodes[n]["tag"][0] in ['N', 'V', 'J', 'R']:
                  between_tags.append(tree.tree.nodes[n]["tag"][0])

            elif n > tkE2:
               if tree.tree.nodes[n]["tag"][0] in ['N', 'V', 'J', 'R']:
                  after_tags.append(tree.tree.nodes[n]["tag"][0])
         
         feats.add('tags_pre='+",".join(before_tags))
         feats.add('tags_bet='+",".join(between_tags))
         feats.add('tags_aft='+",".join(after_tags))

         # features about paths in the tree
         lcs = tree.get_LCS(tkE1,tkE2)
         lcs_word = tree.get_word(lcs)
         lcs_lemma = tree.get_lemma(lcs).lower()
         lcs_tag = tree.get_tag(lcs)
         feats.add("wlcs=" + lcs_word)
         feats.add("llcs=" + lcs_lemma)
         feats.add("tlcs=" + lcs_tag)

         if subj_node and root_node and lcs:
            path_subj_root = tree.get_up_path(subj_node,root_node)
            path_subj_root = "<".join([tree.get_rel(x) for x in path_subj_root])
            path_root_lcs = tree.get_down_path(root_node,lcs)
            path_root_lcs = ">".join([tree.get_rel(x) for x in path_root_lcs])
            path_subj_lcs = path_subj_root+"<"+tree.get_rel(root_node)+">"+path_root_lcs    
            feats.add("pathsubjlcs="+path_subj_lcs)

         path1 = tree.get_up_path(tkE1,lcs)
         path1_list = []
         for j,n in enumerate(path1):
            node_word = tree.get_word(n)
            node_lemma = tree.get_lemma(n).lower()
            node_tag = tree.get_tag(n)
            feats.add(f"path1n{j}w="+node_word)
            feats.add(f"path1n{j}l="+node_lemma)
            feats.add(f"path1n{j}t="+node_tag)
            path1_list.append(tree.get_rel(n))

         path1 = "<".join(path1_list)
         
         feats.add("path1="+path1)

         path2 = tree.get_down_path(lcs,tkE2)
         path2_list=[]
         for j,n in enumerate(path2):
            node_word = tree.get_word(n)
            node_lemma = tree.get_lemma(n).lower()
            node_tag = tree.get_tag(n)
            feats.add(f"path2n{j}w="+node_word)
            feats.add(f"path2n{j}l="+node_lemma)
            feats.add(f"path2n{j}t="+node_tag)
            path2_list.append(tree.get_rel(n))

         path2 = ">".join(path2_list)
         
         feats.add("path2="+path2)

         path = path1+"<"+tree.get_rel(lcs)+">"+path2      
         feats.add("path="+path)
               
      except:
         return set()
   
   return feats


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
## --

# directory with files to process
datadir = sys.argv[1]
# process each file in directory

with open("common_root_dict.pkl", 'rb') as f:
    common_root_dict = pickle.load(f)
for f in listdir(datadir) :

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir+"/"+f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences :
        sid = s.attributes["id"].value   # get sentence id
        stext = s.attributes["text"].value   # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents :
           id = e.attributes["id"].value
           offs = e.attributes["charOffset"].value.split("-")           
           entities[id] = {'start': int(offs[0]), 'end': int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1 : continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
       
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if (ddi=="true") : dditype = p.attributes["type"].value
            else : dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction
            feats= extract_features(analysis,entities,id_e1,id_e2,common_root_dict) 
            #common_root_dict = common_root(analysis,dditype,common_root_dict)
            # resulting vector
            if len(feats) != 0:
              print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")

'''with open("common_root_dict.pkl",'wb') as f:
   pickle.dump(common_root_dict, f)'''
 

