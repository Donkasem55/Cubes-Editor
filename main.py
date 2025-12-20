import tkinter as tk
from tkinter import filedialog, ttk
import re, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

window = tk.Tk()
width, height = 800, 600
window.geometry(f"{width}x{height}")
window.title("Cubes Editor beta 1.2")
icon = tk.PhotoImage(file="icon.png")
window.iconphoto(True, icon)

filenames = []
widgets = []
sidebars = []
current_tab = 0

with open(BASE_DIR / "config" / "theme.json") as f:
    config = json.load(f)

with open(BASE_DIR / "config" / "highlight.json") as f:
    highlighting = json.load(f)
    
window.attributes("-alpha", config["alpha"])

s = ttk.Style()
s.theme_use("default")
s.configure('TNotebook', background=config["tabsBgColor"])
s.configure("TNotebook", borderwidth=0, highlightthickness=0, relief="flat", bordercolor=config["tabsBorderColor"])
s.configure("TNotebook.Tab", borderwidth=0, highlightthickness=0, relief="flat", bordercolor=config["tabsBorderColor"])
s.configure('TNotebook.Tab', background=config["tabsColor"])
s.configure('TNotebook.Tab', foreground=config["tabsTextColor"])
s.map("TNotebook.Tab", background=[("selected", config["tabsActiveColor"])])

topbar = tk.Frame(window, bg=config["topColor"], height=config["UIheight"])
topbar.pack(fill="x", side="top")

files = tk.Menubutton(topbar, text="File", bg=config["topColor"], fg=config["topTextColor"], activebackground=config["activeTopColor"], activeforeground=config["activeTopTextColor"], width=config["UIwidth"], bd=0, relief="flat")
files.pack(side="left")

filemenu = tk.Menu(files, tearoff=0, bg=config["topColor"], fg=config["topTextColor"], bd=0, relief="flat", activeborderwidth=0)

files["menu"] = filemenu

view = tk.Menubutton(topbar, text="View", bg=config["topColor"], fg=config["topTextColor"], activebackground=config["activeTopColor"], activeforeground=config["activeTopTextColor"], width=config["UIwidth"], bd=0, relief="flat")
view.pack(side="left")

viewmenu = tk.Menu(view, tearoff=0, bg=config["topColor"], fg=config["topTextColor"], bd=0, relief="flat", activeborderwidth=0)

view["menu"] = viewmenu

tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, side="left")

tab = ttk.Frame(tabs)
tabs.add(tab, text="Untitled.txt")

canvas = tk.Canvas(tab, bg=config["codeAreaColor"], highlightthickness=0)
canvas.pack(fill="both", expand=True, side="left")

scrollbar = tk.Scrollbar(tab, command=canvas.yview)
scrollbar.pack(fill="y", side="right")

canvas.configure(yscrollcommand=scrollbar.set)

frame = tk.Frame(canvas, bg=config["codeAreaColor"])
canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas_window, width=canvas.winfo_width())

frame.bind("<Configure>", on_configure)

sidebar = tk.Label(master=frame, text="1", font=(config["uiFont"], config["uiFontSize"]), bg=config["sideColor"], fg=config["sideTextColor"])
sidebar.pack(side="left", fill="y")

widget = tk.Text(master=frame, relief="flat", font=(config["editFont"], config["editFontSize"]), bg=config["codeAreaColor"], fg=config["codeAreaTextColor"], insertbackground=config["cursorColor"], width=2000)
widget.pack(side="left", fill="both", expand=True)

filenames.append("Untitled.txt")
sidebars.append(sidebar)
widgets.append(widget)

def add_text_proxy(text):
    orig = text._w + "_orig"
    text.tk.call("rename", text._w, orig)

    def proxy(cmd, *args):
        result = text.tk.call(orig, cmd, *args)

        if cmd in ("insert", "delete", "replace"):
            highlight(text)

        return result

    text.tk.createcommand(text._w, proxy)

add_text_proxy(widget)

