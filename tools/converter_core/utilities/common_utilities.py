# ------------------------------------------------------------------------------------------------------------------------------------
#
#
#   This is a Centralized Utility for functions and constants that are used across scripts and utilities.
#
#
# ------------------------------------------------------------------------------------------------------------------------------------



##############################################################################
#                                                                            #
#                      Enable Absolute Imports Function                      #
#                                                                            #
##############################################################################



#######################  Absolute Imports > Relative Imports  #######################



def enable_absolute_imports():
    import sys
    from os import getcwd
    PWD = getcwd()
    if PWD not in sys.path:
        sys.path.append(PWD)



enable_absolute_imports()



##############################################################################
#                                                                            #
#                       Spacer And New Line Constants                        #
#                                                                            #
##############################################################################



#######################  Variables Are Better Than Blank Spaces  #######################



four_spaces = '    '
eight_spaces = '        '
twelve_spaces = '            '
new_line_string = '\n'



##############################################################################
#                                                                            #
#                          Carriage Return Function                          #
#                                                                            #
##############################################################################



#######################  Carriage Return ('New Line String') Function  #######################



def PRINT_NEWLINES(number: int):
    for _ in range(number):
        print('\n')



##############################################################################
#                                                                            #
#                Get Present Working Directory (PWD) Function                #
#                                                                            #
##############################################################################



from os import getcwd



#######################  HERE - Literally (Actually)  #######################



PWD = getcwd()



##############################################################################
#                                                                            #
#          Get Absolute Path for Present Working Directory Function          #
#                                                                            #
##############################################################################



from os import path



#######################  HERE - (Absolutely) Here  #######################



def get_pwd_absolute_path(PWD):
    absolute_path = path.abspath(PWD)
    return absolute_path



##############################################################################
#                                                                            #
#                 Add Hyphens Every Two Characters Function                  #
#                                                                            #
##############################################################################



import re



#######################  abcdefgh --> In | ab-cd-ef-gh --> Out  #######################



def add_hyphens_every_two_characters(input_text):
    # https://stackoverflow.com/a/9477447
    list_of_characters_in_pairs = re.findall('.{2}', input_text)
    hyphens_added = '-'.join(list_of_characters_in_pairs)
    return hyphens_added



##############################################################################
#                                                                            #
#                      Open and Load JSON File Function                      #
#                                                                            #
##############################################################################



#######################  Open JSON File  #######################



def open_json_file(filename):
    import json
    with open(filename, mode = 'r') as f:
        file_data = json.load(f)
    return file_data



##############################################################################
#                                                                            #
#                      Open and Load SHN File Function                       #
#                                                                            #
##############################################################################



'''
Hard-enforce opening files as UTF-8 regardless of the encoding method
declared in the XML text or the encoding method in the Byte Order Mark (BOM).
'''



from utilities.catch_exceptions_utilities import escape_ampersand
from utilities.catch_exceptions_utilities import remove_xml_junk_data



#######################  Open SHN (XML) File as Text  #######################



def open_shn_file(filename):
    with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
        raw_data = f.read()
        escaped_data = escape_ampersand(raw_data)
        file_data = remove_xml_junk_data(escaped_data)
        print(file_data)
    return file_data



##############################################################################
#                                                                            #
#                      Open and Load MC4 File Function                       #
#                                                                            #
##############################################################################



#######################  Open MC4 File as Byes  #######################



def open_mc4_file(filename):
    with open(filename, 'rb') as f:
        file_data = f.read()
    return file_data



##############################################################################
#                                                                            #
#                       Input File Dialog Box Function                       #
#                                                                            #
##############################################################################



###################  Dialog Box - Select File  ###################



def open_file_dialog_box():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_types = [('JSON Files', '*.json'),('SHN Files', '*.shn'),('MC4 Files', '*.mc4')]
    user_selected_file = filedialog.askopenfilename(filetypes=file_types)
    root.destroy()
    PRINT_NEWLINES(2)
    return user_selected_file



##############################################################################
#                                                                            #
#                    Open and Read File Workflow Function                    #
#                                                                            #
##############################################################################



#######################  Putting It All Together  #######################



def open_and_read_file_workflow():
    from os.path import splitext
    user_selected_file = open_file_dialog_box()
    file_and_path, file_extension = splitext(user_selected_file)
    title_id_and_version = file_and_path.split('/')[-1].strip()
    file_type = file_extension[1:].lower()
        #
    if file_type == 'json':
        file_data = open_json_file(user_selected_file)
    elif file_type == 'shn':
        file_data = open_shn_file(user_selected_file)
    elif file_type == 'mc4':
        file_data = open_mc4_file(user_selected_file)
    return file_type, file_data, title_id_and_version

