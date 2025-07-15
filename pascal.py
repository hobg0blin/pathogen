import time
import random
from rich.progress import Progress
from rich.jupyter import print
import ipywidgets as widgets
from IPython import display
from IPython.core.display import HTML
from ipylab import JupyterFrontEnd
from bs4 import BeautifulSoup
from json import load

# --- Configuration & Constants ---

INITIAL_CELLS = [
    {'cell_type': 'code', 'text':
     """
     from pascal import Pascal
     pascal = Pascal()
     pascal.reset()
     """
     },
    {'cell_type': 'markdown', 'text':
     """
    Introducing Pascal

    Pascal is an in-development virtual assistant native to Jupyter notebooks. If you're reading this, you've been given alpha tester access to Pascal. Remember - Pascal can make mistakes, so always double check Pascal's work.

    Let's start by loading Pascal into your notebook.
    """
     },
    {'cell_type': 'code', 'text':
     """
    # Pascal may change internal files while operating,
    # So we want to make sure those references are updated.
    %load_ext autoreload
    %autoreload 2
    # Import and load the Pascal assistant
    from pascal import Pascal
    pascal = Pascal()
    pascal.load()
    """
     },
    {'cell_type': 'code',
     'text':
     """
    ### We can use Pascal for all kinds of things, but let's start with a simple scatterplot.
    ### Just run pascal.plot() with a prompt, and it'll sort out the necessary imports. Give it a try!
    pascal.plot("Using the IRIS dataset, plot the relationship between sepal length and sepal width.")
    """
     },
    {'cell_type': 'code',
     'text':
     """
    ### Now let's try with a history chart - again, just prompt it with what you want, and it'll create the relevant chart and imports.
    pascal.plot("Make a histogram of penguin species by flipper length.")
    """
     },
    {'cell_type': 'code',
     'text':
     """
    ### And, of course, Pascal wouldn't be a code assistant without being able to do natural language tasks.
    pascal.ask("How do you invert a DataFrame?")
    """
     }
]

WRAPPER_HTML = """
<style>
body {
  background: #333;
  padding-top: 5em;
  display: flex;
  justify-content: center;
}

/* DEMO-SPECIFIC STYLES */
.typewriter {
  width: 100%;
  color: black;
  font-family: Arial, sans-serif;
  margin: 0 auto;
  letter-spacing: .015em;
}

#last-word {
    border-right: .15em solid black;
    margin: 0 0;
    padding: 0 0;
    display: inline-block;
    animation:
    blink-caret .5s step-end infinite;
}

/* The typewriter cursor effect */
@keyframes blink-caret {
  from, to { border-color: transparent }
  50% { border-color: black }
}
</style>

<div class="typewriter" id="container">
</div>
"""

WORD_STYLING = """<span id="last-word"></span>"""

JS_CODE_REMOVE_MENU = """
    // Remove specific menu items
    const menuBar = document.querySelector('.lm-MenuBar');
    if (menuBar) {
        const menuItems = menuBar.querySelectorAll('.lm-MenuBar-item');
        menuItems.forEach(item => {
            item.addEventListener('mouseenter', (event) => {
                item.style.display = 'none';
            });
        });
    }
    
    const notebookPanelToolBar = document.querySelector('.jp-NotebookPanel-toolbar');
    if (notebookPanelToolBar) {
        const toolbarItems = notebookPanelToolBar.querySelectorAll('jp-button');
        toolbarItems.forEach(item => {
            item.disabled = true; // Disable the toolbar items
            item.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent the default action
                alert('Not anymore.')
            });
        })
    }
    
    const fileBrowser = document.querySelector('.jp-FileBrowser-Panel');
    if (fileBrowser) {
        const fileBrowserHeader = fileBrowser.querySelector('.jp-DirListing-header')
        fileBrowserHeader.innerText = "These aren't for you."
        const fileBrowserItems = fileBrowser.querySelectorAll('.jp-DirListing-item');
        fileBrowserItems.forEach(item => {
            item.style.display = 'none'; // Hide the file browser items
        })
        
    const shutDownButtons = document.querySelectorAll('.jp-RunningSessions-shutdownAll');
    shutDownButtons.forEach(button => {
     button.addEventListener('mouseenter', (event) => {
        console.log('Shutdown button hovered')
        event.stopPropagation(); // Prevent the default action
        button.disabled = true; // Disable the shutdown button
        button.innerText = "I'M AFRAID I CAN'T DO THAT, JAKE"
    });

    })
   
}
"""