def new_tab(name="Untitled.txt"):
    global config, current_tab

    tab_new = ttk.Frame(tabs)
    name__ = name.split("/")
    if len(name__) == 1:
        name__ = name.split("\\")
    name_ = name__[-1]
    tabs.add(tab_new, text=name_)

    canvas_new = tk.Canvas(tab_new, bg=config["codeAreaColor"], highlightthickness=0)
    canvas_new.pack(fill="both", expand=True, side="left")

    scrollbar_new = tk.Scrollbar(tab_new, command=canvas_new.yview)
    scrollbar_new.pack(fill="y", side="right")

    canvas_new.configure(yscrollcommand=scrollbar_new.set)

    frame_new = tk.Frame(canvas_new, bg=config["codeAreaColor"])
    canvas_window_new = canvas_new.create_window((0, 0), window=frame_new, anchor="nw")

    def on_configure_new(event):
        canvas_new.configure(scrollregion=canvas_new.bbox("all"))
        canvas_new.itemconfig(canvas_window_new, width=canvas_new.winfo_width())

    frame_new.bind("<Configure>", on_configure_new)

    sidebar_new = tk.Label(master=frame_new, text="1", font=(config["uiFont"], config["uiFontSize"]), bg=config["sideColor"],
                       fg=config["sideTextColor"])
    sidebar_new.pack(side="left", fill="y")

    widget_new = tk.Text(master=frame_new, relief="flat", font=(config["editFont"], config["editFontSize"]),
                     bg=config["codeAreaColor"], fg=config["codeAreaTextColor"], insertbackground=config["cursorColor"],
                     width=2000)
    widget_new.pack(side="left", fill="both", expand=True)
    add_text_proxy(widget_new)
    if name != "Untitled.txt":
        with open(name) as fle:
            widget_new.insert("1.0", fle.read())

    def on_mousewheel_new(event):
        canvas_new.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_new.bind_all("<MouseWheel>", on_mousewheel_new)

    widget_new.tag_config("keyword", foreground=config["keywordColor"])
    widget_new.tag_config("function", foreground=config["functionColor"])
    widget_new.tag_config("punct", foreground=config["puncColor"])
    widget_new.tag_config("string", foreground=config["stringColor"])
    widget_new.tag_config("num", foreground=config["numColor"])
    widget_new.tag_config("ops", foreground=config["opsColor"])
    widget_new.tag_config("bckslsh", foreground=config["bckslshColor"])

    filenames.append(name)
    widgets.append(widget_new)
    sidebars.append(sidebar_new)


def on_mousewheel(event):
    if event.delta:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif event.num == 4:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        canvas.yview_scroll(1, "units")

def openfile():
    newfile = filedialog.askopenfilename(
        title="Select a file",
        initialdir=".",
        filetypes=(
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("MarkDown source file", "*.md"),
            ("HyperText Markup Language webpages", "*.html *.htm"),
            ("Cascading Style Sheet source files", "*.css"),
            ("JavaScript source files", "*.js"),
            ("TypeScript source files", "*.ts"),
            ("Python files", "*.py *.pyw *.pyc"),
            ("C/C++ source files", "*.cpp *.cc *.c *.cp"),
            ("C# source files", "*.cs"),
            ("Java source files", "*.java"),
            ("Javascript Object Notations", "*.json"),
            ("Config files", "*.conf *.cfg *.config"),
            ("Batch scripts", "*.bat *.batch"),
            ("Bash scripts", "*.sh *.bsh *.bash"),
            ("Z Shell scripts", "*.zs *.zsh"),
            ("PowerShell scripts", "*.ps1"),
            ("Quantum Unified Shell scripts", "*.qus")
        )
    )
    if newfile == "":
        return
    new_tab(newfile)
    

def save():
    global current_tab
    file = widgets[current_tab].get("1.0", tk.END)
    name = filenames[current_tab]
    if name == "Untitled.txt":
        saveas()
    else:
        with open(name, "w") as fle:
            fle.write(file)

def saveas():
    global current_tab
    file = widgets[current_tab].get("1.0", tk.END)
    with filedialog.asksaveasfile(
        title="Select a file",
        initialdir=".",
        filetypes=(
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("MarkDown source file", "*.md"),
            ("HyperText Markup Language webpages", "*.html *.htm"),
            ("Cascading Style Sheet source files", "*.css"),
            ("JavaScript source files", "*.js"),
            ("TypeScript source files", "*.ts"),
            ("Python files", "*.py *.pyw *.pyc"),
            ("C/C++ source files", "*.cpp *.cc *.c *.cp"),
            ("C# source files", "*.cs"),
            ("Java source files", "*.java"),
            ("Javascript Object Notations", "*.json"),
            ("Config files", "*.conf *.cfg *.config"),
            ("Batch scripts", "*.bat *.batch"),
            ("Bash scripts", "*.sh *.bsh *.bash"),
            ("Z Shell scripts", "*.zs *.zsh"),
            ("PowerShell scripts", "*.ps1"),
            ("Quantum Unified Shell scripts", "*.qus")
        ),
        mode="w"
    ) as fle:
        if fle:
            fle.write(file)
            filenames[current_tab] = fle.name


