#version v0.1.1

import os
import PySimpleGUI as sg
import json
import pathlib



current_directory = pathlib.Path(__file__).parent.resolve()
input_file = os.path.join(current_directory, "recipes.json")
if os.path.exists(input_file):
    with open(input_file, "r") as infile:
        recipes = json.load(infile)
else: 
    with open(input_file, "w") as infile:
        #create empty recipe file
        pass


def default_layout() -> None: 
        return [
        [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET")],
        [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
        [sg.Button("Calculate", key="CALCULATE", bind_return_key=True), sg.Button("Add Recipe", key="-ADD RECIPE-"), sg.Button("Exit")],
        [sg.Text("", key="OUTPUT")]
    ]

def recipe_layout() -> None:
        return [
        [sg.Text("Adding New Recipe")],
        [sg.Button("Save"), sg.Button("Cancel")],
        [sg.Input("Item Name")],
        [sg.Input("Ingredient 1"), sg.Input("Count")],
        [sg.Input("Ingredient 2"), sg.Input("Count")],
        [sg.Input("Ingredient 3"), sg.Input("Count")],
        [sg.Input("Ingredient 4"), sg.Input("Count")],
        [sg.Input("Ingredient 5"), sg.Input("Count")]
        
]

def output_layout(target: str, count: int) -> None:
    output = get_craft_tree(target, count)
    print("output_layout: ", output)
    totals = get_base_ingredients(output[target])
    treedata = create_output_tree(output)
    return [
        [sg.Button("Close", key="-CLOSE-")],
        [sg.Tree(data=treedata,
            headings=['Total', ],
            auto_size_columns=True,
            select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
            col0_width=40,
            key='-TREE-',
            show_expanded=True,
            enable_events=True,
            expand_x=True,
            expand_y=True,
        )],
        [sg.Text(totals)]
    ]

def get_craft_tree(tgt: dict, total: int, first_pass: bool = True) -> dict:
    recipe_tree = dict()
    recipe_tree["count"] = total
    for k, v in recipes[tgt].items():
        if k in recipes:
            recipe_tree[k] = get_craft_tree(k, total*v, False)
        else:
            recipe_tree[k] = {"count": v*int(total)}
    return {tgt: recipe_tree} if first_pass else recipe_tree

def get_base_ingredients(tgt: dict) -> dict:
    output = dict()
    for k, v in tgt.items():
        if isinstance(v, dict):
            if v["count"] and len(v) == 1:
                if k in output:
                    output[k] += v["count"]
                else:
                    output[k] = 0
                    output[k] += v["count"]
            else:
                temp_dict = get_base_ingredients(v)
                for i, j in temp_dict.items():
                    if i in output:
                        output[i] += j
                    else:
                        output[i] = j

    return output

def create_output_tree(inc: dict, parent: str = "", treedata: sg.TreeData = None) -> sg.TreeData:
    if treedata is None:
        treedata = sg.TreeData()
    for k, v in inc.items():
        if isinstance(v, dict):            
            treedata.Insert(parent, k, k, values=[v["count"]])
            create_output_tree(v, k, treedata)
    return treedata

def calculate_result(target: str, count: int) -> None:
    output_window =  sg.Window("Result", output_layout(target, count), resizable=True)
    while True:
        output_event, output_values = output_window.read()
        if output_event == sg.WIN_CLOSED or output_event == "-CLOSE-":
            break
    output_window.close()

def add_recipe(target: str, inc_recipe: dict):
    recipes[target] = {}
    reduced_values = {k:v for k,v in inc_recipe.items() if ("Ingredient" not in v) if ("Count" not in v)} #remove default values
    for x in range(1, int(len(reduced_values)), 2):
        recipes[target][reduced_values[x].lower()] = int(reduced_values[x+1])
    with open("Icarus_Recipe/recipes.json", "w", encoding = "utf-8") as outfile:
        json.dump(recipes, outfile, ensure_ascii=False, indent=4)

def main() -> None:
    while True:
        event, values = window.read()
        print("main window output: ",event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        match event:
            case "CALCULATE":
                target = values["ITEM_TARGET"].lower()
                count = int(values["ITEM_COUNT"])
                if target == "" or count == "":
                    window["OUTPUT"].update("Please enter values in both target and count")
                    continue
                elif target not in recipes:
                    window["OUTPUT"].update(f"{target} not found in recipe list")
                    continue
                calculate_result(target, count)    
                
            case "-ADD RECIPE-":
                e, v = sg.Window("Input Window", recipe_layout()).read(close=True)
                if e == "Cancel" or e == sg.WIN_CLOSED:
                    continue
                target = v[0].lower()
                del v[0]
                if target in recipes:
                    continue
                add_recipe(target, v)
    
    window.close()



window = sg.Window("Resource Calculator", default_layout())

if __name__ == "__main__":
        main()