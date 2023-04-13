![githubtitle](https://user-images.githubusercontent.com/61150608/192163830-16aaaec7-537a-4ef9-87a5-332769345ede.png)
A tool to quickly prototype jumps. This is build using [PyVMF](https://github.com/GorangeNinja/PyVMF) by GorangeNinja.

## Usage
This consists of a couple of different ideas
1. With **gui.py** we can create directed colored squares, and when pressing spacebar we generate the corresponding .vmf using **gui_build.py**
2. With **main.py** we can give a string, defining our jump, where we use **generate.py** to create the corresponding .vmf
3. These both make use of **classes.py** and especially of the class **AbstractBrush**

## Licenses
The GUI part of this project, i.e. the gui directory uses the GPLv3 License as they use PyQt6
The actual python code, i.e. main.py etc use the MIT License as they use PyVMF
