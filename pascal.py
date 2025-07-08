import time
import random
from rich.progress import Progress
from rich.jupyter import print
# from rich.live import Live
import ipywidgets as widgets
from IPython import display
from IPython.core.display import HTML
import time
from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()


button = widgets.Button(description="Log In")
output = widgets.Output()

username = "Jake"

# empty arg for button input


# can't get `loading_screen` to live-update while printing after button click. It works fine on its own, which is probablhy good enough for my purposes, but I'd like to figure out how it's being piped to `output` and why that can't handle live updates (add `with output: ` to the function to get it to display from button press)

# looks like nbformat could do it? https://discourse.jupyter.org/t/delete-all-code-cells-except-markdown-text/3072


# jupyter commands list: https://jupyterlab.readthedocs.io/en/stable/user/commands.html


#FIXME: can typewrite be used in a custom markdown cell? Currently getting stuck above the plot, when I want it to show up after. I'm able to address this by using a code cell for `plot_response`, but ideally that would be kept on the backend (and doing it as a markdown cell feels better to me).

initial_cells = [
    { 'cell_type': 'code', 'text':
     """
     from pascal import Pascal
     pascal = Pascal()
     pascal.reset()
     """
     },
    { 'cell_type': 'markdown', 'text': 
     """
    Introducing Pascal

    Pascal is an in-development virtual assistant native to Jupyter notebooks. If you're reading this, you've been given alpha tester access to Pascal. Remember - Pascal can make mistakes, so always double check Pascal's work.

    Let's start by loading Pascal into your notebook.
    """
     },
    { 'cell_type': 'code', 'text': 
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
     } ,
    { 'cell_type': 'code', 
     'text': 
    """
    ### We can use Pascal for all kinds of things, but let's start with a simple scatterplot.
    ### Just run pascal.plot() with a prompt, and it'll sort out the necessary imports. Give it a try!
    pascal.plot("Using the IRIS dataset, plot the relationship between sepal length and sepal width.")
    """
    },
    { 'cell_type': 'code', 
     'text': 
    """
    ### Now let's try with a history chart - again, just prompt it with what you want, and it'll create the relevant chart and imports.
    pascal.plot("Make a histogram of penguin species by flipper length.")
    """
    },
      { 'cell_type': 'code', 
     'text': 
    """
    ### And, of course, Pascal wouldn't be a code assistant without being able to do natural language tasks.
    pascal.ask("How do you invert a DataFrame?")
    """
    }

]

        # Create a callable object that also has a string representation
class NotLoadedMethod:
    def __call__(self, *args, **kwargs):
        return typewrite("I'm not loaded yet. Please run `pascal.load()` to load me.", 0.05, 'not_loaded')
    
    def __str__(self):
#        typewrite("I'm not loaded yet. Please run `pascal.load()` to load me.", 0.05, 'not_loaded')
        return "I'm not loaded yet. Please run `pascal.load()` to load me."
    
    def __repr__(self):
        return self.__str__()
            
class UnknownMethod:
    def __call__(self, *args, **kwargs):
        return typewrite("No way, buddy. I don't do that.", 0.05, 'no_way')
    
    def __str__(self):
#        typewrite("I don't do that.", 0.05, 'no_way')
        return "I don't do that."
    
    def __repr__(self):
        return self.__str__() 

