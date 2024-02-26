'''
Copyright 2023-2024 PySimpleSoft, Inc. and/or its licensors. All rights reserved.

Redistribution, modification, or any other use of PySimpleGUI or any portion thereof is subject
to the terms of the PySimpleGUI License Agreement available at https://eula.pysimplegui.com.

You may not redistribute, modify or otherwise use PySimpleGUI or its contents except pursuant
to the PySimpleGUI License Agreement.
'''
    
import PySimpleGUI as sg
from threading import Thread
import sys, os,  shutil
import PyInstaller
import webbrowser

version = '5.0.0'
__version__ = version.split()[0]

PYINSTALLER_HELP_URL = r'https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html'

'''
    Make a "Windows os" executable with PyInstaller
'''

'''
M""""""""M dP                                        dP 
Mmmm  mmmM 88                                        88 
MMMM  MMMM 88d888b. 88d888b. .d8888b. .d8888b. .d888b88 
MMMM  MMMM 88'  `88 88'  `88 88ooood8 88'  `88 88'  `88 
MMMM  MMMM 88    88 88       88.  ... 88.  .88 88.  .88 
MMMM  MMMM dP    dP dP       `88888P' `88888P8 `88888P8 
MMMMMMMMMM
'''


def run_finish(p, window, script, name=None):
    """
    Run PyInstaller
    :param command: Command for PyInstaller
    :type command: (str)
    :param script: Script file including path for use in cleanup
    :type script: (str)
    :param window: Main PySimpleGUI Window
    :type window: (Window)
    :param name: Name of file (if --name variable is used) for use in cleanup
    :type name: (str)
    """
    try:
        for line in p.stdout:
            oline = line.decode().rstrip()
            window.write_event_value('-THREAD CPRINT-', oline)
        p.wait()
        window.write_event_value('-THREAD CPRINT-', "[EXE Maker] Cleaning up...")

        source_path, source_filename = os.path.split(script)

        if name:
            folder_to_remove = os.path.join(source_path, name)
            file_to_remove = os.path.join(source_path, name + '.spec')
        else:
            filename_no_ext, filename_ext = os.path.splitext(source_filename)
            folder_to_remove = os.path.join(source_path, filename_no_ext)
            file_to_remove = os.path.join(source_path, filename_no_ext + '.spec')

        shutil.rmtree(folder_to_remove)
        os.remove(file_to_remove)
        window.write_event_value('-THREAD FINISHED-', '[EXE Maker] ****************** Finished ******************')
    except Exception as e:
        print(f'EXCEPTION in thread {e}')
        window.write_event_value('-THREAD FAILED-', e)

'''
M""M                     dP            dP dP                   
M  M                     88            88 88                   
M  M 88d888b. .d8888b. d8888P .d8888b. 88 88 .d8888b. 88d888b. 
M  M 88'  `88 Y8ooooo.   88   88'  `88 88 88 88ooood8 88'  `88 
M  M 88    88       88   88   88.  .88 88 88 88.  ... 88       
M  M dP    dP `88888P'   dP   `88888P8 dP dP `88888P' dP       
MMMM
'''


def pip_install_thread(window, sp):
    window.write_event_value('-THREAD-', (sp, 'Install thread started'))
    for line in sp.stdout:
        oline = line.decode().rstrip()
        window.write_event_value('-THREAD-', (sp, oline))



