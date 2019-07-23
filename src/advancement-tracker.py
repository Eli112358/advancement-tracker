import json
import os
import time
from tkinter import *

enabled = False
btn_values = ['Start', 'Stop']

paths = {'root': os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}

load_data = lambda key: json.load(open(paths[key], 'r'))
def set_path(key, *parts):
    paths[key] = os.path.join(*parts)

set_path('out', paths['root'], 'out')
if not os.path.exists(paths['out']):
    os.mkdir(paths['out'])
set_path('needed', paths['out'], 'needed.json')
set_path('vanilla', paths['root'], 'data', 'vanilla.json')
set_path('game_dir', os.getenv('APPDATA'), '.minecraft')
set_path('profiles', paths['game_dir'], 'launcher_profiles.json')
data = {
    'profiles': load_data('profiles')['profiles'],
    'vanilla': load_data('vanilla')
}
loaded = {'profiles': {v['name'] if v['name'] else k: v['gameDir'] for k, v in data['profiles'].items()}}
names = {'profile': sorted(loaded['profiles'].keys(), key=str.lower), 'save': [''], 'player': ['']}

window = Tk()
window.title('Advancement Tracker')
label = {}
menu = {}
win_var = {}
for i, (k, v) in enumerate(names.items()):
    label[k] = Label(window, text=k.capitalize() + ':')
    win_var[k] = StringVar(window)
    menu[k] = OptionMenu(window, win_var[k], *v)
    label[k].grid(column=0, row=i)
    menu[k].grid(column=1, row=i)
win_var['sep_files'] = IntVar()
check = Checkbutton(window, text='Separate files', variable=win_var['sep_files'])
check.grid(column=0, row=3)
toggle_btn = Button(window, text='Start')
toggle_btn.grid(column=0, row=4)

def update_list(name, _filter=lambda f: f, *parts):
    plural = name + 's'
    set_path(plural, *parts)
    names[name] = [_filter(f) for f in os.listdir(paths[plural])]
    menu[name]['menu'].delete(0, 'end')
    for n in names[name]:
        menu[name]['menu'].add_command(label=n, command=lambda v=n: win_var[name].set(v))
    loaded[plural] = {'loaded': True}

updates = dict(
    profile=lambda *args: update_list('save', lambda f: f, loaded['profiles'][win_var['profile'].get()], 'saves'),
    save=lambda *args: update_list('player', lambda f: f[:-5], paths['saves'], win_var['save'].get(), 'advancements'),
    player=lambda *args: set_path('player', paths['players'], win_var['player'].get() + '.json')
)

def toggle():
    btn_state = 1 - btn_values.index(toggle_btn['text'])
    toggle_btn['text'] = btn_values[btn_state]
    updates['player']()

for _name, _function in updates.items():
    win_var[_name].trace('w', _function)
toggle_btn['command'] = toggle

def strip_namespace(values) -> object:
    result = [v.split(':')[1] if ':' in v else v for v in values]
    return result

needed = {}

while True:
    try:
        window.update()
        time.sleep(0.1)
        if btn_values.index(toggle_btn['text']):
            data['player'] = load_data('player')
            del data['player']['DataVersion']
            have = {
                path.split(':')[1]: strip_namespace(value['criteria'].keys())
                for path, value in data['player'].items()
                if path.split(':')[1] in data['vanilla'].keys()
            }
            needed = {
                path: strip_namespace([_id for _id in ids if _id not in have[path]] if path in have else ids[0:])
                for path, ids in data['vanilla'].items()
            }
            empty = [k for k, v in needed.items() if not len(v)]
            for e in empty:
                del needed[e]
            if win_var['sep_files'].get():
                for path, ids in needed.items():
                    if len(ids):
                        set_path(path, paths['out'], path.split('/')[1] + '.txt')
                        file = open(paths[path], 'w')
                        for _id in ids:
                            file.write(' '.join([w.capitalize() for w in _id.replace('_', ' ').split(' ')]) + '\n')
                        file.close()
            else:
                json.dump(needed, open(paths['needed'], 'w'), sort_keys=True, indent='\t')
    except TclError as err:
        break