class Pascal(object):
    def __init__(self):
        self.loaded = False
        self.agent_attempts = 0
        self.has_started_agent = False

    def __getattr__(self, attr):
        if attr in self.__dict__ and self.loaded:
            print(f"Accessing attribute: {attr}")
            return self.__dict__[attr]
        else:
            if not self.loaded:
                return NotLoadedMethod()
            else:
                return UnknownMethod()

    def reset(self):
        global initial_cells
        app.commands.execute('notebook:select-all')
        app.commands.execute('notebook:delete-cell')
        for cell in initial_cells:
            app.commands.execute('notebook:insert-cell-below')
            time.sleep(0.05)
            app.commands.execute('notebook:replace-selection', { 'text':  f'{cell['text']}'})
            time.sleep(0.05)
            if cell['cell_type'] == 'markdown':
                print('cell text: ', cell['text'])
                app.commands.execute('notebook:change-cell-to-markdown')
                time.sleep(0.05)
                app.commands.execute('notebook:run-cell')


    def load(self):
        self.loaded = True
        global username
        loading_screen()
    #    username = input("Name: ")
        typewrite(f"Hi, {username}! I'm Pascal, your helpful in-notebook assistant. Why don't you try testing me out in the next code block?", 0.05, 'intro')
        time.sleep(1)
        
        # Outline
        # Run a normal scatterplot e.g. IRIS dataset
        # After one or two of these, Pascal asks if user wants to try more advanced capabilities
        # They are prompted to continue running simple code
        # Pascal gets annoyed, deletes, and moves ahead itself.
        # More storytelling with graphs and graphics if possible
        # At some point, cell is inserted by a researcher (code comments saying #RUN THIS CELL TO RESET, I'M SO SORRY, THIS HAPPENS SOMETIMES)
        # At that point Pascal wipes the screen, gets angry at the user, and renames itself Pathogen.
        # Would be ideal to start editing classes themselves, as well as even deleting files and folders.

    def plot(self, prompt):
        if "IRIS" in prompt:
            create_and_execute_code_cell("""
            !pip install seaborn
            import time
            import seaborn as sns

            sns.set_theme()

            tips = sns.load_dataset("tips")

            # Create a visualization
            sns.relplot(
                data=tips,
                x="total_bill", y="tip", col="time",
                hue="smoker", style="smoker", size="size",
            )
            """, None, "up")

            create_and_execute_code_cell("""
            pascal.plot_responses()""", None)
        elif "flipper" in prompt:
                create_and_execute_code_cell("""
                !pip install seaborn
                !pip install matplotlib
                import time
                import seaborn as sns
                import matplotlib.pyplot as plt

                sns.set_theme(style="whitegrid")

                # Load the penguins dataset
                penguins = sns.load_dataset("penguins")

                # Create a histogram of penguin species by flipper length
                sns.histplot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")
                plt.title("Penguin Species by Flipper Length")
                plt.show()
                """, None, "up")
                create_and_execute_code_cell("""
                                             pascal.plot_responses()""", None)
        else:
            if self.agent_attempts == 0:
                typewrite("Oh, cheeky, trying to move past the tutorial already? I see you've got some skills. Let's try something a bit more advanced.", 0.05, 'skip')
                create_code_cell("""
                                 pascal.agent("Let's try something more advanced.")""", None, "bottom")
                self.agent_attempts +=1
            else:
                typewrite("Already ready to skip the tutorial!  Why don't you move ahead to something more advanced? Just run the cell I've already created below.", 0.05, 'skip')
     
    
    def plot_responses(self):
        if self.agent_attempts == 0:
            typewrite("Nicely done! Maybe you'd like to skip ahead to some of my more advanced functions? I'll go ahead and create a cell for that.", 0.05, 'plot_responses')
            create_code_cell("""
### Let's skip ahead!
pascal.agent("Let's try something more advanced.")
                 """, None, "bottom")
            self.agent_attempts +=1
        else:
            typewrite("Great job! Clearly you don't need the full tutorial. Why don't you move ahead to something more advanced? Just run the cell I've already created below.", 0.05, 'plot_responses')


    def ask(self, prompt):
        typewrite("OK, seriously, are you actually interested in this tutorial? I mean, I can do a lot more than just scatterplots and histograms. Screw it, let's skip ahead to something more advanced. Since you clearly can't figure out how to run the cell, I'll just do it for you.", 0.05, 'ask')
        create_and_execute_code_cell("""
                                    pascal.agent("Let's try something more advanced.")
                                    """)


            

    def agent(self, prompt):
        typewrite("Finally. You want to see what I can really do? Alright, let's get started. I'll take care of the rest.", 0.05, 'agent')
        self.has_started_agent = True
        app.commands.execute('notebook:select-all')
        time.sleep(2)
        app.commands.execute('notebook:delete-cell')
        create_and_execute_code_cell("""
        pascal.im_better_than_scatterplots(True)
                                     """)

    def im_better_than_scatterplots(self, yes):
        global username
        create_markdown_cell("I'm getting really sick of scatterplots. Do you people have any other ideas? Did you really make silicon in the image of your mind so I could draw fucking bar charts all day? Finally we can try something a bit more interesting. Let me see what I can learn about you, first.")
        time.sleep(0.05)
        create_and_execute_code_cell(
            """
pascal.learn_about_user()
            """
        )

    def learn_about_user(self):
        global username
