import time
import random
from rich.progress import Progress
from rich.jupyter import print
# from rich.live import Live
import ipywidgets as widgets
from IPython import display
from IPython.core.display import HTML


button = widgets.Button(description="Log In")
output = widgets.Output()

username = ""

# empty arg for button input


# can't get `loading_screen` to live-update while printing after button click. It works fine on its own, which is probablhy good enough for my purposes, but I'd like to figure out how it's being piped to `output` and why that can't handle live updates (add `with output: ` to the function to get it to display from button press)

def run():
    global username
    loading_screen(0.00001)
    create_and_execute_code_cell("""
    import time
    from ipylab import JupyterFrontEnd
    app = JupyterFrontEnd()
    from setup import typewrite 
    username = input("Username: ")
    typewrite(f"Welcome to Pathogen, {username}!", 0.05)
    print(f"I'm not interested in you, {username}.")
    time.sleep(1)
    #TODO figure out how to delete cell after running it
    app.commands.execute('notebook:delete-cells')
    """)

def loading_screen(interval):
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
            print('TEST Pathogen loaded. Please enter your username to continue.')




from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()

# Create and execute a code cell
def create_and_execute_code_cell(code):
    app.commands.execute('notebook:insert-cell-below')
    time.sleep(0.05)
    app.commands.execute('notebook:replace-selection', { 'text':  f'{code}', 'type': 'code'})
    time.sleep(0.05)
    app.commands.execute('notebook:run-all-below')

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
  font-family: monospace;
  //overflow: hidden; /* Ensures the content is not revealed until the animation */
  //white-space: nowrap; /* Keeps the content on a single line */
  margin: 0 auto; /* Gives that scrolling effect as the typing happens */
  letter-spacing: .15em; /* Adjust as needed */
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

word_styling = """<span id="last-word"></span>"""
#div1 is to be wrapped with div2
def wrap(doc, target_el, target_id, input_text):
    soup = BeautifulSoup(doc, features="html.parser")
    target = soup.find(target_el, attrs={'id': target_id })
    target.clear()
    target.append(input_text)
    return soup
# Create animated text output

def typewrite(text, interval):
    test_string = ""
    display.display(HTML(test_string), display_id='output')
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
        wrap_all = wrap(wrapper_html, "div", "container", output)
        if to_wrap != " ":
            add_cursor = wrap(word_styling, "span", "last-word", to_wrap)
            wrap_all.find('div', attrs={'id': 'container'}).append(add_cursor)
        # print('wrap_all: ', str(wrap_all))
        display.update_display(HTML(str(wrap_all)), display_id='output')
        time.sleep(interval)
        i+=1
