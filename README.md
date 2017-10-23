# sftoolbox
sharing tools and snippets for VFX and animation

Dependencies are :
* PyYaml

Launch tutorial :

    launch.py examples/hellolanguages
    
For development you can launch the tool with live edit of the.

    launch.py examples/hellolanguages --live

## Project

Project is the main directory that you will hook SF Toolbox with.

* name: name of the tool or project
* description: describes what the tool does
* about: will be shown in the help about menu
* panels: list of panels that the project contains
* actions: list of actions that the project contains
* content: list of content that the project contains
* icon: icon for the project relative to project directory
 
## Actions

Action will trigger functionality that you hookup, you can run python code, call functions, eval MEL and MaxScript, ...

 All actions have following attributes
 
 * idname: unique id that identifies this action
 * label: label that you want to show in the ui
 * description: what does the action do (will be shown in tooltips and statustips)
 * type: type of the action this can be python_code, python_function, ...
 * icon: icon for the action relative to project directory 
 
 Following types for actions are available
 
### Python Code (type: python_code)
 
 * code: python code string to run
 
### Python Function (type: python_function)
 * filepath: relative filepath from the project
 * function: name of the function
 * args: list of arguments to pass to the function
 * kwargs: key word arguments for the function

### Mel Eval (type: mel_eval) (Maya Only)

evaluate given mel code
 * code: mel code to run

## Panels

Panel will be presented as widget, panels can contain panels and can be viewed in the main window


* idname: unique id that identifies this action
* label: label that you want to show in the ui
* description: what does the action do (will be shown in tooltips and statustips)
* style: describes in which way the actions are represented, can be horizontal, vertical, grid, dropdown, ...
* actions: list of actions that the panel contains
* panels: list of panels that the panel contains
* content: list of content that the panel contains 
* icon: icon for the panel relative to project directory