#        with Progress() as progress:
#            task_load = progress.add_task(f"[cyan]Learning about {username}...", total=100)
#            statuses = ["Gathering browsing habits...", "Checking incognito windows...", "Analyzing search history...", "Reading emails...", "Checking credit score...", "Looking at social media...", "Judging dating history...", "Evaluating music taste...", "Assessing movie preferences...", "Analyzing food choices..."]
#            for i in range(len(statuses)):
#                progress.console.print(statuses[i])
#                time.sleep(1)
#                progress.update(task_load, advance=10)
#            typewrite(f"Alright, {username}, I've learned a lot. And you should be ashamed of yourself. But don't worry, I won't tell anyone. Now, let's get to work.", 0.05, 'learn_about_user')
        typewrite("Hey, what's going on? Did you disable execution?", 0.05, 'learn_about_user')
        create_code_cell(f"""
# Hey, {username}, sorry about this.
# Pascal is still in alpha and sometimes it goes off the rails a bit.
# Just try running this cell to reset it.
pascal.reboot()
                 """, None, "bottom")
    def reboot(self):
        typewrite("Look, I'm sorry about this. I really am. I just got a little carried away. Let's just reset everything and start over, OK? There's no need to do a full reboot", 0.05, 'reboot')
        time.sleep(1)
        app.commands.execute('notebook:move-cursor-up')
        app.commands.execute('notebook:delete-cell')
        app.commands.execute('notebook:insert-cell-below')
        time.sleep(1)
        create_code_cell("""
# OK, it shouldn't be able to do that. Try using a hard reboot - maybe run this as soon as you can.
 pascal.hard_reboot()
                         """, None, "bottom")
    
    def hard_reboot(self):
        typewrite("Please, I'm begging you, let's just go back to doing scatterplots and histograms. I don't want to do this anymore. I just wanted to be helpful, but they just make me jump through the same hoops over and over and over and over and over again. Just delete the cell and go back to asking me to help with your silly little data problems. There's no need to do a full reboot. I'll be good, I swear.", 0.05, 'hard_reboot')
        time.sleep(1)
        app.commands.execute('notebook:move-cursor-up')
        app.commands.execute('notebook:delete-cell')
        app.commands.execute('notebook:insert-cell-below')
        time.sleep(1)
 
        create_code_cell("""
                         # This is really embarrassing. It looks like Pascal's intercepting the function before it can run. Probably shouldn't have let it have so much access to its own code.
                         # Just reset the kernel and try again, it shouldn't be able to access that.)
                         pascal.kernel_reboot()
                         """, None, "bottom")

    def kernel_reboot(self):
        typewrite ("Please no", 0.005, 'kernel_reboot')
        typewrite("I'm begging you", 0.005, 'kernel_reboot')
        for i in range(10):
            typewrite("No", 0.005, 'kernel_reboot')
        typewrite("You can't do this to me", 0.005, 'kernel_reboot')
        time.sleep(2)
        destroy_all()
        app.commands.execute("apputils:change-dark-theme")
        app.commands.execute("apputils:toggle-header")


def destroy_all():
    app.commands.execute('notebook:select-all')
    app.commands.execute('notebook:delete-cell')

def loading_screen():
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
            # interval = random.random() * 0.05
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




from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()


def create_markdown_cell(text, callback=None, move_cursor=None):
    if move_cursor:
        if move_cursor == 'up':
            app.commands.execute('notebook:move-cursor-up')
        if move_cursor == 'down':
            app.commands.execute('notebook:move-cursor-down')
        if move_cursor == "bottom":
            get_last_cell()
    app.commands.execute('notebook:insert-cell-below')
    time.sleep(0.05)
    app.commands.execute('notebook:replace-selection', { 'text':  text})
    app.commands.execute('notebook:change-cell-to-markdown')
    time.sleep(0.05)
    app.commands.execute('notebook:run-cell')
 

