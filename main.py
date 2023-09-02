import os
from pathlib import Path
import re
import enchant
import json
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

IMAGE_PATH = Path(__file__).parent / "images/"

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding=10)
        # window icon
        self.ico=[
        ttk.PhotoImage(name='window', file=IMAGE_PATH / "xml.png"),]
        # Setting icon of master window
        master.iconphoto(False, 'window')
        # get device screen size
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        # set min height and width to that of the screen
        self.master.minsize(self.screen_width, self.screen_height)

        self.master = master
        self.pack()
        # set config file
        self.config_file = 'config.json'

        # create notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=BOTH, expand=True)
        self.text_widgets = []
        # Define the themes
        self.themes = {
            "light_themes": ["cerculean", "morph", "pulse", "minty", "litera"],
            "dark": ["solar", "superhero", "darkly", "cyborg", "vapor"]
        }
        # Get a list of available fonts
        self.font_families = ['Courier New', 'Lucida Console', 'Consolas', 'Menlo', 'DejaVu Sans Mono', 'Source Code Pro', 'Inconsolata', 'Monaco', 'Ubuntu Mono', 'Fira Code']

        self.theme_choice=ttk.StringVar()
        self.style=ttk.Style()
        self.font_size = ttk.StringVar(value='10')

        # set theme to either default or user set theme
        try:
            self.style.theme_use(self.get_key_from_json('default_theme'))
        except:
            pass

        self.create_widgets()
        self.add_new_tab()
        # bind key shortcuts
        # shortcut for new tab
        self.master.bind('<Control-n>', self.add_new_tab)
        self.master.bind('<Control-N>', self.add_new_tab)
        # shortcut for open file
        self.master.bind('<Control-o>', self.open_file_dialog)
        self.master.bind('<Control-O>', self.open_file_dialog)
        # shortcut for save file
        self.master.bind('<Control-s>', self.save_tab)
        self.master.bind('<Control-S>', self.save_tab)
        # shortcut for save as file 
        self.master.bind('<Control-Shift-s>', self.save_as_tab)
        self.master.bind('<Control-Shift-S>', self.save_as_tab)
        # shortcut for close tab
        self.master.bind('<Control-w>', self.close_tab)
        self.master.bind('<Control-W>', self.close_tab)
        # shortcut for undo
        self.master.bind('<Control-z>', self.undo_text)
        self.master.bind('<Control-Z>', self.undo_text)
        # shortcut for redo
        self.master.bind('<Control-Shift-z>', self.redo_text)
        self.master.bind('<Control-Shift-Z>', self.redo_text)
        # shortcut for cut
        self.master.bind('<Control-x>', self.cut_text)
        self.master.bind('<Control-X>', self.cut_text)
        # shortcut for copy
        self.master.bind('<Control-c>', self.copy_text)
        self.master.bind('<Control-C>', self.copy_text)
        # shortcut for paste
        # shortcut for delete
        self.master.bind('<Delete>', self.delete_text)
        # shortcut for find
        self.master.bind('<Control-f>', self.find_text)
        self.master.bind('<Control-F>', self.find_text)
        #  shortcut for select all
        self.master.bind('<Control-a>', self.select_all_text)
        self.master.bind('<Control-A>', self.select_all_text)

        # shortcut for help

    def create_widgets(self):
        """
        # add a menu with the following items
        # File, Edit, View,Preference,Help
        # File: New, Open, Save, Save As, Exit
        # Edit: Undo, Redo, Cut, Copy, Paste, Delete, Select All
        # View: Zoom In, Zoom Out, Zoom Reset, Fullscreen
        # Preference: Theme, Font, Font Size, Font Color, Background Color
        # Help: About, Help, Report Issue, Check for Updates
        """
        # create menu bar
        self.menubar = ttk.Menu(self.master)
        self.master.config(menu=self.menubar)

        # create file menu
        self.filemenu = ttk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.add_new_tab)
        self.filemenu.add_command(label="Open", command=self.open_file_dialog)
        self.filemenu.add_command(label="Save", command=self.save_tab)
        self.filemenu.add_command(label="Save As", command=self.save_as_tab)
        self.filemenu.add_separator()
        # add close tab
        self.filemenu.add_command(label="Close Tab", command=self.close_tab)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.master.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # create edit menu
        self.editmenu = ttk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Undo", command=self.undo_text)
        self.editmenu.add_command(label="Redo", command=self.redo_text)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.cut_text)
        self.editmenu.add_command(label="Copy", command=self.copy_text)
        self.editmenu.add_command(label="Paste", command=self.paste_text)
        self.editmenu.add_command(label="Delete", command=self.delete_text)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Find/ Replace", command=self.find_text)
        self.editmenu.add_separator()
        # add format text option
        self.editmenu.add_command(label="Format Text", command=self.format_text)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Select All", command=self.select_all_text)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        # create preference menu
        self.prefmenu = ttk.Menu(self.menubar, tearoff=0)
        
        # Create the theme menu
        self.theme_menu = ttk.Menu(self.prefmenu, tearoff=0)
        self.prefmenu.add_cascade(label="Themes", menu=self.theme_menu)

        # Create the light theme submenu
        self.light_theme_menu = ttk.Menu(self.theme_menu, tearoff=0)
        self.theme_menu.add_cascade(label="Light Themes", menu=self.light_theme_menu)
        for theme in self.themes["light_themes"]:
            self.light_theme_menu.add_radiobutton(
                label=theme.capitalize(), 
                variable=self.theme_choice,
                value=theme, 
                command=self.set_theme
            )

        # Create the dark theme submenu
        self.dark_theme_menu = ttk.Menu(self.theme_menu, tearoff=0)
        self.theme_menu.add_cascade(label="Dark Themes", menu=self.dark_theme_menu)
        for theme in self.themes["dark"]:
            self.dark_theme_menu.add_radiobutton(
                label=theme.capitalize(), 
                variable=self.theme_choice,
                value=theme,
                command=self.set_theme
            )
        
        # Create a Font menu
        self.font_menu = ttk.Menu(self.prefmenu, tearoff=1,type="menubar")

        # Add each font to the Font menu
        for font_family in self.font_families:
            self.font_menu.add_command(label=font_family, command=lambda font_family=font_family: self.change_font(font_family))

        # Create font size sub-menu
        font_size_menu = ttk.Menu(self.prefmenu, tearoff=0)
        for size in range(8, 22, 2):
            font_size_menu.add_radiobutton(
                label=str(size),
                value=str(size),
                variable=self.font_size,
                command=self.change_font_size
            )

        # Add the Font menu to the menu bar
        self.prefmenu.add_cascade(label="Font", menu=self.font_menu)
        self.prefmenu.add_cascade(label='Font Size', menu=font_size_menu)
        self.menubar.add_cascade(label="Preferences", menu=self.prefmenu)
        
        # create help menu
        self.helpmenu = ttk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About")
        self.helpmenu.add_command(label="Help", command= self.get_help )
        # self.helpmenu.add_command(label="Report Issue", command=self.donothing)
        # self.helpmenu.add_command(label="Check for Updates", command=self.donothing)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

    def set_theme(self, event=None):
        # get the theme choice from the theme choice variable
        theme = self.theme_choice.get()
        # set the theme
        self.style.theme_use(theme)
        # save the theme choice to the config.json file
        self.save_key_to_json("default_theme", theme)
    
    def change_font(self, font_family):
        # change the font of the text
        self.tab.configure(font=(font_family,self.font_size.get()))
        # save the font family to the config.json file
        self.save_key_to_json("current_font_family", font_family)
    
    def change_font_size(self, event=None):
        current_font=self.get_key_from_json("current_font_family")
        # set only the font size withou changing the font family
        self.tab.configure(font=(current_font, self.font_size.get()))
        # save the font size to the config.json file
        self.save_key_to_json("current_font_size", self.font_size.get())

    def get_key_from_json(self, key):
        # get the value of the key from the config.json file
        with open(self.config_file,'r') as config_file:
            data = json.load(config_file)
            return data[key]

    def save_key_to_json(self, key, value):
        # save the key value pair to the config.json file
        with open(self.config_file,'r') as config_file:
            data = json.load(config_file)
            data[key] = value
        with open(self.config_file,'w') as config_file:
            json.dump(data, config_file)

    def add_new_tab(self, event=None):
        # get a new text widget
        self.tab = HighlightingText(self.notebook)
        # add the text widget to the list of text widgets
        self.text_widgets.append(self.tab)
        self.tab.pack(fill=BOTH, expand=True)
        # add a new tab to the notebook and also add x button to close the tab to the tab
        self.notebook.add(self.tab, text='Untitled')
        # select the new tab
        self.notebook.select(len(self.text_widgets) - 1)
        # set the focus on the new tab
        self.tab.focus()

    def open_file_dialog(self, event=None):
        # prompt user to select a file
        file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")] ) 
        # if user selected a file, open it
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path):
        # open the file and get the content
        with open(file_path, 'r') as f:
            contents = f.read()
        
        # add a new tab
        self.add_new_tab()
        # get the current tab
        current_tab = self.get_active_tab()
        self.notebook.tab(current_tab, text=os.path.basename(file_path))
        # delete the current content of the text widget and add the new content
        text_widget = self.text_widgets[current_tab]
        text_widget.delete(1.0, END)
        text_widget.insert(END, contents)

        # trigger syntax highlighting
        self.tab.syntax_highlight()

        # add error highlighting
        self.tab.highlight_errors()

    def get_active_tab(self):
        # returns the index of the active tab
        return self.notebook.index(self.notebook.select())

    def close_tab(self, event=None):
        # get current tab
        current_tab = self.get_active_tab()
        # check if the tab is edited and not saved
        if self.notebook.tab(current_tab, "text").endswith("*"):
            # get the name of the tab
            tabname = self.notebook.tab(current_tab, "text")
            # check if tabname ends with * and remove it if it does
            if tabname.endswith("*"):
                tabname = tabname[:-1]
            # ask user if he wants to save the file
            answer = messagebox.askyesnocancel("Save?", "Do you want to save " + tabname + "?")
            if  answer:
                # if user clicked yes, save the file
                self.save_tab()
            
            if answer != None:
                # remove the tab from the notebook
                self.notebook.forget(current_tab)
                # remove the text widget from the list of text widgets
                self.text_widgets.pop(current_tab)

                # close application if no tab is left
                if len(self.text_widgets) == 0:
                    self.master.destroy()

    def save_tab(self, event=None):
        
        # get the content of the text widget
        text_widget = self.text_widgets[self.get_active_tab()]
        contents = text_widget.get(1.0, END)
        # get the name of the tab
        tab_name = self.notebook.tab(self.get_active_tab(), "text")
        # remove the * from the tab name if it is there
        if tab_name.endswith("*"):
            tab_name = tab_name[:-1]
        # if the name of the tab is Untitled, save the file as a new file
        if tab_name == 'Untitled':
            self.save_as_tab()
        else:
            # save the content of the text widget in the file
            with open(tab_name, 'w') as f:
                f.write(contents)

    def save_as_tab(self, event=None):
        # get the content of the text widget
        text_widget = self.text_widgets[self.get_active_tab()]
        contents = text_widget.get(1.0, END)
        # get the tab name
        tab_name = self.notebook.tab(self.get_active_tab(), "text")
        if tab_name == 'Untitled':
            initial_file_name = 'Untitled'
        else:
            initial_file_name = tab_name
        
        # remove the * from the tab name if it is there
        if tab_name.endswith("*"):
            initial_file_name = tab_name[:-1]
        # prompt the user to select a file
        file_path = filedialog.asksaveasfilename(
            filetypes=[("XML Files", "*.xml")], 
            defaultextension=".xml",
            initialfile=initial_file_name,
            )
        # if the user selected a file, save the content of the text widget to the selected file
        if file_path:
            with open(file_path, 'w') as f:
                f.write(contents)
            # update the name of the tab with the name of the file
            self.notebook.tab(self.get_active_tab(), text=os.path.basename(file_path))


        else:
            # if there is only one tab, clear the content of the text widget
            self.text_widgets[0].delete(1.0, END)
            # update the name of the tab
            self.notebook.tab(0, text='Untitled')

    def undo_text(self, event=None):
        # undo the last action
        curent_tab = self.get_active_tab()
        self.text_widgets[curent_tab].event_generate("<<Undo>>")

    def redo_text(self, event=None):
        # redo the last action
        self.text_widgets[self.get_active_tab()].event_generate("<<Redo>>")
    
    def cut_text(self, event=None):
        # copy the selected text and delete it
        self.copy_text()
        self.delete_text()
    
    def copy_text(self, event=None):
        # copy the selected text
        selection = self.text_widgets[self.get_active_tab()].selection_get()
        #print(selection)
        self.clipboard_clear()
        self.clipboard_append(selection)

    def paste_text(self, event=None):
        # paste the text from the clipboard
        self.text_widgets[self.get_active_tab()].insert(INSERT, self.clipboard_get())
        # add error highlighting
        self.tab.highlight_errors()
        # trigger syntax highlighting
        self.tab.syntax_highlight()
    
    def delete_text(self, event=None):
        # delete the selected text
        try:
            self.text_widgets[self.get_active_tab()].delete(SEL_FIRST, SEL_LAST)
        except:
            pass
    
    def select_all_text(self, event=None):
        # select all the text
        self.text_widgets[self.get_active_tab()].tag_add(SEL, 1.0, END)
    
    def find_text(self, event=None):
        # open the find window
        FindWindow(self)

    def change_theme(self, event=None):
        # change the theme of the text widget
        selected_theme = self.theme.get()
        # set the theme of the application
        self.style.theme_use(selected_theme)

    def format_text(self, event=None):
        # get the text from the current tab
        text = self.text_widgets[self.get_active_tab()].get(1.0, END)
        # format the text
        # x_text=ET.fromstring(text)
        # formatted_text = self.tab.format_xml(x_text)
        # insert the formatted text in the text widget
        self.text_widgets[self.get_active_tab()].delete(1.0, END)
        self.text_widgets[self.get_active_tab()].insert(1.0, text)

        # add error highlighting
        self.tab.highlight_errors()
        # trigger syntax highlighting
        self.tab.syntax_highlight()

    def get_help(self, event=None):
        # get content from the help file and show it in a messagebox
        with open("help.md", "r") as f:
            help_text = f.read()
        messagebox.showinfo("Help", help_text)

