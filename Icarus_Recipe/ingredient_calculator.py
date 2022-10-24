import os, sys
import PySimpleGUI as sg
import json
from github import Github
import config

version = 0.16
#github_link = "https://github.com/Kyiki-Nasoka/Icarus-Recipe"

#g = Github(config.GIT_API)
#user = g.get_user()
#repo = user.get_repo("Icarus-Recipe")
#current_version = float(repo.get_contents("Icarus_Recipe/version.txt").decoded_content)

#if version < current_version:
#    e, v = sg.Window("Update Available", [[sg.Text(f"current version {version}, available version {current_version}. Please visit the URL below and select {current_version} from tags")],
#        [sg.Input(default_text=github_link)],
#        [sg.Button("OK")]]).read(close=True)


if getattr(sys, 'frozen', False):
    current_directory = os.path.dirname(sys.executable)
elif __file__:
    current_directory = os.path.dirname(__file__)
recipe_file = os.path.join(current_directory, "recipes.json")

if os.path.exists(recipe_file):
    print(f"opening {recipe_file} to get saved recipes")
    with open(recipe_file, "r") as infile:
        recipes = json.load(infile)
else: 
    recipes = dict()

def default_layout() -> None: 
        return [
        [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET", focus=True)],
        [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
        [sg.Button("Calculate", key="CALCULATE", bind_return_key=True), sg.Button("Add Recipe", key="-ADD RECIPE-"),
            sg.Button("Delete Recipe", key="-DELETE-"), sg.Button("Keep On Top", key="-KEEPTOP-"), sg.Button("Exit")],
        [sg.Text("", key="OUTPUT")]
    ]

def recipe_layout(cur_item: str) -> None:
        return [
        [sg.Text("Adding New Recipe")],
        [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")],
        [sg.Input(cur_item, focus=True)],
        [sg.Input("Ingredient 1"), sg.Input("Count")],
        [sg.Input("Ingredient 2"), sg.Input("Count")],
        [sg.Input("Ingredient 3"), sg.Input("Count")],
        [sg.Input("Ingredient 4"), sg.Input("Count")],
        [sg.Input("Ingredient 5"), sg.Input("Count")]
        
]

def delete_layout() -> None:
    return [
        [sg.Text("Enter recipe to delete.")],
        [sg.Button("Delete"), sg.Button("Cancel")],
        [sg.Input(focus=True)]
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

def output_message(target: str, message: str) -> None:
    window[target].update(message)

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

def calculate_result(target: str, count: int, tops: bool) -> None:
    output_window =  sg.Window("Result", output_layout(target, count), resizable=True, keep_on_top=tops)
    while True:
        output_event, output_values = output_window.read()
        if output_event == sg.WIN_CLOSED or output_event == "-CLOSE-":
            break
    output_window.close()

def save_recipe_file(rec_dict: dict) -> None:
    with open(recipe_file, "w", encoding = "utf-8") as outfile:
        json.dump(rec_dict, outfile, ensure_ascii=False, indent=4)

def add_recipe(target: str, inc_recipe: dict):
    recipes[target] = {}
    reduced_values = {k:v for k,v in inc_recipe.items() if ("Ingredient" not in v) if ("Count" not in v)} #remove default values
    for x in range(1, int(len(reduced_values)), 2):
        recipes[target][reduced_values[x].lower()] = float(reduced_values[x+1])
    save_recipe_file(recipes)

def main() -> None:
    keep_output_on_top = False
    while True:
        event, values = window.read()
        print("main window output: ",event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        match event:
            case "CALCULATE":
                target = values["ITEM_TARGET"].lower()
                if target == "" or values["ITEM_COUNT"] == "":
                    output_message("OUTPUT", "Please enter values in both target and count")
                    continue
                elif target not in recipes:
                    output_message("OUTPUT", f"{target} not found in recipe list")
                    continue
                count = int(values["ITEM_COUNT"])
                calculate_result(target, count, keep_output_on_top)
            case "-ADD RECIPE-":
                e, v = sg.Window("Input Window", recipe_layout(values["ITEM_TARGET"].lower())).read(close=True)
                if e == "Cancel" or e == sg.WIN_CLOSED:
                    output_message("OUTPUT", "Recipe addition canceled")
                target = v[0].lower()
                del v[0]
                add_recipe(target, v)
                output_message("OUTPUT", f"{target} added to recipes")
            case "-DELETE-":
                e, v = sg.Window("Delete Window", delete_layout()).read(close=True)
                if e == "Cancel" or e == sg.WIN_CLOSED:
                    continue
                target = v[0].lower()
                if target in recipes:
                    del recipes[v[0]]
                    save_recipe_file(recipes)
                    output_message("OUTPUT", f"deleted {v[0]}")
                else:
                    output_message("OUTPUT", f"{target} not found in recipes")
            case "-KEEPTOP-":
                if keep_output_on_top:
                    keep_output_on_top = False
                else:
                    keep_output_on_top = True
    
    window.close()



window = sg.Window("Resource Calculator", default_layout())

if __name__ == "__main__":
        main()