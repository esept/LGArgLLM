import streamlit as st
import json


class AttackNode:
    def __init__(self, num, data):
        id_key = 'id' if 'id' in data else 'id:'
        self._id = num + '_' + data[id_key]
        if data[id_key].startswith('A'):
            cate = data['cate']
            self.cate = cate if cate is not None else None
        else:
            self.cate = None
        self._text = data['text']
        conf_key = 'confidence' if 'confidence' in data else "confidence:"
        conf_value = str(data[conf_key]).replace('..','.')
        self.conf = float(conf_value)
        attack_key = 'attacks' if 'attacks' in data else 'attacks:'
        # print(f"attack == {type(data[attack_key])}")
        if type(data[attack_key]) is dict:
            self.attack = [{f'{num}_{n}': data[attack_key][n]} for n in data[attack_key]]
        else:
            self.attack = [{f'{num}_{n}': 0.5 } for n in data[attack_key]]
        # self.attack = [{f'{num}_{n}': data[attack_key][n]} for n in data[attack_key]]
        # self.next = []
        self.next = {}
        self.status = None
        self.node = self.create_gnode()

    def show_node(self):
        st.markdown(f'{self._id} {self.conf}')
        if self.next:
            for n in self.next:
                n.show_node()

    def set_next(self, child):
        self.next.append(child)

    def set_next(self, child, poid):
        self.next[child] = poid

    
    def get_id(self):
        return self._id

    def get_attack(self):
        return self.attack

    def create_gnode(self):
        this_node = {
            'id': self._id,
            'text': self._text,
            'conf': self.conf,
            'newconf': self.conf,
            'status': self.status,
            'cate': self.cate,
        }
        return this_node

    def update_gnode(self, status=1):
        self.node['newconf'] = self.conf
        self.status = status
        self.node['status'] = self.status