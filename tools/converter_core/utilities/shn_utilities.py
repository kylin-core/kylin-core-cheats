# ------------------------------------------------------------------------------------------------------------------------------------
#
#
#   This Utility contains functions used to work with XML Objects and SHN-Based Cheats.
#
#
#   While this is the SHN (XML) Utility, many of the functions and doc-strings below reference JSON.
#   The functions in this Utility take JSON as an input and ultimately output SHN (XML).
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
#                                                  Functions Related to Converting JSON to SHN (XML)                                                  #
#                                                                                                                                                     #
#######################################################################################################################################################



'''
XML uses the terminology element, attributes, and tags, among others.
For simplicity, this code uses start_tag, end_tag, and entity.


Start Tags and End Tags should be clear, as tags are foundational items in XML.


    Start Tag Example:
        <Cheatline>

    End Tag Example:
        </Cheatline>


An Entity object, in the context of this code, refers to the specific elements
related to an individual cheat in XML format.


The Entities used are:
    * Offset
    * Section
    * ValueOn
    * ValueOff


These entity names should be very familiar to anyone who has taken even a cursory
look at a JSON or XML Cheat File.  These Entity objects include their Start
and End Tags.

The entire collection of Entity Objects for a given individual cheat is
referred to as a `Cheat Entity`.


    Example Individual Cheat Entity:

        <Cheat Text="Infinite Stamina">
            <Cheatline>
                <Offset>751BF8</Offset>
                <Section>0</Section>
                <ValueOn>90-90-90-90</ValueOn>
                <ValueOff>C5-FA-5C-C1</ValueOff>
            </Cheatline>
        </Cheat>
'''


##############################################################################
#                                                                            #
#                    Generate Trainer Start Tag Function                     #
#                                                                            #
##############################################################################



#######################  XML Version and Encoding Line | Trainer Start Tag  #######################



def generate_trainer_start_tag(json_file_data):
    game_name = json_file_data['name']
    game_id = json_file_data['id']
    game_version = json_file_data['version']
    game_process = json_file_data['process']
    cheat_author = json_file_data['credits'][0]
    game_name = json_file_data['name']
        #
    trainer_start_tag = f'''<?xml version="1.0" encoding="utf-16"?>
<Trainer
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Game="{game_name}" Moder="{cheat_author}" Cusa="{game_id}" Version="{game_version}" Process="{game_process}">'''
    return trainer_start_tag



##############################################################################
#                                                                            #
#                     Generate Trainer End Tag Function                      #
#                                                                            #
##############################################################################



#######################  Trainer End Tag  #######################



def generate_trainer_end_tag():
    trainer_end_tag = f'''</Trainer>'''
    return trainer_end_tag



##############################################################################
#                                                                            #
#            Generate Genre and Item Start and End Tags Function             #
#                                                                            #
##############################################################################



from utilities.common_utilities import four_spaces



#######################  Genre Start and End Tag (In One) | Item Start and End Tag (In One)  #######################



def generate_genre_and_item_tags():
    # Example: '    <Genres Name="Adventure" />\n    <Items />\n'
    genre_and_item_tags = f'''{four_spaces}<Genres Name="Adventure" />
{four_spaces}<Items />\n'''
    return genre_and_item_tags



##############################################################################
#                                                                            #
#                     Generate Cheat Start Tag Function                      #
#                                                                            #
##############################################################################



#######################  Cheat Start Tag and Text  #######################



def generate_cheat_start_tag(cheat_name):
    # Example: '    <Cheat Text="Infinite Health">\n'
    cheat_start_tag = f'''{four_spaces}<Cheat Text="{cheat_name}">{new_line_string}'''
    return cheat_start_tag


##############################################################################
#                                                                            #
#                      Generate Cheat End Tag Function                       #
#                                                                            #
##############################################################################



from utilities.common_utilities import new_line_string



#######################  Cheat End Tag  #######################



def generate_cheat_end_tag():
    # Example: '    </Cheat>\n'
    cheat_end_tag = f'''{four_spaces}</Cheat>{new_line_string}'''
    return cheat_end_tag



##############################################################################
#                                                                            #
#                   Generate Cheat Line Start Tag Function                   #
#                                                                            #
##############################################################################



from utilities.common_utilities import eight_spaces



#######################  Cheatline Start Tag  #######################



