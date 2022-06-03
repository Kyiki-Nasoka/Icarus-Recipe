import PySimpleGUI as sg
import json

with open("Icarus_Recipe/recipes.json", "r") as infile:
    recipes = json.load(infile)


layout = [
    [sg.Text("Target Item"), sg.Input(key="ITEM_TARGET")],
    [sg.Text("Count to make"), sg.Input(key="ITEM_COUNT")],
    [sg.Button("Calculate", key="CALCULATE"), sg.Button("Debug", key="DEBUG")],
    [sg.Text("Nothing to Display", key="OUTPUT")],
    [sg.Text("", key = "DEFAULTOUTPUT")]
]

window = sg.Window("Resource Calculator", layout)

def main() -> None:
    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break
            case "CALCULATE":
                target = values["ITEM_TARGET"].lower()
                count = int(values["ITEM_COUNT"])
                window["OUTPUT"].update(my_format_two(get_craft_tree(target, count)))
            case "DEBUG":
                target = "rifle round"
                count = 5
                print("-----recipes-----\n",recipes, "\n-----End Recipe-----\n")
                print("-----craft tree-----\n",get_craft_tree(target, count), "\n-----end craft tree\n")
                print("-----output-----\n",my_format_two(get_craft_tree(target, count)),"\n-----end output-----\n")

    
    window.close()

#for each key in recipe list, check if it's value is in the recipes. If so, then make the entry for that item. Otherwise, default format
def get_craft_tree(tgt, total) -> dict():
    recipe_tree = dict()
    for k, v in recipes[tgt].items():
        if k in recipes:
            recipe_tree[k] = get_craft_tree(k, int(total)*v)
        else:
            recipe_tree[k] = v*int(total)
    return recipe_tree

def my_format_two(tgt: dict) -> dict:
    output = dict()
    for k, v in tgt.items():
        if isinstance(v, dict):
            temp_dict = my_format_two(v)
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


if __name__ == "__main__":
        main()