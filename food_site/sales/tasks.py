from background_task import background, Task
from Mo

@background(repeat=Task.Daily, repeat_until=None)
def scrape():