def pip_install_latest():

    pip_command = '-m pip install --upgrade --no-cache-dir PySimpleGUI>=5'

    python_command = sys.executable  # always use the currently running interpreter to perform the pip!
    if 'pythonw' in python_command:
        python_command = python_command.replace('pythonw', 'python')

    layout = [[sg.Text('Installing PySimpleGUI', font='_ 14')],
              [sg.Multiline(s=(90, 15), k='-MLINE-', reroute_cprint=True, reroute_stdout=True, echo_stdout_stderr=True, write_only=True, expand_x=True, expand_y=True)],
              [sg.Push(), sg.Button('Downloading...', k='-EXIT-'), sg.Sizegrip()]]

    window = sg.Window('Pip Install PySimpleGUI Utilities', layout, finalize=True, keep_on_top=True, modal=True, disable_close=True, resizable=True)

    window.disable_debugger()

    sg.cprint('Installing with the Python interpreter =', python_command, c='white on purple')

    sp = sg.execute_command_subprocess(python_command, pip_command, pipe_output=True, wait=False)

    window.start_thread(lambda: pip_install_thread(window, sp), end_key='-THREAD DONE-')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or (event == '-EXIT-' and window['-EXIT-'].ButtonText == 'Done'):
            break
        elif event == '-THREAD DONE-':
            sg.cprint('\n')
            show_package_version('PySimpleGUI')
            sg.cprint('Done Installing PySimpleGUI.  Click Done and the program will restart.', c='white on red', font='default 12 italic')
            window['-EXIT-'].update(text='Done', button_color='white on red')
        elif event == '-THREAD-':
            sg.cprint(values['-THREAD-'][1])

    window.close()

def suggest_upgrade_gui():
    layout = [[sg.Image(sg.EMOJI_BASE64_HAPPY_GASP), sg.Text(f'PySimpleGUI 5+ Required', font='_ 15 bold')],
              [sg.Text(f'PySimpleGUI 5+ required for this program to function correctly.')],
              [sg.Text(f'You are running PySimpleGUI {sg.version}')],
              [sg.Text('Would you like to upgrade to the latest version of PySimpleGUI now?')],
              [sg.Push(), sg.Button('Upgrade', size=8, k='-UPGRADE-'), sg.Button('Cancel', size=8)]]

    window = sg.Window(title=f'Newer version of PySimpleGUI required', layout=layout, font='_ 12')

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            window.close()
            break
        elif event == '-UPGRADE-':
            window.close()
            pip_install_latest()
            sg.execute_command_subprocess(sys.executable, __file__, pipe_output=True, wait=False)
            break


def make_str_pre_38(package):
    return f"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import pkg_resources
try:
    ver=pkg_resources.get_distribution("{package}").version.rstrip()
except:
    ver=' '
print(ver, end='')
"""

def make_str(package):
    return f"""
import importlib.metadata

try:
    ver = importlib.metadata.version("{package}")
except importlib.metadata.PackageNotFoundError:
    ver = ' '