def generate_cheat_line_start_tag():
    # Example: '       <Cheatline>\n'
    cheat_line_start_tag = f'''{eight_spaces}<Cheatline>{new_line_string}'''
    return cheat_line_start_tag



##############################################################################
#                                                                            #
#                    Generate Cheat Line End Tag Function                    #
#                                                                            #
##############################################################################



#######################  Cheatline End Tag  #######################



def generate_cheat_line_end_tag():
    # Example: '        </Cheatline>\n'
    cheat_line_end_tag = f'''{eight_spaces}</Cheatline>{new_line_string}'''
    return cheat_line_end_tag



##############################################################################
#                                                                            #
#                           Generate Offset Entity                           #
#                                                                            #
##############################################################################



from utilities.common_utilities import twelve_spaces



#######################  Offset Entity  #######################



def generate_offset_entity(offset):
    # Example: '            <Offset>760519</Offset>\n'
    offset_entity = f'''{twelve_spaces}<Offset>{offset}</Offset>{new_line_string}'''
    return offset_entity



##############################################################################
#                                                                            #
#                          Generate Section Entity                           #
#                                                                            #
##############################################################################



#######################  Section Entity  #######################



def generate_section_entity():
    # Example: '            <Section>0</Section>\n'
    section_entity = f'''{twelve_spaces}<Section>0</Section>{new_line_string}'''
    return section_entity



##############################################################################
#                                                                            #
#                  Generate Value When On (ValueOn) Entity                   #
#                                                                            #
##############################################################################



#######################  On Value Entity  #######################



def generate_on_value_entity(normalized_on_value):
    # Example: '            <ValueOn>90-90-90-90-90</ValueOn>\n'
    on_value_entity = f'''{twelve_spaces}<ValueOn>{normalized_on_value}</ValueOn>{new_line_string}'''
    return on_value_entity



##############################################################################
#                                                                            #
#                 Generate Value When Off (ValueOff) Entity                  #
#                                                                            #
##############################################################################



#######################  Off Value Entity  #######################



def generate_off_value_entity(normalized_off_value):
    # Example: '            <ValueOff>C5-FA-10-45-B8</ValueOff>\n'
    off_value_entity = f'''{twelve_spaces}<ValueOff>{normalized_off_value}</ValueOff>{new_line_string}'''
    return off_value_entity



##############################################################################
#                                                                            #
#               Individual XML Cheat Entity Workflow Function                #
#                                                                            #
##############################################################################



from utilities.common_utilities import add_hyphens_every_two_characters



#######################  Slice Individual Cheat | Populate Cheat Object  #######################



def individual_xml_cheat_entity_workflow(individual_cheat):
    cheat_name = individual_cheat['name']
    offset     = individual_cheat['memory'][0]['offset']
    on_value   = individual_cheat['memory'][0]['on']
    off_value  = individual_cheat['memory'][0]['off']
        #
    normalized_on_value  = add_hyphens_every_two_characters(on_value).upper()
    normalized_off_value = add_hyphens_every_two_characters(off_value).upper()
        #
    cheat_start_tag = generate_cheat_start_tag(cheat_name)
    cheat_line_start_tag = generate_cheat_line_start_tag()
    offset_entity = generate_offset_entity(offset)
    section_entity = generate_section_entity()
    on_value_entity = generate_on_value_entity(normalized_on_value)
    off_value_entity = generate_off_value_entity(normalized_off_value)
    cheat_line_end_tag = generate_cheat_line_end_tag()
    cheat_end_tag = generate_cheat_end_tag()
        #
    # https://stackoverflow.com/a/48881390
    cheat_entity = (
        f'{cheat_start_tag}{cheat_line_start_tag}{offset_entity}{section_entity}'
        f'{on_value_entity}{off_value_entity}{cheat_line_end_tag}{cheat_end_tag}'
        )
    return cheat_entity



############################################################################
#                                                                          #
#                      JSON to XML Workflow Function                       #
#                                                                          #
############################################################################