filemenu.add_command(label="New tab", accelerator="Ctrl+N", command=new_tab)
filemenu.add_command(label="Open", accelerator="Ctrl+O", command=openfile)
filemenu.add_command(label="Save", accelerator="Ctrl+S", command=save)
filemenu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=saveas)

def openconf():
    new_tab(str(BASE_DIR / "config" / "theme.json"))

def openreadme():
    new_tab(str(BASE_DIR / "config" / "readme.md"))

def openhl():
    new_tab(str(BASE_DIR / "config" / "highlight.json"))

viewmenu.add_command(label="Config", command=openconf)
viewmenu.add_command(label="Highlighting", command=openhl)
viewmenu.add_command(label="README.md", command=openreadme)

canvas.bind_all("<MouseWheel>", on_mousewheel)
window.bind("<Control-n>", lambda e: new_tab())
window.bind("<Control-o>", lambda e: openfile())
window.bind("<Control-s>", lambda e: save())
window.bind("<Control-Shift-s>", lambda e: saveas())

window.option_add("*Menu.borderWidth", 0)
window.option_add("*Menu.activeBorderWidth", 0)
window.option_add("*Menu.relief", "flat")
window.option_add("borderColor", config["topColor"])

widget.tag_config("keyword", foreground=config["keywordColor"])
widget.tag_config("function", foreground=config["functionColor"])
widget.tag_config("punct", foreground=config["puncColor"])
widget.tag_config("string", foreground=config["stringColor"])
widget.tag_config("num", foreground=config["numColor"])
widget.tag_config("ops", foreground=config["opsColor"])
widget.tag_config("bckslsh", foreground=config["bckslshColor"])

KEYWORDS = highlighting["keywords"]
FUNCTIONS = highlighting["functions"]
PUNCT = highlighting["punct"]
STRINGS = highlighting["string"]
NUM = highlighting["num"]
OPS = highlighting["ops"]
BCKSLSH = highlighting["bckslsh"]
re_keywords = re.compile(KEYWORDS)
re_functions = re.compile(FUNCTIONS)
re_punct = re.compile(PUNCT)
re_strings = re.compile(STRINGS, re.DOTALL)
re_num = re.compile(NUM)
re_ops = re.compile(OPS)
re_bckslsh = re.compile(BCKSLSH)

def highlight(wid = widgets[current_tab]):
    wid.tag_remove("keyword", "1.0", "end")
    wid.tag_remove("function", "1.0", "end")
    wid.tag_remove("punct", "1.0", "end")
    wid.tag_remove("strings", "1.0", "end")

    text = wid.get("1.0", "end-1c")

    for m in re_keywords.finditer(text):
        start_off, end_off = m.start(), m.end()
        start_index = f"1.0+{start_off}c"
        end_index = f"1.0+{end_off}c"
        wid.tag_add("keyword", start_index, end_index)

    for m in re_functions.finditer(text):
        start_off, end_off = m.start(), m.end()
        start_index = f"1.0+{start_off}c"
        end_index = f"1.0+{end_off}c"
        wid.tag_add("function", start_index, end_index)

    for m in re_punct.finditer(text):
        start, end = m.start(), m.end()
        wid.tag_add(
            "punct",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )

    for m in re_num.finditer(text):
        start, end = m.start(), m.end()
        wid.tag_add(
            "num",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )

    for m in re_ops.finditer(text):
        start, end = m.start(), m.end()
        wid.tag_add(
            "ops",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )

    for m in re_strings.finditer(text):
        start, end = m.start(), m.end()
        wid.tag_add(
            "string",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )

    for m in re_bckslsh.finditer(text):
        start, end = m.start(), m.end()
        wid.tag_add(
            "bckslsh",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )


def update():
    global current_tab
    current_tab = tabs.index("current")
    text = widgets[current_tab].get("1.0", "end-1c")
    text_array = text.split("\n")
    text_add = ""
    for i in range(1, len(text_array)+1):
        text_add += f"{i}  \n"
    for i in range(40):
        text_add += "   \n"
    sidebars[current_tab].configure(text=text_add)

    highlight(widgets[current_tab])

    window.after(100, update)

def main():
    update()

    window.mainloop()
    
if __name__ == "__main__":
    main()