print(ver, end='')
"""


def show_package_version(package):
    """
    Function that shows all versions of a package
    """
    interpreter = sg.execute_py_get_interpreter()
    sg.cprint(f'{package} upgraded to ', end='', c='red')
    # print(f'{interpreter}')
    if sys.version_info.major == 3 and sys.version_info.minor in (6, 7):  # if running Python version 3.6 or 3.7
        pstr = make_str_pre_38(package)
    else:
        pstr = make_str(package)
    temp_file = os.path.join(os.path.dirname(__file__), 'temp_py.py')
    with open(temp_file, 'w') as file:
        file.write(pstr)
    sg.execute_py_file(temp_file, interpreter_command=interpreter, pipe_output=True, wait=True)
    os.remove(temp_file)



def upgrade_check():
    if not sg.version.startswith('5'):
        suggest_upgrade_gui()
        exit()



'''
M"""""`'"""`YM          oo          
M  mm.  mm.  M                      
M  MMM  MMM  M .d8888b. dP 88d888b. 
M  MMM  MMM  M 88'  `88 88 88'  `88 
M  MMM  MMM  M 88.  .88 88 88    88 
M  MMM  MMM  M `88888P8 dP dP    dP 
MMMMMMMMMMMMMM
'''


def main():
    """
    Main function for Demo_EXE_Maker
    """

    sg.user_settings_filename(filename='psgcompiler.json')
    upgrade_check()

    ver = version # make a local copy for debugging

    icon = b'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'

    sg.set_options(icon=icon)    # first make sure version of PySimpleGUI is high enough

    variable_list = ['--name', '--upx-dir', '--log-level', '--version-file', '--manifest', '--osx-bundle-identifier',
                     '--runtime-tmpdir', '--target-architecture', '--codesign-identity', '--osx-entitlements-file',
                     '--splash']
    bool_list = ['--ascii', '--clean', '--strip', '--noupx', '--uac-admin', '--uac-uiaccess',
                 '--win-private-assemblies',
                 '--win-no-prefer-redirects', '--bootloader-ignore-signals', '--disable-windowed-traceback']
    addition_list = ['--paths', '--additional-hooks-dir', '--runtime-hook']

    multi_variable_list = ['--exclude-module', '--upx-exclude', '--collect-submodules', '--collect-data',
                           '--collect-binaries',
                           '--collect-all', '--copy-metadata', '--recursive-copy-metadata']
    bool_touched = []
    variable_touched = {}
    addition_touched = {}
    multi_variable_touched = {}

    sg.theme('DarkPurple4')
    main_tab = [[sg.HorizontalSeparator()],
                [sg.Text('PSG Compiler - Convert Your Python Program to Binary', font='Any 15'), sg.Push(),
                 sg.Image(sg.EMOJI_BASE64_DREAMING, key='--STATUS_IMAGE--')],
                # [sg.Text('Requires PySimpleGUI >= 4.54.0', font='_ 9',)],
                [sg.Text('Python Script: ', s=20), sg.Input(key='-SOURCEFILE-', expand_x=True, enable_events=True),
                 sg.FileBrowse(target='-SOURCEFILE-', file_types=(("Python Files", "*.py *.pyw *.PY *.PYW"),))],
                [sg.Text('Icon: ', s=20), sg.Input(key='-ICONFILE-', expand_x=True, enable_events=True),
                 sg.FileBrowse(target='-ICONFILE-', file_types=(("Icon Files", "*.ico"),))],
                [sg.Text('Optional specific pyinstaller: ', s=20), sg.Input(key='-PYINSTALLER-', expand_x=True),
                 sg.FileBrowse(target='-PYINSTALLER-', file_types=(("All Files", "*.*"),))],
                [sg.Text('Arguments: ', s=10), sg.Button('--onefile', key='-ONEFILE BUTTON-', enable_events=True, expand_x=True), sg.Button('--windowed', key='-WINDOWED BUTTON-', enable_events=True, expand_x=True)],
                [sg.HorizontalSeparator()],
                [sg.Frame('Command', font='Any 13', expand_x=True, layout=[
                    [sg.Multiline('--onefile --windowed', key='-COMMAND-', s=(None, 7), expand_x=True)]])],
                [sg.HorizontalSeparator()],
                [sg.Frame('Output', font='Any 13', expand_x=True, expand_y=True, layout=[
                    [sg.Multiline(font='Courier 10', key='-OUTPUT-', size=(85,10), expand_x=True, expand_y=True, reroute_cprint=True, write_only=True, autoscroll=True)]])],
                [sg.HorizontalSeparator()],
                [sg.Push(), sg.T('Click Me for PyInstaller Help', enable_events=True, key='-PYINSTALLER HELP-', tooltip='If you have problems with PyInstaller, click and\nyou will be taken to the help page'), sg.Push()],
                [sg.Button("CONVERT", expand_x=True)],
                ]

    # :O
    arguments_tab = []
    size = max([len(v) for v in variable_list])
    for variable in variable_list:
        arguments_tab.append([sg.T(variable.replace('--', ''), s=size), sg.Input(k=variable, enable_events=True, expand_x=True)])

    bool_tab = []
    size = max([len(v) for v in bool_list])
    for variable in bool_list:
        bool_tab.append(
            [sg.Checkbox(variable.replace('--', ''), k=variable, enable_events=True, )])


    # Start addition of listbox
    additions_tab = []
    size = max([len(v) for v in addition_list])
    for variable in addition_list:
        additions_tab.append([sg.T(variable.replace('--', ''), font='_ 15')])
        additions_tab.append([sg.Listbox(values=list(), select_mode=sg.SELECT_MODE_EXTENDED, k=f"COMBO_{variable}", size=(None, 5), expand_x=True, expand_y=True),
             sg.Input(k=f"KEY_{variable}", visible=False, enable_events=True), sg.Button("(-)", k=f"REM_{variable}"),
             sg.FolderBrowse("(+)", target=f"KEY_{variable}")])

    multi_var_tab = []
    size = max([len(v) for v in multi_variable_list])
    for variable in multi_variable_list:
        multi_var_tab.append(
            [sg.T(variable.replace('--', ''), s=size), sg.Listbox(values=list(), select_mode=sg.SELECT_MODE_EXTENDED, k=f"COMBO_{variable}", expand_x=True, expand_y=True),
             sg.Button('(-)', k=f"REM_{variable}"), sg.Button('(+)', k=f"ADD_{variable}")])

    layout = [[sg.TabGroup([[sg.Tab('Home', main_tab), sg.Tab('Arguments', arguments_tab, expand_x=True, ), sg.Tab('Booleans', bool_tab),
                             sg.Tab('Additions', additions_tab), sg.Tab('Other', multi_var_tab)]], expand_x=True, expand_y=True)]]

    right_click_menu = ['', ['Edit Me', 'Version', 'File Location', f'Version {version}', f'PyInstaller {PyInstaller.__version__}', 'Exit']]

    window = sg.Window('PSG Compiler', layout, right_click_menu=right_click_menu, finalize=True, resizable=True, auto_save_location=True)
    [window[variable].block_focus() for variable in bool_list]
    window['-PYINSTALLER HELP-'].set_cursor('hand1')
    counter = 0
    while True:
        event, values = window.read(timeout=500)
        counter += 1
        if event in ('Exit', 'Quit', None):
            break
        elif event == 'File Location':
            sg.popup_scrolled('This Python file is:', __file__)
        elif event == 'Edit Me':
            sg.execute_editor(__file__)
        elif event == 'Version':
            sg.popup_scrolled(f'psgcompiler version {ver}', sg.get_versions(), f'PyInstaller version for this Python version: {PyInstaller.__version__}')
        elif event == '-THREAD CPRINT-':
            sg.cprint(values[event])
        elif event == '-THREAD FINISHED-':
            window['CONVERT'].update(disabled=False)
            window['--STATUS_IMAGE--'].update(sg.EMOJI_BASE64_HAPPY_JOY)
            sg.cprint("[EXE Maker] *********************** Finished ***********************", colors='white on red')
            window.ding()
        elif event == '-THREAD FAILED-':
            window['CONVERT'].update(disabled=False)
            window['--STATUS_IMAGE--'].update(sg.EMOJI_BASE64_FRUSTRATED)
            sg.cprint("[EXE Maker] *********************** FAILED ***********************", colors='white on red')
            sg.cprint(values[event], colors='white on red')
            window.ding()
        elif event in '-ONEFILE BUTTON-':
            if window['-ONEFILE BUTTON-'].get_text() == '--onefile':
                window['-ONEFILE BUTTON-'].update('--onedir')
            else:
                window['-ONEFILE BUTTON-'].update('--onefile')
        elif event == '-WINDOWED BUTTON-':
            if window['-WINDOWED BUTTON-'].get_text() == '--windowed':
                window['-WINDOWED BUTTON-'].update('--console')
            else:
                window['-WINDOWED BUTTON-'].update('--windowed')
        elif event in variable_list:
            if values[event]:
                variable_touched[event] = values[event]
            else:
                try:
                    variable_touched.pop(event)
                except KeyError:
                    pass
        elif event in bool_list:
            if values[event]:
                bool_touched.append(event)
            else:
                bool_touched.remove(event)
        # HOLY CRAP YOU CAN DO THIS??
        elif event in [f"{pre}_{varz}" for pre in ['ADD', 'REM', 'KEY'] for varz in
                       (addition_list + multi_variable_list)]:
            using_variable = event[4:]
            if event.startswith('ADD'):
                if using_variable in multi_variable_touched.keys():
                    multi_variable_touched[using_variable] += [sg.popup_get_text(f"Value for {using_variable.replace('--', '')}")]
                else:
                    multi_variable_touched[using_variable] = [sg.popup_get_text(f"Value for {using_variable.replace('--', '')}")]
                window[f"COMBO_{using_variable}"].update(values=multi_variable_touched[using_variable])
            elif event.startswith('REM'):
                # Here it can work with additions OR multi_variable so let's check both.
                try:
                    if using_variable in multi_variable_list:
                        if using_variable in multi_variable_touched.keys():
                            for x in values[f"COMBO_{using_variable}"]:
                                multi_variable_touched[using_variable].remove(x)
                        if not multi_variable_touched[using_variable]:
                            multi_variable_touched.pop(using_variable)
                            window[f"COMBO_{using_variable}"].update(values=list())
                        else:
                            window[f"COMBO_{using_variable}"].update(values=multi_variable_touched[using_variable])
                    else:
                        if using_variable in addition_touched.keys():
                            for x in values[f"COMBO_{using_variable}"]:
                                addition_touched[using_variable].remove(x)
                        if not addition_touched[using_variable]:
                            addition_touched.pop(using_variable)
                            window[f"COMBO_{using_variable}"].update(values=list())
                        else:
                            window[f"COMBO_{using_variable}"].update(values=addition_touched[using_variable])
                except Exception as ex:
                    sg.cprint(ex)
                    pass
            elif event.startswith('KEY'):
                if (using_variable not in addition_touched.keys()) or (using_variable in addition_touched.keys() and values[f"KEY_{using_variable}"] not in addition_touched[using_variable]):
                    if using_variable in addition_touched.keys():
                        addition_touched[using_variable] += [values[f"KEY_{using_variable}"]]
                    else:
                        addition_touched[using_variable] = [values[f"KEY_{using_variable}"]]
                    window[f"COMBO_{using_variable}"].update(values=addition_touched[using_variable])
                else:
                    sg.PopupError('Oh-No!', 'The directory or file you have attempted to has been marked as a duplicate, and therefore has not been added.')
        elif event == 'CONVERT':
            window['CONVERT'].update(disabled=True)
            command_raw = f"pyinstaller {values['-COMMAND-']}"
            sg.cprint("[EXE Maker] Starting process...")
            try:
                name = None
                if '--name' in variable_touched.keys():
                    name = variable_touched['--name']
                window['--STATUS_IMAGE--'].update(sg.EMOJI_BASE64_YIKES)
                command = values['-PYINSTALLER-'] if  values['-PYINSTALLER-'] else 'pyinstaller'
                p = sg.execute_command_subprocess(command, values['-COMMAND-'], pipe_output=True)
                thread = Thread(target=run_finish, args=(p, window, values['-SOURCEFILE-'], name)).start()
            except:
                window['CONVERT'].update(disabled=False)
                sg.PopupError('Something went wrong',
                              'close this window and copy command line from text printed out in main_tab window',
                              'Additional info is also listen in the output log.')
                sg.cprint('Raw Command For PyInstaller:\n\n', command_raw)
        elif event == '-PYINSTALLER HELP-':
            webbrowser.open_new_tab(PYINSTALLER_HELP_URL)
        # Thank you!
        command = f"{window['-ONEFILE BUTTON-'].get_text()} {window['-WINDOWED BUTTON-'].get_text()} "
        for key in variable_list:
            if values[key]:
                command += f"{key} {values[key]} "
        for key in multi_variable_touched.keys():
            for i in multi_variable_touched[key]:
                command += f'{key} "{i}" '
        for key in addition_touched.keys():
            for i in addition_touched[key]:
                command += f'{key} "{i}" '
        for key in bool_touched:
            command += f"{key} "
        if values['-ICONFILE-']:
            icon = values['-ICONFILE-']
            command += f'-i "{icon}" '
        if values['-SOURCEFILE-']:
            script = values['-SOURCEFILE-']
            source_path, source_filename = os.path.split(script)
            command += f'--workpath "{source_path}" --distpath "{source_path}" --specpath "{source_path}" "{script}"'
        window['-COMMAND-'].update(command)
    window.close()
    sys.exit(0)


if __name__ == '__main__':

    main()
