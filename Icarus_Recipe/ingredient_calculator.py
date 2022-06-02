import PySimpleGUI as sg
import json

with open("recipes.json", "r") as infile:
    recipes = json.load(infile)


layout = [
    [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET")],
    [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
    [sg.Button("Calculate", key="CALCULATE")],
    [sg.Text("Nothing to Display", key="OUTPUT")],
    [sg.Button("debug", key = "DEBUG")]
]

window = sg.Window("Resource Calculator", layout)

def main() -> None:
    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break
            case "CALCULATE":
                target = values["ITEM_TARGET"]
                count = values["ITEM_COUNT"]
                window["OUTPUT"].update(my_format(get_base_item_total(target, count)))
            case "DEBUG":
                print(recipes)

    
    window.close()

#for each key in recipe list, check if it's value is in the recipes. If so, then make the entry for that item. Otherwise, default format
def get_base_item_total(tgt, total) -> dict():
    recipe_total = dict()
    for k, v in recipes[tgt].items():
        if k in recipes:
            recipe_total[k] = get_base_item_total(k, int(total)*v)
        else:
            recipe_total[k] = v*int(total)
    return recipe_total

#formatting top level on left, each indented recipe preceeded by an additional "-"
def my_format(tgt_dict, depth = 0) -> str:
    output = ""
    for k, v in tgt_dict.items():
        if isinstance(v, dict):
            intermediate = depth*"-"
            interm2 = f"{intermediate}{k}\n" + my_format(v, depth + 1)
            output = output + interm2
        else:
            intermediate = depth*"-"
            return f"{intermediate}{k}: {v}\n"
    return output




if __name__ == "__main__":
        main()