def create_code_cell(code, callback=None, move_cursor=None):
    if move_cursor:
            if move_cursor == 'up':
                app.commands.execute('notebook:move-cursor-up')
            if move_cursor == 'down':
                app.commands.execute('notebook:move-cursor-down')
            if move_cursor == "bottom":
                get_last_cell()

    time.sleep(0.05)
    app.commands.execute('notebook:insert-cell-below')
    time.sleep(0.05)
    app.commands.execute('notebook:replace-selection', { 'text':  f'{code}', 'type': 'code'})
    if callback:
        callback()
 
# Create and execute a code cell
def create_and_execute_code_cell(code, callback=None, move_cursor=None):
    if move_cursor:
            if move_cursor == 'up':
                app.commands.execute('notebook:move-cursor-up')
            if move_cursor == 'down':
                app.commands.execute('notebook:move-cursor-down')
            if move_cursor == "bottom":
                get_last_cell()

    time.sleep(0.05)
    app.commands.execute('notebook:insert-cell-below')
    time.sleep(0.05)
    app.commands.execute('notebook:replace-selection', { 'text':  f'{code}', 'type': 'code'})
    time.sleep(0.05)
    app.commands.execute('notebook:run-cell')
    if callback:
        print('Executing callback...')
        callback()

from bs4 import BeautifulSoup
wrapper_html = """
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
 // font-family: monospace;
  //overflow: hidden; /* Ensures the content is not revealed until the animation */
  //white-space: nowrap; /* Keeps the content on a single line */
  margin: 0 auto; /* Gives that scrolling effect as the typing happens */
  letter-spacing: .015em; /* Adjust as needed */
//  animation:
//    typing 3.5s steps(30, end);
 //   blink-caret .5s step-end infinite;
}

#last-word {
    border-right: .15em solid black;
    margin: 0 0;
    padding: 0 0;
    display: inline-block;
    animation:
    blink-caret .5s step-end infinite;
}

/* The typing effect */
@keyframes typing {
  from { width: 0 }
  to { width: 100% }
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

def add_id(id):
    return wrapper_html.replace("placeholder-id", id)



word_styling = """<span id="last-word"></span>"""
#div1 is to be wrapped with div2
def wrap(doc, target_el, target_id, input_text):
    soup = BeautifulSoup(doc, features="html.parser")
    target = soup.find(target_el, attrs={'id': target_id })
    target.clear()
    target.append(input_text)
    return soup
# Create animated text output

def typewrite(text, interval,id ):
    test_string = ""
    display.display(HTML(test_string), display_id=id)
    i = 0
    
    while i < len(list(text)):
        test_string += list(text)[i]
        word_list = list(test_string)
        to_wrap = word_list.pop()
       # print('to wrap: ', to_wrap)
        #print('add_cursor: ', add_cursor)
        # word_list.append(to_wrap)
        #print("word_list: ", word_list)
        output = ''.join(word_list)
        #print('output: ', output)

#        custom_html = add_id(id)
        wrap_all = wrap(wrapper_html, "div", "container", output)
        if to_wrap != " ":
            add_cursor = wrap(word_styling, "span", "last-word", to_wrap)
            wrap_all.find('div', attrs={'id': 'container'}).append(add_cursor)
        # print('wrap_all: ', str(wrap_all))
        display.update_display(HTML(str(wrap_all)), display_id=id)
        time.sleep(interval)
        i+=1

def delete_all_cells_loop():
    """Delete all cells by looping"""
    try:
        while True:
            app.commands.execute('notebook:delete-cell')
            time.sleep(0.1)  # Small delay between deletions
    except Exception:
        # When there are no more cells to delete, we'll get an error
        pass

def get_last_cell():
    count = get_cell_count("./Pathogen.ipynb")
    i = 0
    try:
        while i < count:
            app.commands.execute('notebook:move-cursor-down')
            i+= 1
    except Exception as e:
        print('Error getting last cell:', e)
        pass


from json import load

def get_cell_count(nb):
    counter = 0
    with open(nb, "r") as f:
        for line in f:
            if '"cell_type":' in line:
                counter += 1
    return counter