class FindWindow(ttk.Toplevel):
    """
    this class creates a window that allows the user to find a string in the text widget
    and also replace one or more occurences of a string with another string
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Find")
        self.transient(master)
        self.resizable(False, False)
        self.master = master
        # set the position of the toplevel window to at the right of the text widget in the master app
        self.geometry(f"+{master.winfo_rootx()+master.winfo_width()}+{master.winfo_rooty()}")
        self.create_widgets()
    
    def create_widgets(self):
        # create a label for the find entry
        self.find_label = ttk.Label(self, text="Find:")
        self.find_label.grid(row=0, column=0, padx=5, pady=5)
        # create an entry for the find label
        self.find_entry = ttk.Entry(self, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)
        # create a button to find the string
        self.find_button = ttk.Button(self, text="Find", command=self.find)
        self.find_button.grid(row=0, column=2, padx=5, pady=5)
        # create a label for the replace entry
        self.replace_label = ttk.Label(self, text="Replace:")
        self.replace_label.grid(row=1, column=0, padx=5, pady=5)
        # create an entry for the replace label
        self.replace_entry = ttk.Entry(self, width=30)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)
        # create a button to replace the string
        self.replace_button = ttk.Button(self, text="Replace", command=self.replace)
        self.replace_button.grid(row=1, column=2, padx=5, pady=5)
        # create a button to replace all the strings
        self.replace_all_button = ttk.Button(self, text="Replace all", command=self.replace_all)
        self.replace_all_button.grid(row=2, column=2, padx=5, pady=5)

        # create a label to display the number of matches
        self.matches_var = ttk.StringVar()
        self.matches_label = ttk.Label(self, textvariable=self.matches_var)
        self.matches_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        # bind the key release event to the find method
        self.find_entry.bind("<KeyRelease>", self.find)

    def find(self,event=None):
        # get the string to find
        find_string = self.find_entry.get()
        # get the content of the text widget
        text_widget = self.master.text_widgets[self.master.get_active_tab()]
        text_widget.tag_remove("match", 1.0, END)
        # check if the string to find is not empty
        if find_string:
            idx='1.0'
            while 1:
                # get the index of the first match
                idx = text_widget.search(find_string, idx, END, nocase=True)
                # check if there is a match
                if idx:
                    # get the last index of the match
                    last_idx = f"{idx}+{len(find_string)}c"
                    # add a tag to the match
                    text_widget.tag_add("match", idx, last_idx)
                    # make sure the match is visible
                    text_widget.tag_configure("match",foreground ="yellow")
                    
                    # set the focus on the match
                    #text_widget.tag_raise("match", idx)
                    # set the index to the end of the match
                    idx = last_idx
                else:
                    break
            # get the number of matches
            matches = len(text_widget.tag_ranges('match'))//2
            # display the number of matches
            if matches:
                # update the number of matches
                    self.matches_var.set(f"{matches} matches")
            else:
                # no matches were found
                self.matches_var.set("No matches")
    
    def replace(self):
        # get the string to find
        find_string = self.find_entry.get()
        # get the string to replace
        replace_string = self.replace_entry.get()
        # get the content of the text widget
        text_widget = self.master.text_widgets[self.master.get_active_tab()]
        #text_widget.tag_remove("match", 1.0, END)
        # check if the string to find is not empty
        if find_string:
            # get the index of the first match
            idx = text_widget.search(find_string, 1.0, END, nocase=True)
            # check if there is a match
            if idx:
                # get the last index of the match
                last_idx = f"{idx}+{len(find_string)}c"
                # add a tag to the match
                text_widget.tag_add("match", idx, last_idx)
                # make sure the match is visible
                text_widget.tag_configure("match", foreground="yellow")
                # update the number of matches
                self.matches_var.set(f"{len(text_widget.tag_ranges('match'))//2} matches")
                # replace the string
                text_widget.delete(idx, last_idx)
                text_widget.insert(idx, replace_string)
            else:
                # if there is no match, display a message
                self.matches_var.set("No matches")
        
    def replace_all(self):
        # get the string to find
        find_string = self.find_entry.get()
        # get the string to replace
        replace_string = self.replace_entry.get()
        # get the content of the text widget
        text_widget = self.master.text_widgets[self.master.get_active_tab()]
        text_widget.tag_remove("match", 1.0, END)
        # check if the string to find is not empty
        if find_string:
            # get the index of the first match
            idx = text_widget.search(find_string, 1.0, END, nocase=True)
            # check if there is a match
            while idx:
                # get the last index of the match
                last_idx = f"{idx}+{len(find_string)}c"
                # add a tag to the match
                text_widget.tag_add("match", idx, last_idx)
                # make sure the match is visible
                text_widget.tag_configure("match", foreground="yellow")
                # update the number of matches
                self.matches_var.set(f"{len(text_widget.tag_ranges('match'))//2} matches")
                # # set the focus on the match
                # text_widget.tag_raise("match", "1.0")
                # replace the string
                text_widget.delete(idx, last_idx)
                text_widget.insert(idx, replace_string)
                # get the index of the next match
                idx = text_widget.search(find_string, idx, END)
            else:
                # if there is no match, display a message
                self.matches_var.set("No matches")

    def destroy(self):
        try:
            # set on destroy to remove foreground color
            self.master.text_widgets[self.master.get_active_tab()].tag_remove("match", 1.0, END)   
        except:
            pass
        super().destroy()    

class HighlightingText(ttk.Text):
    """
    this class creates tabs for the notebook

    """
    def __init__(self, master):
        super().__init__(master)
        # set the padding of the text widget
        #self.configure(padx=(20,0))
        self.master = master
        # add border to the text widget
        self.configure(
            borderwidth=4, 
            highlightthickness=2,
            highlightbackground="yellow",
            undo=True,
            maxundo=-1,
            font=(self.get_key_from_json("current_font_family"), self.get_key_from_json("current_font_size")),
            )
        # Initialize Enchant spell checker
        self.spell_checker = enchant.Dict("en_US")
        # add a vertical scrollbar to the text widget when there is more content 
        # than the height of the text widget
        # only show the scrollbar when the mouse is over the text widget
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        # change the cursor to an arrow when the mouse is over the scrollbar and 
        # to a bar when it is over the text widget
        self.scrollbar.bind("<Enter>", lambda event: self.configure(cursor="arrow"))
        self.scrollbar.bind("<Leave>", lambda event: self.configure(cursor="xterm"))
        # set error color
        self.tag_configure("error", underline=True, underlinefg="red")

        # set tags auto completion on key release
        self.bind("<KeyRelease>", self._on_key_release)
        # bind undo <<Undo>> and redo <<Redo>> to the text widget
        #self.bind("<<Undo>>", self.on_key_release)

        # ensure the tab is focused when the mouse is over the text widget
        self.bind("<Enter>", lambda event: self.focus_set())

        # bind to when the text widget is modified and set the name of the tab to have a * at the end if it is modified
        self.bind("<<Modified>>", self.on_modified)

        # 

    def get_key_from_json(self, key):
        try:
            # get the value of the key from the config.json file
            with open('config.json','r') as config_file:
                data = json.load(config_file)
                return data[key]
        except:
            # if the key does not exist, return None
            return str(10) if key == "current_font_size" else "Consolas"
    
    def on_modified(self, event=None):
        # get the name of the tab
        tab_name = self.master.tab(self.master.select(), "text")
        # check if the tab name ends with *
        if not tab_name.endswith("*"):
            # add * to the tab name
            self.master.tab(self.master.select(), text=tab_name+"*")

    def format_xml(self, element, indent=0):
        xml_str = ""
        if len(element):
            xml_str += "\t" * indent + f"<{element.tag}>\n"
            for child in element:
                xml_str += self.format_xml(child, indent+2)
            xml_str += "\t" * indent + f"</{element.tag}>\n"
        else:
            xml_str += "\t" * indent + f"<{element.tag}>"
            if element.text:
                xml_str += "\t" + element.text.strip() + "\n"
            else:
                xml_str += "\n"
        return xml_str


        # add a horizontal scrollbar to the text widget when there is more content
        # than the width of the text widget
        # self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.xview)
        # self.configure(xscrollcommand=self.scrollbar.set)
        # self.scrollbar.pack(side="bottom", fill="x")
    
    def syntax_highlight(self, event=None):
        """
        add syntax highlighting to the text widget to highlight xml tags and attributes and also comments
        change text color to blue for tags, green for attributes, red for values, gray for comments, and purple for strings
        """
        
        # remove blue and green tags from all tags
        self.tag_remove("blue", "1.0", END)
        self.tag_remove("green", "1.0", END)
        self.tag_remove("comment", "1.0", END)

        # remove blue foreground color from all tags


        # get the content of the text widget
        text = self.get("1.0", END)

        # defning pattern
        xml_declaration_pattern = re.compile(r'<\?xml.*\?>')

        # create a list of all tag names and tag endings
        """
        <\s*: matches the opening angle bracket and any whitespace before the tag name
        (\w+): captures the tag name (one or more word characters)
        (?:: starts a non-capturing group for the tag's attributes
        \s+\w+: matches any whitespace followed by an attribute name (one or more word characters)
        (?:: starts a non-capturing group for the attribute's value
        \s*=\s*: matches any whitespace around the equals sign
        (?:"[^"]*"|'[^']*'|[\w-]+): matches either a double-quoted string, a single-quoted string, or a word character or hyphen (allowed in unquoted attribute values)
        )?: closes the attribute value group and makes it optional
        )*: closes the attribute group and makes it repeatable (zero or more times)
        \s*/?\s*>: matches any whitespace and the closing angle bracket, with an optional forward slash for self-closing tags
        """
        tag_pattern =re.compile(r"(</?\w+)|([<>])")

        # regex to get the where the attributes start and end
        attribute_pattern = re.compile(r'\w+\s*=\s*["\'][^"\']*["\']')

        comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)

        # set any match of def_pattern to blue
        start = "1.0"
        while True:
            # search for next tag or angle bracket
            match = xml_declaration_pattern.search(self.get(start, "end"))
            if not match:
                break
            
            # get the start and end indexes of the match
            tag_start = f"{start}+{match.start()}c"
            tag_end = f"{start}+{match.end()}c"

            # apply blue tag to tag name or angle bracket
            self.tag_add("blue", tag_start, tag_end)
            self.tag_configure("blue", foreground="blue")

            # update start position for next search
            start = tag_end


        # search for tags and angle brackets
        start = "1.0"
        while True:
            # search for next tag or angle bracket
            match = tag_pattern.search(self.get(start, "end"))
            if not match:
                break
            
            # get the start and end indexes of the match
            tag_start = f"{start}+{match.start()}c"
            tag_end = f"{start}+{match.end()}c"

            # apply blue tag to tag name or angle bracket
            if match.group().startswith("<"):
                tag_name = match.group()[1:]
                self.tag_add("blue", tag_start, tag_end)
                self.tag_configure("blue", foreground="blue")
            elif match.group().startswith("</"):
                tag_name = match.group()[2:-1]
                self.tag_add("blue", tag_start, tag_end)
                self.tag_configure("blue", foreground="blue")
            elif match.group() == ">":
                # apply blue tag to angle bracket
                self.tag_add("blue", tag_start, tag_end)
                self.tag_configure("blue", foreground="blue")
            else:
                tag_name = None

            # search for next occurrence of the same tag name
            if tag_name:
                start = tag_end
                while True:
                    next_range = self.tag_nextrange("blue", start, "end")
                    if not next_range or next_range[0] >= tag_end:
                        break
                    self.tag_add("blue", next_range[0], next_range[1])
                    self.tag_configure("blue", foreground="blue")
                    start = next_range[1]
            else:
                start = tag_end

        # search for tags and angle brackets
        start = "1.0"
        while True:
            # highlight attributes
            match = attribute_pattern.search(self.get(start, "end"))
            if not match:
                break
            
            # get the start and end indexes of the match
            tag_start = f"{start}+{match.start()}c"
            tag_end = f"{start}+{match.end()}c"

            # get the start and end indexes of the match
            tag_start = f"{start}+{match.start()}c"
            tag_end = f"{start}+{match.end()}c"

            # highlight the match with green color
            self.tag_add("green", tag_start, tag_end)
            self.tag_configure("green", foreground="#239F0D")

            # update start position for next search
            start = tag_end

        # search for comments
        start = "1.0"
        while True:
            # highlight attributes
            match = comment_pattern.search(self.get(start, "end"))
            if not match:
                break
            
            # get the start and end indexes of the match
            tag_start = f"{start}+{match.start()}c"
            tag_end = f"{start}+{match.end()}c"

            # highlight the match with green color
            self.tag_add("comment", tag_start, tag_end)
            self.tag_configure("comment", foreground="gray")

            # update start position for next search
            start = tag_end
    
    def _on_key_release(self, event):
        #print(event.keysym)
        if not event.keysym in ["v","V","Control_L"]:
            #print(f"key pressed {event.keysym}")
            # add error highlighting
            self.highlight_errors()
            # trigger syntax highlighting
            self.syntax_highlight()
            # add auto completion
            self.autocomplete_tags(event)
            
        # add error highlighting
        self.highlight_errors()
        # trigger syntax highlighting
        self.syntax_highlight()

    def check_xml_syntax(self,xml_text):
        closing_tag_regex =re.compile(r'^\s*<\w+\s+[^>]+>|^\s*</\w+\s*>$|^\s*<\w+((\s+\w+\s*=\s*["\'][^"\']*["\'])*)\s*>[\s\S]*?</\w+\s*>$', re.DOTALL)
        comment_regex = re.compile(r'<!--.*-->')

        # Detect syntax errors in the XML text
        # if not root_regex.search(xml_text):
        #     return (None, 'XML documents must have a root element.')

        if not closing_tag_regex.search(xml_text):
            return (None, 'All XML elements must have a closing tag.')
        
        # if case_sensitive_regex.search(xml_text):
        #     return (None, 'XML tags are case-sensitive.')
        # if attribute_value_regex.search(xml_text):
        #     return (None, 'Attribute values cannot contain certain special characters.')
        # if entity_regex.search(xml_text):
        #     return (None, 'XML entities cannot be used.')

        if comment_regex.search(xml_text):
            return (None, 'XML comments are not allowed.')
        
        # if processing_instruction_regex.search(xml_text):
        #     return (None, 'XML processing instructions are not allowed.')

        # If there are no syntax errors, return None
        return (None, None)
    
    def highlight_errors(self, event=None):
        #print("highlight_errors")
        # Remove any existing error tags
        self.tag_remove("unclosed_tag", "1.0", "end")
        self.tag_remove("unclosed_attr", "1.0", "end")
        self.tag_remove("mistyped_word", "1.0", "end")

        # Get the XML content
        xml_content = self.get("1.0", END)

        closing_tag_pattern = re.compile(r'</\w+(?![^<]*>)')

        matches = closing_tag_pattern.finditer(xml_content)

        # Loop through all matches and highlight them in the text widget
        for match in matches:
            start = match.start()
            end = match.end()
            self.tag_add("unclosed_tag", f"1.0+{start}c", f"1.0+{end}c")
        
        word_regex = re.compile(r'\b\w+\b')
        # Loop over all words in the XML content
        for word in word_regex.findall(xml_content):
            # Check if the word is not in the Enchant dictionary
            # if word has underscore or its has numbers in it, ignore it
            if word=="xml" or"_" in word or any(char.isdigit() for char in word):
                continue
            elif not self.spell_checker.check(word):
                # find all matches for the word
                matches=re.finditer('\\b'+word+'\\b', xml_content)
                for match in matches:
                    start = match.start()
                    end = match.end()
                    self.tag_add("mistyped_word", f"1.0+{start}c", f"1.0+{end}c")

        # Apply error tag styles
        self.tag_configure("unclosed_tag", underline=True, underlinefg="red")
        # self.tag_configure("unclosed_attr", underline=True, underlinefg="blue")
        self.tag_configure("mistyped_word", underline=True, underlinefg="#BD08DD")

    def autocomplete_tags(self, event):
        char = event.char
        #print(char)
        # Only autocomplete if the character typed is ">"
        if char == ">":
            # Get the current position of the cursor
            index = self.index(INSERT)

            # Get the text before the cursor
            line, col = map(int, index.split('.'))
            line_text = self.get(f"{line}.0", f"{line}.{col}")
            before_cursor = line_text[:-1]

            # Get the tag name of the current open tag
            tag_name = ""
            for c in reversed(before_cursor):
                if c == "<":
                    break
                tag_name = c + tag_name

            # If the current tag is not closed, add the closing tag
            if before_cursor.endswith(f"<{tag_name}"):
                # Split tag name to remove attributes
                tag_parts = tag_name.split(" ")
                tag_name = tag_parts[0]
                #print(f'tag_name: {tag_name}')
                if not ("/" in tag_name or "?" in tag_name or "!" in tag_name):
                    # Insert the closing tag without attributes
                    self.insert(INSERT, f"</{tag_name}>")
                    
                    # set the cursor to be between the opening and closing tags
                    self.mark_set(INSERT, f"{line}.{col}")


root = ttk.Window(title="Interactive Xml Editor",)
app = App(master=root)
app.mainloop()


