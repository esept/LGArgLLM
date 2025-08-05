import math
import os
import streamlit as st
from .AttackNode import AttackNode

class AttackTree:
    def __init__(self):
        self.updates = [
            self.calcul_a_1,
            self.calcul_a_2,
            self.calcul_a_3,
            self.calcul_a_4,
            self.calcul_a_5,
            self.calcul_a_6,
            self.calcul_a_7,
        ]
        self._conf_supps = []
        self._trees = []
        self.edges = []
        self.nodes = []
        self.judgement = []
        self.threshold = 0.9

    def clean(self):
        self._claim = None
        self._datajson = None
        self._conf_supps = []
        self._trees = []
        self.edges = []
        self.nodes = []
        self.judgement = []

    def calcul_a_7(self, CA, CR, conf):
        # nodes = CA
        # nodes = CR
        # nodes = CA + CR
        # the_sum = self.sum_poid_attak_relation(nodes)
        A_sum = self.sum_poid_attak_relation(CA)
        C_sum = self.sum_poid_attak_relation(CR)
        the_sum = A_sum - C_sum

        new_conf = conf - the_sum
        return new_conf


    def get_data(self, claim, datajson, update):
        self._claim = claim
        self._datajson = datajson
        self.update_way = self.updates[update]
        # print(datajson)
        for a_k, a_v in self._datajson['Args'].items():
            # print(a_k)
            self.get_tree(a_k, a_v)

    def get_tree(self, num, s_argu):
        nodes = []
        self._conf_supps.append(s_argu['attacks'][0]['confidence'])
        # print(s_argu['attacks'])
        for i in s_argu['attacks']:
            # print(i)
            an = AttackNode(num, i)
            nodes.append(an)
            # print(s_argu['attacks'][i])
            # nodes.append({an,})
        self.build(nodes)
        self._trees.append(nodes[0])

    def build(self, nodes):
        ids = [node.get_id() for node in nodes]
        edges = []
        for n in nodes[1:]:
            # print(n.get_attack())
            for na in n.get_attack():
                # print(na)
                na_key = list(na.keys())[0]
                # nodes[ids.index(na)].set_next(n)
                poid = na.get(na_key, 0) 
                nodes[ids.index(na_key)].set_next(n, poid)

        for n in nodes:
            for i in n.next:
                edges.append((i.get_id(), n.get_id()))
        gnodes = [n.node for n in nodes]
        self.edges.append(edges)
        self.nodes.append(gnodes)

    def get_first_tree(self):
        data = {
            'id': 'Claim',
            'text': self._claim,
            'confidence': 0.5,
            'attacks': []
        }
        an = AttackNode('The',data)
        self.nodes.append(an.node)
        edges = []
        nodes = [an.node]
        argus = []
        confs = []
        for t in self._trees:
            argus.append(t._text)
            nodes.append(t.node)
            if t.cate == 'P' and t.status == 1:
                confs.append(t.node['newconf'])
            edges.append((t.get_id(),an.get_id()))
        # print(f"nodes {nodes[1]}")
        an.conf = max(confs) if len(confs) != 0 else 0.5
        an.update_gnode()
        # an['newconf'] = max(confs)
        # print(confs)
        return edges, nodes, argus

    def show_tree(self):
        for t in self._trees[:1]:
            t.show_node()

    def update(self):
        for tree in self._trees:
            self.update_node(tree)
            self._conf_supps.append(tree.conf)
            self.judgement.append(self.judge(tree))

    def update_node(self, node):
        if hasattr(node, 'next') and node.next:
            for child_node in node.next:
                if child_node:
                    self.update_node(child_node)
        node.update_gnode(1)
        if len(node.next) > 0:
            CA = [{i: node.next[i]} for i in node.next if i.status == 1]
            CR = [{i: node.next[i]} for i in node.next if i.status == 2]
            # print(node.conf)
            node.conf = self.update_way(CA, CR, node.conf)

            if node.conf > self.threshold :
                status = 2
            elif node.conf == self.threshold :
                status = 0
            elif node.conf < self.threshold :
                if node.conf < 0 :
                    node.conf = -node.conf
                status = 1

            node.update_gnode(status)

    def g_diff_card(self, CA, CR):
        return len(CA) - len(CR)

    def f_sigmoid(self, val):
        return (1 - math.exp(-val)) / (1 + math.exp(-val))

    def get_conf_list(self, nodes):
        confs = [list(item.keys())[0].conf for item in nodes] if nodes else [0]
        return confs

    def g_max_diffval(self, CA, CR):
        max = 0
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        for i in CA:
            for j in CR:
                if i - j > max:
                    max = i-j
        return max

    def g_diff_maxval(self,CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return max(CA) - max(CR)

    def g_diff_sum(self, CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return sum(CA) - sum(CR)

    def g_percentage(self, CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return len(CA)/(len(CA) + len(CR))

    def f_neg(self, val):
        return -val

    def f_pos(self, val):
        return val
        
    def f_split(self, val):
        if val == 1:
            return -1
        else:
            return 1

    def sum_poid_attak_relation(self, nodes):
        the_sum = 0
        for i in nodes:
            for j in i:
                the_sum += j.conf * i[j]
        # the_sum = 
        return the_sum

    def calcul_a_1(self,CA, CR, conf):
        return self.f_sigmoid(self.g_diff_card(CA, CR))

    def calcul_a_2(self,CA, CR, conf):
        return self.f_neg(self.g_max_diffval(CA, CR))

    def calcul_a_3(self,CA, CR, conf):
        return self.f_pos(self.g_diff_maxval(CA, CR))

    def calcul_a_4(self,CA, CR, conf):
        return self.f_sigmoid(self.g_diff_sum(CA, CR))

    def calcul_a_5(self,CA, CR, conf):
        return self.f_split(self.g_percentage(CA, CR))

    def calcul_a_6(self,CA, CR, conf):
        return -1
    

    def judge(self, node):
        if node.status == 1:
            return 'Warranted'
        elif node.status == 2:
            return 'Unwarranted'
        elif node.status == 0:
            return 'Undecided'
