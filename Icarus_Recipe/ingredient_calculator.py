import PySimpleGUI as sg
import json

with open("Icarus_Recipe/recipes.json", "r") as infile:
    recipes = json.load(infile)

def default_layout() -> None: 
        return [
        [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET")],
        [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
        [sg.Button("Calculate", key="CALCULATE"), sg.Button("Add Recipe", key="-ADD RECIPE-"), sg.Button("Exit")],
        [sg.Column([[sg.Text("Line 1", key="OUTPUT")]])],
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

window = sg.Window("Resource Calculator", default_layout())

def main() -> None:
    i = 0
    while True:
        event, values = window.read()
        print("main window output: ",event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        match event:
            case "CALCULATE":
                target = values["ITEM_TARGET"].lower()
                count = values["ITEM_COUNT"]
                if target == "" or count == "":
                    window["OUTPUT"].update("Please enter values in both target and count")
                    continue
                elif target not in recipes:
                    window["OUTPUT"].update(f"{target} not found in recipe list")
                    continue
                output = get_base_ingredients(get_craft_tree(target, int(count)))
                print(get_craft_tree(target, int(count)))
                print_result(output)
            case "-ADD RECIPE-":
                e, v = sg.Window("Input Window", recipe_layout()).read(close=True)
                if e == "Cancel" or e == sg.WIN_CLOSED:
                    continue
                print("recipe window output: ", e, v)
                target = v[0].lower()
                del v[0]
                if target in recipes:
                    continue
                recipes[target] = {}
                reduced_values = {k:v for k,v in v.items() if ("Ingredient" not in v) if ("Count" not in v)} #remove default values
                for x in range(int(len(reduced_values)/2)):
                   recipes[target][v[x+1].lower()] = v[x+2]
                with open("Icarus_Recipe/recipes.json", "w", encoding = "utf-8") as outfile:
                    json.dump(recipes, outfile, ensure_ascii=False, indent=4)          
    
    window.close()

#for each key in recipe list, check if it's value is in the recipes. If so, then make the entry for that item. Otherwise, default format
def get_craft_tree(tgt: dict, total: int = 1) -> dict():
    recipe_tree = dict()
    recipe_tree[tgt] = dict()
    for k, v in recipes[tgt].items():
        if k in recipes:
            recipe_tree[tgt][k] = get_craft_tree(k, total*v)
        else:
            recipe_tree[tgt][k] = v*int(total)
    return recipe_tree

def get_base_ingredients(tgt: dict) -> dict:
    output = dict()
    for k, v in tgt.items():
        if isinstance(v, dict):
            temp_dict = get_base_ingredients(v)
            for i, j in temp_dict.items():
                if i in output:
                    output[i] += j
                else:
                    output[i] = j
        else:
            if k in output:
                output[k] += v
            else:
                output[k] = v
    return output


def add_result_layer(first: str, second: str) -> list:
    return [sg.Text(f"{first}: {second}")]

def print_result(input: dict) -> None:
    s = ""
    for k, v in input.items():
        s = s + f"{k}: {v}\n"
    window["OUTPUT"].update(s)

if __name__ == "__main__":
        main()