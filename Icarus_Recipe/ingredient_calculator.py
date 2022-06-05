import PySimpleGUI as sg
import json

with open("Icarus_Recipe/recipes.json", "r") as infile:
    recipes = json.load(infile)


layout = [
    [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET")],
    [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
    [sg.Button("Calculate", key="CALCULATE")],
    [sg.Text("Output", key="OUTPUT")],
    [sg.Button("Add Recipe", key="ADDRECIPE"), sg.Button("Save Recipe and close", key="SAVE")]
]

window = sg.Window("Resource Calculator", layout)

def main() -> None:
    i = 0
    while True:
        event, values = window.read()
        print(event, values)
        match event:
            case sg.WIN_CLOSED:
                break
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
                print_result(output)
            case "ADDRECIPE":
                window.extend_layout(window, [[sg.Text("Ingredient:"), sg.I(key = f'-IN-{i}'), sg.Text("Count:"), sg.I(key = f"-REQUIRED-{i}")]])
                i += 1
            case "SAVE":
                target = values["ITEM_TARGET"].lower()
                recipes[target] = {}
                for x in range(i):
                    recipes[target][values[f"-IN-{x}"]] = float(values[f"-REQUIRED-{x}"])
                with open("Icarus_Recipe/recipes.json", "w", encoding = "utf-8") as outfile:
                    json.dump(recipes, outfile, ensure_ascii=False, indent=4)
                break
                

    
    window.close()

#for each key in recipe list, check if it's value is in the recipes. If so, then make the entry for that item. Otherwise, default format
def get_craft_tree(tgt: dict, total: int = 1) -> dict():
    recipe_tree = dict()
    for k, v in recipes[tgt].items():
        if k in recipes:
            recipe_tree[k] = get_craft_tree(k, total*v)
        else:
            recipe_tree[k] = v*int(total)
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