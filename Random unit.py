#!/usr/bin/env python
# coding: utf-8

import random
import pandas as pd
import json
import tkinter as tk
from tkinter import ttk
from typing import Tuple
import numpy as np

# Load configuration from the Config File
with open('Config.json', 'r') as f:
    config = json.load(f)

# Retrieve configuration values
hobbit_fill = config['hobbit_fill_team']
hobbit_team_chance = config['full_hobbit_team_chance']
budget = config["budget"]
max_unit_width = config["max_unit"]
teams_created = config["teams_created"]
team_difficulty = config["difficulty"]
app_width = config["width"]
app_height = config["height"]
app_mode = config["application_mode"]

# Read unit data from a CSV file
unit_df = pd.read_csv('Units.csv')

# Flag for when the application is closing
closing = False

# Define color schemes for dark mode and light mode
dark_mode_colours = {
    'background': '#2d2d2d',
    'foreground': '#ffffff'
}
light_mode_colours = {
    'background': '#f0f0f0',
    'foreground': '#000000'
}


class CustomTk(tk.Tk):
    """
    CustomTk is a subclass of tk.Tk that adds support for managing GUI elements and changing the color scheme.

    Attributes: Most are same as Tkinter
        colour (dict): Dictionary of colour palette to be used for the window

    """
    def __init__(
            self, 
            screenName: str = None, 
            baseName: str = None, 
            className: str = "Tk", 
            useTk: bool = True, 
            sync: bool = False, 
            use: str = None,
            colour: dict = None
        ) -> None:
        super().__init__(screenName=screenName, baseName=baseName, className=className, useTk=useTk, sync=sync, use=use)
        self.settings_entries = {}
        self.button_entries = {}
        self.label_entries = {}
        self.checkbutton_entries = {}
        self.checkbutton_vars = {}
        if colour is None:
            self.colour_mode = {
                'background': '#f0f0f0',
                'foreground': '#000000'
            }
        else:
            self.colour_mode = colour

    def set_app_mode(self, colour: dict) -> None:
        """
        Sets the colour of the app to the provided dict.
        
        Args:
            colour (dict): Dictionary of colour palette to be used for the window
        """
        self.colour_mode = colour
        self.config(bg=colour['background'])
        for label in self.label_entries.values():
            label.config(bg=colour['background'], fg=colour['foreground'])
        for button in self.button_entries.values():
            button.config(bg=colour['background'], fg=colour['foreground'])
        for setting in self.settings_entries.values():
            if isinstance(setting, tk.Entry):
                setting.config(bg=colour['background'], fg=colour['foreground'])
        for checkbutton in self.checkbutton_entries.values():
            checkbutton.config(bg=colour['background'], 
                               fg=colour['foreground'],
                               activebackground=colour['background'], 
                               activeforeground=colour['foreground'], 
                               selectcolor=colour['background'])


class RandomTabsTeam:
    """
    RandomTabsTeam randomly generates a team of units for the game Totally Accurate Battle Simulator (TABS).

    Attributes:
        budget (int): Integer for the amount of money the generator has to spend
        selection_df (pd.Dataframe): Dataframe of units to select from
        hobbit_fill (bool): Boolean value for if the remaining money gets spent on hobbits
        hobbit_team_chance (int): a 1 out of integer chance of the team just being hobbits
        max_unit_width (int): the max size of distinct units in the team 
    """
    def __init__(
            self, 
            budget: int, 
            selection_df: pd.DataFrame, 
            hobbit_fill: bool, 
            hobbit_team_chance: int,
            max_unit_width: int,
        ) -> None:
        self.budget = budget
        self.cost = 0
        self.team = {}
        self.unit_df = selection_df
        self.hobbit_fill = hobbit_fill
        self.hob_chance = hobbit_team_chance
        self.max_unit_width = max_unit_width

        self.generate_team()

    def __str__(self) -> str:
        formatted_team = [f"{key} x {value}" for key, value in self.team.items()]

        # Returns a string for the number of each unit, and a total cost at the end.
        return "\n".join(formatted_team) + f"\nTotal Cost: {self.cost}"
    
    def generate_team(self) -> None:
        """
        Checks if the team is all hobbits, otherwise loops through the max_unit_width and adds random units, subtracting the cost from the budget.
        """
        if random.randint(1, self.hob_chance) == 1:
            self.hobbit_fill_remaining()
            return
            
        for _ in range(self.max_unit_width):
            if self.budget < self.unit_df['Cost'].min():
                break
            self.filter_df_cost()
            name, faction, unit_cost = self.random_unit()
            total_units = random.randint(1, np.floor(self.budget/unit_cost))
            key = self.get_unit_key(name, faction)
            self.team[key] = self.team.get(key, 0) + total_units
            self.budget -= total_units * unit_cost
            self.cost += total_units * unit_cost

        self.hobbit_fill_remaining()

    def get_unit_key(self, name: str, faction: str) -> str:
        """
        Formats a string containing the units name, then the faction they belong to in brackets.
        
        Args:
            name (str): Name of the unit
            faction (str): Faction name the unit belongs to
        
        Returns:
            str: combination of name and faction
        """
        return f"{name} ({faction})"

    def random_unit(self) -> Tuple[str, str, int]:
        """
        Provides a random unit from the Dataframe.
        
        Returns:
            str: The unit's name
            str: The unit's faction
            int: The cost of the unit
        """
        random_row = self.unit_df.sample(n=1)
        unit_name = random_row.iloc[0]['Name']
        unit_faction = random_row.iloc[0]['Faction']
        unit_cost = random_row.iloc[0]['Cost']

        return unit_name, unit_faction, unit_cost

    def filter_df_cost(self) -> None:
        """
        Filters the unit Dataframe to only contain units that have a cost less than the current budget.
        """
        self.unit_df = self.unit_df[self.unit_df["Cost"] <= self.budget]

    def hobbit_fill_remaining(self) -> None:
        if self.budget > 50:
            value = int(np.floor(self.budget/50))
            key = self.get_unit_key("Hobbit", "Farmer")
            self.team[key] = self.team.get(key, 0) + value
            self.cost += value * 50


