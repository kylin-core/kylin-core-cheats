# ------------------------------------------------------------------------------------------------------------------------------------
#
#
#   This Utility contains functions used to work with JSON Objects and JSON-Based Cheats.
#
#
#   While this is the JSON Utility, many of the functions and doc-strings below reference SHN (XML).
#   The functions in this Utility take XML as an input and ultimately output JSON.
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



#######################################################################################################################################################
#                                                                                                                                                     #
#                                                  Functions Related to Converting SHN (XML) to JSON                                                  #
#                                                                                                                                                     #
#######################################################################################################################################################



'''
SHN Cheat Files are XML Files.
XML Objects can easily be converter to JSON Objects in Python.

This code uses the terms `XML` and `SHN` depending on the context (such as `convert_xml` in the function name below).
When you see XML, think SHN.
When you see SHN, think XML.

They are ostensibly equal.
'''



##############################################################################
#                                                                            #
#                 Convert XML String to JSON Object Function                 #
#                                                                            #
##############################################################################



import xmltodict



#######################  XML String --> In | JSON Dictionary --> Out  #######################



def convert_xml_to_json_object(xml_file_data):
    json_object = xmltodict.parse(xml_file_data)
    return json_object



############################################################################
#                                                                          #
#                  Create Empty Cheat Dictionary Function                  #
#                                                                          #
############################################################################



#######################  Master Cheat Dictionary Creation  #######################



def create_empty_master_cheat_dictionary():
    cheat_dictionary = {
      'name': None,
      'id': None,
      'version': None,
      'process': None,
      'mods': None,
      'credits': None,
    }
    return cheat_dictionary



############################################################################
#                                                                          #
#                    Create Empty Cheat Object Function                    #
#                                                                          #
############################################################################



#######################  Individual Cheat Object Creation  #######################



def create_empty_cheat_object():
    cheat_object = {
      'name': None,
      'type': 'checkbox',
      'memory': []
    }
    return cheat_object



##############################################################################
#                                                                            #
#                    Create Empty Memory Object Function                     #
#                                                                            #
##############################################################################



#######################  Individual Memory Object Creation  #######################



def create_empty_memory_object():
    memory_object = {
          'offset': None,
          'on': None,
          'off': None
        }
    return memory_object



##############################################################################
#                                                                            #
#                 Populate Individual Cheat Object Function                  #
#                                                                            #
##############################################################################



'''
JSON Cheat Files are dictionaries.
Each Individual Cheat in a Cheat File is itself a dictionary.


This code uses the terminology `Master Cheat Dictionary` to refer to the item
that is ultimately turned into the JSON Cheat File.


The term `Cheat Object` refers to an Individual Cheat within the JSON Cheat File.
'''



#######################  Slice Individual Cheat | Populate Cheat Object  #######################



def populate_cheat_object(individual_cheat):
    cheat_object = create_empty_cheat_object()
    cheat_name = individual_cheat['@Text']
    cheat_object['name'] = cheat_name
        #
    cheat_lines = get_cheat_lines_from_individual_cheat(individual_cheat)
    for cheat in cheat_lines:
        memory_object = create_empty_memory_object()
        cheat_offset = cheat['Offset']
        value_when_on = cheat['ValueOn']
        value_when_off = cheat['ValueOff']
            #
        normalized_on_value  = value_when_on.replace('-', '').upper()
        normalized_off_value = value_when_off.replace('-', '').upper()
            #
        memory_object['offset'] = cheat_offset
        memory_object['on'] = normalized_on_value
        memory_object['off'] = normalized_off_value
        cheat_object['memory'].append(memory_object)
    return cheat_object



############################################################################
#                                                                          #
#                Populate Master Cheat Dictionary Function                 #
#                                                                          #
############################################################################



#######################  Slice Converted Dictionary | Populate Master Dictionary  #######################



def populate_master_cheat_dictionary(json_object, modification_list):
    master_cheat_dictionary = create_empty_master_cheat_dictionary()
        #
    game_name = json_object['Trainer']['@Game']
    game_id = json_object['Trainer']['@Cusa']
    game_version = json_object['Trainer']['@Version']
    game_process = json_object['Trainer']['@Process']
    cheat_credits = json_object['Trainer']['@Moder']
        #
    master_cheat_dictionary['name'] = game_name
    master_cheat_dictionary['id'] = game_id
    master_cheat_dictionary['version'] = game_version
    master_cheat_dictionary['process'] = game_process
    master_cheat_dictionary['mods'] = modification_list
    master_cheat_dictionary['credits'] = [cheat_credits]
    return master_cheat_dictionary



############################################################################
#                                                                          #
#                      XML to JSON Workflow Function                       #
#                                                                          #
############################################################################



