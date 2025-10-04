---
Project Name: LoGicArgLLM
Description: Reasoning Framework  
Date: 2025-09-23
Tech Stack:
Path: /Users/xuzy/Main/1-Code/LAM/1p-LAM-Python-LoGicArgLLM
---

### Utilisation 
./go.sh : 
Run the web UI

./run.sh : 
Fetch data for a single dataset; once completed, you can use ./go.sh to perform reasoning on the data

### Folder
- configs: Stores prompts
- data: Stores datasets and the generated arguments; each run reads the latest res for storage/reasoning
- result: Stores the results of a dataset, from which condition/semantic weights are computed



### Architecture 
.
LGArgLLM
├── Argument_Generator.py # Uses an LLM to generate supporting and attacking arguments and structures them into JSON.
├── Evaluator.py # Evaluates correctness counts and accuracy of semantics, displaying results in the UI.
├── LGArgLLM_pipeline.py # Controls the execution mode (UI or new dataset) and orchestrates argument generation and reasoning.
├── Ranker.py # Computes condition and semantic weights from result files for aggregation.
├── Reasoner.py # Executes reasoning over conditions and semantics, applying multiple aggregation strategies.
├── __init__.py 
│
├── ARTree # Argumentative Reasoning Tree 
│   ├── ART_Node.py # Represents a single argument node with text, category, confidence, and attack relations.
│   ├── ART_Reasoner.py # Performs logical condition reasoning (Cond1–11, s/p/m), with some conditions handled by an LLM.
│   ├── ART_Tree.py # Builds the attack reasoning tree from claims and arguments, and updates confidence values.
│   ├── ART_Updater.py # Provides multiple update strategies to adjust node confidence and status based on children.
│   ├── ART_Viser.py # Visualizes argumentation trees and reasoning in Streamlit using Graphviz.
│   └── __init__.py
│
├── LLM_Manager
│   ├── DS_manager.py # Interfaces with the DeepSeek API, handling requests and responses.
│   ├── LLM_manager.py # Abstract base class that defines prompt loading and unified LLM call interfaces.
│   ├── Sflow_manager.py # Interfaces with the SiliconFlow API, handling HTTP requests and responses.
│   └── __init__.py
│
└── streamlit_UI
    ├── Base_page.py # Abstract base class for pages, providing common data handling and tree construction methods.
    ├── Page_DemoSingle.py # Demo page for a single claim, showing generation, reasoning, and visualization.
    ├── Page_Evaluation.py # Evaluation page for datasets, supporting batch execution and result saving.
    ├── UIManager.py # Manages UI pages and LLM selection, orchestrating page execution.
    └── __init__.py

