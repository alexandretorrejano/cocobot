import os
import multiprocessing
import psutil
import time

# Function to build a nested dictionary representing the file tree
def build_file_tree(folder_path):
    tree = {}
    for entry in os.scandir(folder_path):
        if entry.is_dir():
            tree[entry.name] = build_file_tree(entry.path)
        else:
            tree[entry.name] = None

    tree.pop("desktop.ini", None)
        
    return tree

# Function to convert the file tree into options for the tree_select widget
def tree_to_treeselect(tree):
    def convert_node(name, children):
        return {
            "label": name,  # Visible label in the tree
            "value": name,  # Internal value for selection
            "children": [convert_node(k, v) for k, v in children.items()] if children else []
        }
    return [convert_node(k, v) for k, v in tree.items()]



# Debugging print
def extract_selected_paths(nodes, selected_values, parent=""):
    selected_paths = []
    for node in nodes:
        current_path = os.path.join(parent, node["label"])
        print(f"Path before replace: {current_path}")  # Debugging print
        current_path = str(current_path).replace("\\", "/")
        print(f"Path after replace: {current_path}")  # Debugging print
        
        if node["value"] in selected_values and '.' in node["label"]:
            selected_paths.append(current_path)
        
        if "children" in node:
            selected_paths.extend(extract_selected_paths(node["children"], selected_values, current_path))
    
    return selected_paths