'''
In the XML (SHN) format, each Individual Cheat is delineated
by an XML Object of the format `<Cheat Text="Cheat Name">.

When the XML is converted to JSON, a key: value pair is created where the key is `Cheat`
and the value is dependent on how many Individual Cheats are contained with the Original File.

If the Original File contained only a single Cheat,
the result value of the Key `Cheat` is a Python Dictionary.

If the Original File contained multiple Cheats,
the result value of the Key `Cheat` is a Python List.

This function ensures that the the resulting object is always read in as list.

    # Cheat File With Multiple Cheats Example
    # Cheat List Truncated For Brevity

        json_object = {
            'Trainer': {
                '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@Game': 'Assassins Creed? Syndicate',
                '@Moder': 'Saso',
                '@Cusa': 'CUSA02378',
                '@Version': '01.52',
                '@Process': 'eboot.bin',
                'Genres': {'@Name': 'Adventure'},
                'Items': None,
                'Cheat': [                  <---- Python List
                    {
                        '@Text': 'Infinite Bombs',
                        'Cheatline': {
                            'Absolute': 'True',
                            'Section': '0',
                            'Offset': '1EB59BB',
                            'ValueOn': '41-89-54-24-28',
                            'ValueOff': '41-89-44-24-28'
                        }
                    },
                    {
                        '@Text': 'Max Money',
                        'Cheatline': [
                            {
                                'Absolute': 'True',
                                'Section': '0',
                                'Offset': '594387B',
                                'ValueOn': '41-C7-44-24-28-3F-42-0F-00-E9-37-21-57-FC',
                                'ValueOff': '00-00-00-00-00-00-00-00-00-00-00-00-00-00'
                            },
                            {
                                'Absolute': 'True',
                                'Section': '0',
                                'Offset': '1EB59BB',
                                'ValueOn': 'E9-BB-DE-A8-03',
                                'ValueOff': '41-89-44-24-28'
                            }
                        ]
                    },
                ]
            }
        }


    # Cheat File With Single Cheat Example

        json_object = {
            'Trainer': {
                '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@Game': 'Nier Automata',
                '@Moder': 'Skal',
                '@Cusa': 'CUSA04480',
                '@Version': '01.06',
                '@Process': 'eboot.bin',
                'Genres': [
                    {'@Name': 'Action'},
                    {'@Name': 'Adventure'}
                ],
                'Items': None,
                'Cheat': {                  <---- Python Dictionary
                    '@Text': 'One Hit Kill',
                    'Cheatline': {
                        'Offset': '3D471B',
                        'Section': '0',
                        'ValueOn': '4D-29-A6-50-08-00-00',
                        'ValueOff': '41-29-9E-50-08-00-00'
                    }
                }
            }
        }
'''



#######################  JSON Converted XML --> In | [Cheats] --> Out  #######################



def get_all_cheats_list_from_json_data(json_object):
    cheats_from_json = json_object['Trainer']['Cheat']
    if isinstance(cheats_from_json, dict):
        all_cheats = [cheats_from_json]
    elif isinstance(cheats_from_json, list):
        all_cheats = cheats_from_json
    return all_cheats



##############################################################################
#                                                                            #
#               Get Cheat Lines From Individual Cheat Function               #
#                                                                            #
##############################################################################



'''
In the XML (SHN) format, each Individual Cheat is delineated
by an XML Object of the format `<Cheat Text="Cheat Name">.

Within each Individual Cheat, there are a set of items that include the offset,
on value, and off value. Each one of these sets is delineated by an
XML Object starting with `<Cheatline>` and ending with `</Cheatline>`.

When the XML is converted to JSON, each Individual Cheat contains a key named `CheatLine`.
If an Individual Cheat only has one set of items (offset, on value, off value),
the value of the `CheatLine` key is a dictionary.

If an Individual Cheat only has more than one set of items (offset, on value, off value),
the value of the `CheatLine` key is a list.

The following function ensures that the the resulting value is always read in as list.


    # Multiple Sets Example

        individual_cheat = {
            '@Text': 'Infinite Health',
            'Cheatline': [                  <---- Python List
                {
                    'Absolute': 'True',
                    'Section': '0',
                    'Offset': '5943800',
                    'ValueOn': '48-39-C1-75-03-8B-77-04-89-37-C3-90',
                    'ValueOff': '00-00-00-00-00-00-00-00-00-00-00-00'
                },
                {
                    'Absolute': 'True',
                    'Section': '0',
                    'Offset': '18D1890',
                    'ValueOn': 'E9-6B-1F-07-04-90-90-90-90-90-90-90-90-90-90-90',
                    'ValueOff': '89-37-C3-66-66-66-66-2E-0F-1F-84-00-00-00-00-00'
                }
            ]
        }


    # Single Set Example

        individual_cheat = {
            '@Text': 'One hit kill',
            'Cheatline': {                  <---- Python Dictionary
                'Offset': '3D471B',
                'Section': '0',
                'ValueOn': '4D-29-A6-50-08-00-00',
                'ValueOff': '41-29-9E-50-08-00-00'
            }
        }
'''



#######################  Individual Cheat --> In | [Cheat Lines] --> Out  #######################



def get_cheat_lines_from_individual_cheat(individual_cheat):
    cheat_line_from_cheat = individual_cheat['Cheatline']
    if isinstance(cheat_line_from_cheat, dict):
        cheat_lines = [cheat_line_from_cheat]
    elif isinstance(cheat_line_from_cheat, list):
        cheat_lines = cheat_line_from_cheat
    return cheat_lines



##############################################################################
#                                                                            #
#                       SHN to JSON Workflow Function                        #
#                                                                            #
##############################################################################



'''
1. Convert XML String to JSON Dictionary Object.
2. Assign Cheat List to Variable `all_cheats`.
3. For Each Individual Cheat
    a. Create Empty Cheat Dictionary
    b. Parse and Slice Cheat to Populate Cheat Dictionary Object
    c. Append Cheat Object to Modifications List
4. Create Empty Master Cheat Dictionary
5. Parse and Slice JSON Dictionary Object to Populate Master Dictionary
6. Assign Modifications List as Value to Dictionary Key `mods`.
'''



#######################  SHN in XML --> In | JSON --> Out  #######################



def shn_to_json_workflow(xml_file_data):
    json_object = convert_xml_to_json_object(xml_file_data)
    all_cheats = get_all_cheats_list_from_json_data(json_object)
        #
    modifications_list = []
    for individual_cheat in all_cheats:
        cheat_dictionary = populate_cheat_object(individual_cheat)
        modifications_list.append(cheat_dictionary)
        #
    master_cheat_dictionary = populate_master_cheat_dictionary(json_object, modifications_list)
    return master_cheat_dictionary