def is_number_input(s) -> bool:
    """
    Check whether the input string is a digit or empty.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is a digit or empty, False otherwise.
    """
    return s.isdigit() or s == ''


def update_config() -> None:
    """
    Updates the currently selected options, and saves them back to the Config.json file
    """
    global hobbit_fill, hobbit_team_chance, budget, max_unit_width, teams_created, team_difficulty, root
    hobbit_fill = bool(root.checkbutton_vars['Hobbit Fill'].get())
    hobbit_team_chance = int(root.settings_entries['Full Hobbit Team Chance'].get())
    budget = int(root.settings_entries['Team Budget'].get())
    max_unit_width = int(root.settings_entries['Max Distinct Units'].get())
    teams_created = int(root.settings_entries['Random Teams Generated'].get())
    team_difficulty = int(root.settings_entries['Difficulty'].get())
    config['hobbit_fill_team'] = hobbit_fill
    config['full_hobbit_team_chance'] = hobbit_team_chance
    config["budget"] = budget
    config["max_unit"] = max_unit_width
    config["teams_created"] = teams_created
    config["difficulty"] = team_difficulty
    config["width"] = app_width
    config["height"] = app_height
    config["application_mode"] = app_mode
    with open('Config.json', 'w') as f:
        json.dump(config, f, indent=4)


def filter_df_difficulty(df: pd.DataFrame, difficulty: int) -> pd.DataFrame:
    """
    Creates a subsection of the provided Dataframe, filtered by the difficulty level.
    Note that the max difficulty is 4.
    
    Args:
        df (pd.Dataframe): the unit Dataframe to be filtered
        difficulty (int): the difficulty to be filtered to

    Returns:
        pd.Dataframe: the filtered Dataframe
    """
    
    if difficulty > 4:
        raise ValueError(f"Unable to set difficulty to higher than 4. Provided value is {difficulty}")
    
    filtered_df = df[df["Ranking"] >= difficulty]
    return filtered_df


def on_resize(event) -> None:
    """
    When resizing the window, automatically update the width and height variables.
    This is ignored if the application is closing.
    """
    global app_width, app_height, closing
    if not closing:
        app_width = event.width
        app_height = event.height


def on_close() -> None:
    """
    When closing the window, set the closing flag to true, update the Config.json file and close the application.
    """
    global closing
    closing = True
    update_config()
    root.destroy()


def add_settings_int_box(name: str, row: int, column: int, root: CustomTk, value: int) -> None:
    """
    Creates a label and entry pair, with the entry box being limited to only Integers or empty.
    
    Args:
        name (str): Label next to the entry box
        row (int): Row that the UI objects will appear
        column (int): Column that the UI objects will start at
        root (CustomTK): Which application the UI is being added to
        value (int): Current value the entry box is set to
    """
    validate_command = root.register(lambda s: is_number_input(s))
    label = tk.Label(root, text=name)
    label.grid(row=row, column=column)
    root.label_entries[name] = label
    entry = tk.Entry(root, validate='key', validatecommand=(validate_command, '%S'))
    entry.insert(0, value)
    entry.grid(row=row, column=column+1)
    root.settings_entries[name] = entry