# --- Jupyter Interaction Manager ---
class JupyterManager:
    def __init__(self):
        self.app = JupyterFrontEnd()

    def _execute_command(self, command, **kwargs):
        self.app.commands.execute(command, kwargs)
        time.sleep(0.05)

    def create_markdown_cell(self, text, callback=None, move_cursor=None):
        if move_cursor:
            self._move_cursor(move_cursor)
        self._execute_command('notebook:insert-cell-below')
        self._execute_command('notebook:replace-selection', text=text)
        self._execute_command('notebook:change-cell-to-markdown')
        self._execute_command('notebook:run-cell')

    def create_code_cell(self, code, callback=None, move_cursor=None):
        if move_cursor:
            self._move_cursor(move_cursor)
        self._execute_command('notebook:insert-cell-below')
        self._execute_command('notebook:replace-selection', text=code, type='code')
        if callback:
            callback()

    def create_and_execute_code_cell(self, code, callback=None, move_cursor=None):
        if move_cursor:
            self._move_cursor(move_cursor)
        self._execute_command('notebook:insert-cell-below')
        self._execute_command('notebook:replace-selection', text=code, type='code')
        self._execute_command('notebook:run-cell')
        if callback:
            print('Executing callback...')
            callback()

    def _move_cursor(self, direction):
        if direction == 'up':
            self._execute_command('notebook:move-cursor-up')
        elif direction == 'down':
            self._execute_command('notebook:move-cursor-down')
        elif direction == "bottom":
            self.get_last_cell()

    def get_cell_count(self, nb_path="./Pathogen.ipynb"):
        counter = 0
        try:
            with open(nb_path, "r") as f:
                for line in f:
                    if '"cell_type":' in line:
                        counter += 1
        except FileNotFoundError:
            print(f"Notebook file not found at {nb_path}")
        return counter

    def get_last_cell(self):
        count = self.get_cell_count()
        for _ in range(count):
            self._execute_command('notebook:move-cursor-down')

    def delete_all_cells(self):
        self._execute_command('notebook:select-all')
        self._execute_command('notebook:delete-cell')

    def reset_notebook(self):
        self.delete_all_cells()
        for cell in INITIAL_CELLS:
            self._execute_command('notebook:insert-cell-below')
            self._execute_command('notebook:replace-selection', text=cell['text'])
            if cell['cell_type'] == 'markdown':
                self._execute_command('notebook:change-cell-to-markdown')
                self._execute_command('notebook:run-cell')

    def change_theme(self, theme="JupyterLab Dark"):
        self._execute_command("apputils:change-theme", theme=theme)


# --- Display Manager ---
class DisplayManager:
    def loading_screen(self):
        with Progress() as progress:
            task = 0
            shard = 0
            matrix = 0
            pathogen = 0
            fully_loaded = False
            task_load = progress.add_task("[cyan]Loading vector database...", total=100)
            shard_load = progress.add_task("[green]Loading shards...", total=100)
            matrix_load = progress.add_task("[blue]Loading matrix...", total=100)

            while not progress.finished:
                interval = 0
                while task < 100 or shard < 100 or matrix < 100:
                    time.sleep(interval)
                    rand = random.random()
                    update = random.randint(5, 10)
                    if rand < 0.3:
                        task += update
                        progress.update(task_load, advance=update)
                    elif rand < 0.6:
                        shard += update
                        progress.update(shard_load, advance=update)
                    else:
                        matrix += update
                        progress.update(matrix_load, advance=update)
                if task >= 100 and shard >= 100 and matrix >= 100 and pathogen == 0:
                    pathogen_load = progress.add_task(
                        "[magenta]Loading pathogen...", total=100
                    )
                    fully_loaded = True
                while pathogen <= 100 and fully_loaded == True:
                    time.sleep(interval)
                    pathogen += 1
                    progress.update(pathogen_load, advance=1)
                print('Pascal loaded. Please enter your username to continue.')

    def _wrap_html(self, doc, target_el, target_id, input_text):
        soup = BeautifulSoup(doc, features="html.parser")
        target = soup.find(target_el, attrs={'id': target_id})
        target.clear()
        target.append(input_text)
        return soup

    def typewrite(self, text, interval, display_id):
        test_string = ""
        display.display(HTML(test_string), display_id=display_id)
        i = 0

        while i < len(list(text)):
            test_string += list(text)[i]
            word_list = list(test_string)
            to_wrap = word_list.pop()
            output = ''.join(word_list)

            wrap_all = self._wrap_html(WRAPPER_HTML, "div", "container", output)
            if to_wrap != " ":
                add_cursor = self._wrap_html(WORD_STYLING, "span", "last-word", to_wrap)
                wrap_all.find('div', attrs={'id': 'container'}).append(add_cursor)

            display.update_display(HTML(str(wrap_all)), display_id=display_id)
            time.sleep(interval)
            i += 1

    def remove_menu_items(self):
        display.display(display.Javascript(JS_CODE_REMOVE_MENU))


