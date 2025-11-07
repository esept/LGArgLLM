import json
import os


if __name__ == '__main__':
    datas = [os.path.join("./data",i) for i in os.listdir("./data") if i != 'ELSE']
    max_tree = 0
    min_tree = 10
    max_tree_node = 0
    min_tree_node = 100
    max_forest_node = 0
    min_forest_node = 1000
    for data in datas:
        if os.path.isdir(data):
            sources = [res for res in os.listdir(data) if os.path.isdir(os.path.join(data,res))]
            max_idx = max([int(i.split('_')[-1]) for i in sources])
            data_folder = os.path.join(data, f'res_{max_idx}')
            for instance in os.listdir(data_folder):
                if not instance.endswith('json'):
                    continue
                json_path = os.path.join(data_folder, instance)
                with open(json_path, 'r') as f:
                    content = f.read()
                    jdata = dict(json.loads(content))
                all_nodes = 0
                nb_tree = len(jdata['Args'])

                if nb_tree > max_tree:
                    max_tree = nb_tree
                if nb_tree < min_tree:
                    min_tree = nb_tree

                for tree in jdata['Args'].keys():
                    nb_node = len(jdata['Args'][tree]['attacks'])
                    all_nodes += nb_node
                    if nb_node > max_tree_node:
                        max_tree_node = nb_node
                    if nb_node < min_tree_node:
                        min_tree_node = nb_node

                if all_nodes > max_forest_node :
                    max_forest_node = all_nodes
                if all_nodes < min_forest_node:
                    min_forest_node = all_nodes

    print('Tree',max_tree, min_tree)
    print('Node', max_tree_node, min_tree_node)
    print('all_Node', max_forest_node, min_forest_node)