def new_main_application_window(width: int, height: int, mode: str) -> CustomTk:
    """
    Creates the application that is used as the main window.
    
    Args:
        width (int): The width of the application in pixels
        height (int): The height of the application in pixels
        mode (str): The colour palette used for the application
        
    Returns:
        CustomTk: Application object
    """
    colour = get_mode_colours(mode)
    root = CustomTk(colour=colour)
    root.title("Random TABS Team Generator")
    geo_size = f"{width}x{height}"
    root.geometry(geo_size)

    root.bind('<Configure>', on_resize)
    root.protocol("WM_DELETE_WINDOW", on_close)

    i = 0

    settings_label = tk.Label(root, text="Settings")
    settings_label.grid(row=i, column=1)
    root.label_entries['Settings'] = settings_label
    i += 1

    label = tk.Label(root, text='Hobbit Fill')
    label.grid(row=i, column=0)
    root.label_entries['Hobbit Fill'] = label
    hob_fill_check_var = tk.BooleanVar()
    hob_fill_check_var.set(hobbit_fill)
    root.checkbutton_vars['Hobbit Fill'] = hob_fill_check_var
    hob_fill_check_button = tk.Checkbutton(root, text='', variable=hob_fill_check_var)
    hob_fill_check_button.grid(row=i, column=1)
    root.checkbutton_entries['Hobbit Fill'] = hob_fill_check_button
    i += 1

    add_settings_int_box('Full Hobbit Team Chance', i, 0, root, hobbit_team_chance, )
    i += 1
    add_settings_int_box('Team Budget', i, 0, root, budget)
    i += 1
    add_settings_int_box('Max Distinct Units', i, 0, root, max_unit_width)
    i += 1
    add_settings_int_box('Random Teams Generated', i, 0, root, teams_created)
    i += 1
    add_settings_int_box('Difficulty', i, 0, root, team_difficulty)
    i += 1

    button_light = tk.Button(root, text="Light Mode", command=lambda: switch_mode("light"))
    button_light.grid(row=i, column=0)
    root.button_entries["Light Mode"] = (button_light)
    button_dark = tk.Button(root, text="Dark Mode", command=lambda: switch_mode("dark"))
    button_dark.grid(row=i, column=1)
    root.button_entries["Dark Mode"] = (button_dark)
    i += 1

    button_submit = tk.Button(root, text='Generate', command=generate_button_pressed)
    button_submit.grid(row=i, column=1)
    root.button_entries['Generate'] = button_submit
    i += 1

    root.set_app_mode(colour)

    return root


def generate_button_pressed() -> None:
    """
    This function is invoked when the 'Generate' button is pressed.
    """
    update_config()
    teams = generate_tabs_teams()
    colour = root.colour_mode
    show_teams_in_notebook(teams, colour)



def generate_tabs_teams() -> dict:
    """
    This function generats the teams for the game.
    
    Returns:
        dict: Dictionary containing all the generated teams
    """
    teams = []
    filtered_unit_df = filter_df_difficulty(unit_df, team_difficulty)

    for _ in range(teams_created):
        team = RandomTabsTeam(budget, filtered_unit_df, hobbit_fill, hobbit_team_chance, max_unit_width)
        teams.append(team)

    return teams


def show_teams_in_notebook(teams: dict, colour_mode: dict) -> None:
    """
    This function shows the generated teams in a new notebook window
    
    Args:
        teams (dict): Dictionary containing generated teams to display in tabbed windows
        colour (dict): Dictionary of colour palette to be used for the window
    """
    notebook_window = tk.Toplevel(root)
    notebook_window.title("Generated Teams")

    style = ttk.Style()
    style_name = 'CustomNotebook'
    
    if style_name not in style.theme_names():
        style.theme_create(style_name, parent="alt")

    style.theme_settings(style_name, settings={
        ".": {
            "configure": {
                "background": colour_mode["background"],
                "foreground": colour_mode["foreground"]
            }
        },
        "TNotebook": {
            "configure": {
                "tabmargins": [2, 5, 2, 0]
            }
        },
        "TNotebook.Tab": {
            "configure": {
                "padding": [5, 1],
                "background": colour_mode["background"],
                "foreground": colour_mode["foreground"]
            },
            "map": {
                "background": [("selected", colour_mode["foreground"])],
                "foreground": [("selected", colour_mode["background"])],
                "expand": [("selected", [1, 1, 1, 0])]
            }
        }
    })
    style.theme_use(style_name)

    notebook = ttk.Notebook(notebook_window)

    for i, team in enumerate(teams):
        team_tab = tk.Frame(notebook)
        team_text = tk.Text(team_tab, wrap="word", bg=colour_mode['background'], fg=colour_mode['foreground'])
        team_text.insert("1.0", str(team))
        team_text.pack(expand=True, fill="both")
        notebook.add(team_tab, text=f"Team {i+1}")

    notebook.pack(expand=True, fill="both")


def get_mode_colours(mode: str) -> dict:
    """
    Converts string description to a dictionary colour palette.

    Args:
        mode (str): Name of the colour palette to be used

    Returns:
        dict: Dictionary of the colour palette
    """
    colours = light_mode_colours
    if mode == "dark":
        colours = dark_mode_colours
    elif mode == "light":
        colours = light_mode_colours
    else:
        raise ValueError("Invalid mode")
    
    return colours


def switch_mode(mode: str) -> None:
    """
    Changes the current colour palette

    Args:
        mode (str): Name of the colour palette to be used
    """
    global app_mode
    app_mode = mode
    colour = get_mode_colours(mode)
    root.set_app_mode(colour)

def main():
    """
    Main function of the application
    """
    global root
    root = new_main_application_window(width=app_width, height=app_height, mode=app_mode)
    root.mainloop()

if __name__ == "__main__":
    main()