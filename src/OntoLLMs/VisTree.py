import streamlit as st
import graphviz

COLOR = ["#c912a5", "#12c99e","#34495e"]
STATUS = ['Undecided', 'Accepted', 'Rejected']


class VisTree:
    def _init__(self):
        self.edges = None

    def show_status_legend(self):
        """在graphviz图中展示状态颜色图例"""
        dot = graphviz.Digraph(
            name='legend',
            graph_attr={
                'rankdir': 'LR',
                'margin': '0',
                'pad': '0.5'
            },
            node_attr={
                'shape': 'box',
                'style': 'filled',
                'fontname': 'Arial',
                'fontsize': '10',
                'width': '1',
                'height': '0.5'
            }
        )

        for i, (color, status) in enumerate(zip(COLOR, STATUS)):
            dot.node(
                f'legend_{i}',
                label=status,
                fillcolor=color,
                fontcolor='white'
            )

        st.sidebar.graphviz_chart(dot)

    def get_data(self, edges, org_nodes):
        self.edges = edges
        # print(self.edges)
        # print(org_nodes)
        # print(len(edges), len(org_nodes))
        # st.markdown(f"{1}: **{org_nodes[1][0]['text']}**")
        # print(org_nodes)
        for i in range(len(self.edges)):
            # print(org_nodes[i])
            # print('---'*20)
            self.new_container(self.edges[i], org_nodes[i])

    def set_judge_color(self, jd):
        # JCOLOR = ["#c912a5", "#12c99e","#34495e"]
        JCOLOR = ["#d67ba8", "#9da81b", "#21a39a"]
        jcolor = ["#12c99e"]
        for j in jd:
            if j == 'Warranted':
                jcolor.append(JCOLOR[0])
            elif j == 'Unwarranted':
                jcolor.append(JCOLOR[1])
            else:
                jcolor.append(JCOLOR[2])
        return jcolor

    def draw_first_tree(self, edges, nodes, jds, res):
        with st.container():
            dot = graphviz.Digraph(
                # name=f"tree_{name}",
                engine='dot',  # 使用dot引擎，适合层次结构
                graph_attr={
                    'rankdir': 'BT',  # 自下而上布局
                    'concentrate': 'true',  # 合并边以减少混乱
                    'splines': 'ortho',  # 直角边，更整洁
                    'nodesep': '0.3',  # 节点水平间距
                    'ranksep': '0.3',  # 层级垂直间距
                }
            )
            jcolor = self.set_judge_color(jds)
            # for node,jc in zip(nodes,jcolor):
            for i in range(len(nodes)):
                node = nodes[i]
                jc = jcolor[i]
                if i == 0:
                    label = f"{node['id']}\n{node['conf']:.2f}➡️{node['newconf']:.2f}\n{res}"
                    if res:
                        jc = '#0e8f0e'
                    else:
                        jc = '#620e9e'
                else:
                    label = f"{node['id']} {node['cate']}\n{node['conf']:.2f}➡️{node['newconf']:.2f}\n{jds[i - 1]}"
                # thejd = jds[i]
                dot.node(
                    f"{node['id']}",
                    # label=f"{node['id']} {self.set_status(node['status'])} \n{node['conf']:.2f}➡️{node['newconf']:.2f}",
                    label=label,
                    width='1',
                    height='0.8',  # 高度略小于宽度，美观
                    style='filled',
                    # fillcolor=node_color,
                    color=jc,  # 深灰色边框
                    shape='rect',  # 使用矩形节点
                    fontcolor='white',  # 白色文字
                    penwidth='1.5',  # 边框粗细
                    fixedsize='true'
                )
            # for (src, dst) in edges[-1]:
            #     dot.edge(src, dst, color='red')
            EDGE_COLORS = {
                'P': '#FF5733',  # 支持观点的橙色
                'S': '#33A1FF'  # 反对观点的蓝色
            }
            for ((src, dst), nn) in zip(edges, nodes[1:]):
                if nn['cate'] == 'P':
                    color = EDGE_COLORS['P']
                else:
                    color = EDGE_COLORS['S']
                dot.edge(src, dst, color=color)

            st.graphviz_chart(dot)
        st.markdown('---')


    def new_container(self, edges, nodes):

        org_supported = nodes[0]

        with st.container():
            st.markdown(f"**{org_supported['text']}**")
            st.markdown(f"{org_supported['conf']:.2f} ➡️ {org_supported['newconf']:.2f}")
            self.set_columns(edges, nodes)
        st.markdown('---')

    def draw_tree(self, edges, nodes):
        dot = graphviz.Digraph(
            # name=f"tree_{name}",
            engine='dot',  # 使用dot引擎，适合层次结构
            graph_attr={
                'rankdir': 'BT',  # 自下而上布局
                'concentrate': 'true',  # 合并边以减少混乱
                'splines': 'ortho',  # 直角边，更整洁
                'nodesep': '0.3',  # 节点水平间距
                'ranksep': '0.3',  # 层级垂直间距
            }
        )

        for node in nodes:
            dot.node(
                f"{node['id']}",
                # label=f"{node['id']} {self.set_status(node['status'])} \n{node['conf']:.2f}➡️{node['newconf']:.2f}",
                label=f"{node['id']}\n{node['conf']:.2f}➡️{node['newconf']:.2f}",
                width='1',
                height='0.8',  # 高度略小于宽度，美观
                style='filled',
                # fillcolor=node_color,
                color=COLOR[node['status']],  # 深灰色边框
                shape='rect',  # 使用矩形节点
                fontcolor='white',  # 白色文字
                penwidth='1.5',  # 边框粗细
                fixedsize='true'
            )
        # for (src, dst) in edges[-1]:
        #     dot.edge(src, dst, color='red')

        for src, dst in edges:
            dot.edge(src, dst, color='red')
        st.graphviz_chart(dot)
    '''绘制树结构'''

    def set_status(self, status):
        if status == 0:
            return f'🆄 + {status}'
        elif status == 1:
            return f'🅰️ + {status}'
        elif status == 2:
            return f'🆁 + {status}'
    '''在 node 里显示负号的状态'''

    def set_columns(self, edges, nodes):
        tree, info = st.columns([0.3, 0.7])
        with tree:
            # st.markdown('ORG TREE')
            self.draw_tree(edges, nodes)
        # with new_tree:
        #     st.markdown('NEW TREE')
        with info:
            st.markdown('Informations')
            for i in nodes[1:]:
                st.markdown(f"**{i['id']}** {i['conf']:.2f} ➡️ {i['newconf']:.2f}")
                st.write(f"**Text**: {i['text']}")
                # with st.expander(f"**{i['id']}** {i['conf']:.2f} ➡️ {i['newconf']:.2f}"):
                #     st.write(f"**Text**: {i['text']}")
    '''设置页面布局'''