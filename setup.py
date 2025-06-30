import time
import random
from rich.progress import Progress
from rich.jupyter import print
from rich.live import Live
import ipywidgets as widgets
from IPython.display import display

#button = widgets.Button(description="Load Pathogen")
#output = widgets.Output()
 
# empty arg for button input

# can't get `loading_screen` to live-update while printing after button click. It works fine on its own, which is probablhy good enough for my purposes, but I'd like to figure out how it's being piped to `output` and why that can't handle live updates (add `with output: ` to the function to get it to display from button press)
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
            while task < 100 or shard < 100 or matrix < 100:
              time.sleep(0.1)
              rand = random.random()
              if rand < 0.3:
                  task += 1
                  progress.update(task_load, advance=1)
              elif rand < 0.6:
                  shard +=1
                  progress.update(shard_load, advance=1)
              else:   
                  matrix += 1
                  progress.update(matrix_load, advance=1)
            if task >= 100 and shard >= 100 and matrix >= 100 and pathogen == 0:
                pathogen_load = progress.add_task("[magenta]Loading pathogen...", total=100)
                fully_loaded = True
            while pathogen < 100 and fully_loaded==True:
                time.sleep(0.1)
                pathogen += 1
                progress.update(pathogen_load, advance=1)

#def run():
#    button.on_click(loading_screen)
#
#    display(button, output)