'''
1. Generate Trainer Start Tag.
2. Assign Cheat List (Mods) to Variable `all_cheats`.
3. For Each Individual Cheat
    a. Slice JSON and Assign to Variables
    b. Add Hyphens to On and Off Values
    c. Ensure On and Off Values are Upper Case
    d. Generate Cheat Start Tag
    e. Generate Cheat Line Start Tag
    f. Generate Offset Entity
    g. Generate Section Entity
    h. Generate On Value Entity
    i. Generate Off Value Entity
    j. Generate Cheat Line End Tag
    k. Generate Cheat End Tag
    l. Combine Generate Object into `Cheat Entity`
    m. Concatenate Cheat Entity to XML Cheat List
4. Generate Trainer End Tag
5. Concatenate Trainer Start Tag, XML Cheat List, and Trainer End Tag
'''



#######################  JSON --> In | SHN in XML --> Out  #######################



def json_to_xml_workflow(json_file_data):
    xml_cheat_list = ''
    trainer_start_tag = generate_trainer_start_tag(json_file_data)
    genre_and_item_tags = generate_genre_and_item_tags()
    all_cheats = json_file_data['mods']
    for individual_cheat in all_cheats:
        cheat_entity = individual_xml_cheat_entity_workflow(individual_cheat)
        xml_cheat_list = xml_cheat_list + cheat_entity
    trainer_end_tag = generate_trainer_end_tag()
    shn_cheat = f'''{trainer_start_tag}{genre_and_item_tags}{xml_cheat_list}{trainer_end_tag}'''
    return shn_cheat



##############################################################################
#                                                                            #
#                   Normalize XML Entity Indents Function                    #
#                                                                            #
##############################################################################



'''
While not all the SHN files in online Cheat Repositories are standardized or consistent,
two spaces is the most common ident used.


    See:
        https://github.com/GoldHEN/GoldHEN_Cheat_Repository/tree/main/shn


When this scripts writes the JSON cheats, it uses an ident of four.
This utility uses indents that are multiples of four for each of the entities it creates.


    from utilities.common_utilities import four_spaces
    from utilities.common_utilities import eight_spaces
    from utilities.common_utilities import twelve_spaces


If the input file is JSON, the resulting output SHN file uses four spaces due to this utility.
If the input file is SHN, the resulting output SHN file would be identical to the input file.


        def conversion_workflow(file_type, file_data):
            if file_type == 'json':
                json_cheat_object = file_data
                shn_cheat_object = json_to_xml_workflow(file_data)
            elif file_type == 'shn':
                json_cheat_object = shn_to_json_workflow(file_data)
                shn_cheat_object = file_data    <------- Input and output equal
            elif file_type == 'mc4':
                shn_cheat_object = decrypt_mc4_to_shn(file_data)
                json_cheat_object = shn_to_json_workflow(shn_cheat_object)
            return json_cheat_object, shn_cheat_object


The result is that there would be inconsistencies between the output files depending on the file type
of the input file.  

The following function normalizes the `shn_cheat_object` using idents that are multiples of four.
Not only does this create consistency, it also provides an easy method to standardize existing SHN files
at speed (and with a little tweaking, at scale).
'''



import re



#######################  (╯°□°）╯︵┻━┻ --> In | ┬─┬ノ(ಠ_ಠノ) --> Out  #######################



def normalize_xml_entity_idents(shn_cheat_object):
    # https://stackoverflow.com/a/38162461
    shn_cheat_object = re.sub(r'[^\S\n\t]+xmlns:xsd', f'{new_line_string}{four_spaces}xmlns:xsd', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+xmlns:xsi', f'{new_line_string}{four_spaces}xmlns:xsi', shn_cheat_object)
        #
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Genres Name ', f'{four_spaces}<Genres Name ', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Items />', f'{four_spaces}<Items />', shn_cheat_object)
        #
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Cheat ', f'{four_spaces}<Cheat ', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+</Cheat>', f'{four_spaces}</Cheat>', shn_cheat_object)
        #
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Cheatline>', f'{eight_spaces}<Cheatline>', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+</Cheatline>', f'{eight_spaces}</Cheatline>', shn_cheat_object)
        #
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Offset>', f'{twelve_spaces}<Offset>', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+<Section>', f'{twelve_spaces}<Section>', shn_cheat_object)
        #
    shn_cheat_object = re.sub(r'[^\S\n\t]+<ValueOn>', f'{twelve_spaces}<ValueOn>', shn_cheat_object)
    shn_cheat_object = re.sub(r'[^\S\n\t]+<ValueOff>', f'{twelve_spaces}<ValueOff>', shn_cheat_object)
    return shn_cheat_object