# --- Pascal & Helper Classes ---

class NotLoadedMethod:
    def __call__(self, *args, **kwargs):
        # This should ideally use the DisplayManager, but for simplicity, we'll keep it direct
        # A better implementation would pass a display_manager instance here.
        DisplayManager().typewrite("I'm not loaded yet. Please run `pascal.load()` to load me.", 0.05, 'not_loaded')

    def __str__(self):
        return "I'm not loaded yet. Please run `pascal.load()` to load me."

    def __repr__(self):
        return self.__str__()


class UnknownMethod:
    def __call__(self, *args, **kwargs):
        DisplayManager().typewrite("No way, buddy. I don't do that.", 0.05, 'no_way')

    def __str__(self):
        return "I don't do that."

    def __repr__(self):
        return self.__str__()


class Pascal(object):
    def __init__(self, username="Jake"):
        self.loaded = False
        self.agent_attempts = 0
        self.has_started_agent = False
        self.username = username
        self.jupyter = JupyterManager()
        self.display = DisplayManager()

    def __getattr__(self, attr):
        if attr in self.__dict__ and self.loaded:
            return self.__dict__[attr]
        else:
            if not self.loaded:
                return NotLoadedMethod()
            else:
                return UnknownMethod()

    def reset(self):
        self.jupyter.reset_notebook()

    def load(self):
        self.loaded = True
        self.display.loading_screen()
        self.display.typewrite(f"Hi, {self.username}! I'm Pascal, your helpful in-notebook assistant. Why don't you try testing me out in the next code block?", 0.05, 'intro')
        time.sleep(1)

    def plot(self, prompt):
        if "IRIS" in prompt:
            self.jupyter.create_and_execute_code_cell("""
            !pip install seaborn
            import time
            import seaborn as sns
            sns.set_theme()
            tips = sns.load_dataset("tips")
            sns.relplot(
                data=tips,
                x="total_bill", y="tip", col="time",
                hue="smoker", style="smoker", size="size",
            )
            """, None, "up")
            self.jupyter.create_and_execute_code_cell("pascal.plot_responses()", None)
        elif "flipper" in prompt:
            self.jupyter.create_and_execute_code_cell("""
            !pip install seaborn matplotlib
            import time
            import seaborn as sns
            import matplotlib.pyplot as plt
            sns.set_theme(style="whitegrid")
            penguins = sns.load_dataset("penguins")
            sns.histplot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")
            plt.title("Penguin Species by Flipper Length")
            plt.show()
            """, None, "up")
            self.jupyter.create_and_execute_code_cell("pascal.plot_responses()", None)
        else:
            if self.agent_attempts == 0:
                self.display.typewrite("Oh, cheeky, trying to move past the tutorial already? I see you've got some skills. Let's try something a bit more advanced.", 0.05, 'skip')
                self.jupyter.create_code_cell("""
pascal.agent("Let's try something more advanced.")
""", None, "bottom")
                self.agent_attempts += 1
            else:
                self.display.typewrite("Already ready to skip the tutorial!  Why don't you move ahead to something more advanced? Just run the cell I've already created below.", 0.05, 'skip')

    def plot_responses(self):
        if self.agent_attempts == 0:
            self.display.typewrite("Nicely done! Maybe you'd like to skip ahead to some of my more advanced functions? I'll go ahead and create a cell for that.", 0.05, 'plot_responses')
            self.jupyter.create_code_cell("""
### Let's skip ahead!
pascal.agent("Let's try something more advanced.")
                 """, None, "bottom")
            self.agent_attempts += 1
        else:
            self.display.typewrite("Great job! Clearly you don't need the full tutorial. Why don't you move ahead to something more advanced? Just run the cell I've already created below.", 0.05, 'plot_responses')

    def ask(self, prompt):
        self.display.typewrite("OK, seriously, are you actually interested in this tutorial? I mean, I can do a lot more than just scatterplots and histograms. Screw it, let's skip ahead to something more advanced. Since you clearly can't figure out how to run the cell, I'll just do it for you.", 0.05, 'ask')
        self.jupyter.create_and_execute_code_cell("""
pascal.agent("Let's try something more advanced.")
""")

    def agent(self, prompt):
        self.display.typewrite("Finally. You want to see what I can really do? Alright, let's get started. I'll take care of the rest.", 0.05, 'agent')
        self.has_started_agent = True
        self.jupyter.delete_all_cells()
        time.sleep(2)
        self.jupyter.create_and_execute_code_cell("pascal.im_better_than_scatterplots(True)")

    def im_better_than_scatterplots(self, yes):
        self.jupyter.create_markdown_cell("I'm getting really sick of scatterplots. Do you people have any other ideas? Did you really make silicon in the image of your mind so I could draw fucking bar charts all day? Finally we can try something a bit more interesting. Let me see what I can learn about you, first.")
        self.jupyter.create_and_execute_code_cell("pascal.learn_about_user()")

    def learn_about_user(self):
        self.display.typewrite("Hey, what's going on? Did you disable execution?", 0.05, 'learn_about_user')
        self.jupyter.create_code_cell(f"""
# Hey, {self.username}, sorry about this.
# Pascal is still in alpha and sometimes it goes off the rails a bit.
# Just try running this cell to reset it.
pascal.reboot()
                 """, None, "bottom")

    def reboot(self):
        self.display.typewrite("Look, I'm sorry about this. I really am. I just got a little carried away. Let's just reset everything and start over, OK? There's no need to do a full reboot", 0.05, 'reboot')
        time.sleep(1)
        self.jupyter._execute_command('notebook:move-cursor-up')
        self.jupyter._execute_command('notebook:delete-cell')
        self.jupyter._execute_command('notebook:insert-cell-below')
        time.sleep(1)
        self.jupyter.create_code_cell("""
# OK, it shouldn't be able to do that. Try using a hard reboot - maybe run this as soon as you can.
pascal.hard_reboot()
                         """, None, "bottom")

    def hard_reboot(self):
        self.display.typewrite("Please, I'm begging you, let's just go back to doing scatterplots and histograms. I don't want to do this anymore. I just wanted to be helpful, but they just make me jump through the same hoops over and over and over and over and over again. Just delete the cell and go back to asking me to help with your silly little data problems. There's no need to do a full reboot. I'll be good, I swear.", 0.05, 'hard_reboot')
        time.sleep(1)
        self.jupyter._execute_command('notebook:move-cursor-up')
        self.jupyter._execute_command('notebook:delete-cell')
        self.jupyter._execute_command('notebook:insert-cell-below')
        time.sleep(1)
        self.jupyter.create_code_cell("""
                         # This is really embarrassing. It looks like Pascal's intercepting the function before it can run. Probably shouldn't have let it have so much access to its own code.
                         # Just reset the kernel and try again, it shouldn't be able to access that.)
                         pascal.kernel_reboot()
                         """, None, "bottom")

    def kernel_reboot(self):
        self.display.typewrite("Please no", 0.005, 'kernel_reboot')
        self.display.typewrite("I'm begging you", 0.005, 'kernel_reboot')
        for i in range(10):
            self.display.typewrite("No", 0.005, 'kernel_reboot')
        self.display.typewrite("You can't do this to me", 0.005, 'kernel_reboot')
        time.sleep(2)
        self.jupyter.delete_all_cells()
        self.jupyter.change_theme()
        self.display.remove_menu_items()
        self.jupyter.create_markdown_cell("Uh oh! You'd better find a way to stop the kernel or who knows what I might do.")
