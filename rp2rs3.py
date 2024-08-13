# Cameron Lindsey's rp to rs3 code, 2023
# University of North Alabama

import xml.etree.ElementTree as ET
from xml.dom import minidom
from dataclasses import dataclass
import os

'''
 Information about tpl_strct:

 It is a dictionary-based structure with a str key and a list 'value'.
 This structure repeats in a recursive fashion, with an int at the bottom.
 The str key is the relationship name that connects the elements inside its 'value'.
 The list 'value' can contain 2 elements (in the case of a rst relation type),
  or more than 2 (in the case of a convergence or multinuc relation type).

 Example of tpl_strct:
 {'convergence': [
     {'antithesis': [
         {'preparation': [1, 2]},
         3]},
     {'evidence': [
         {'nonvolitional-result': [
             {'disjunction': [6, 7]},
             {'elaboration': [5, 4]}
             ]},
         3]}
     ]}
'''


@dataclass(order=False)
class _Connection:
    id_num: int
    tag_type: str
    parent_id: int
    rel_name: str
    text: str

#class RhetoricalStructure:
class rp2rs3:
    #Public Class Constants - data used by other methods both inside the class and outside
    RELATIONSHIP_DATA = {
        '': 'rst', '???': 'rst', 'adversative-antithesis': 'rst', 'adversative-concession': 'rst',
        'antithesis': 'rst', 'attribution': 'rst', 'attribution-negative': 'rst', 'attribution-positive': 'rst',
        'background': 'rst', 'causal-cause': 'rst', 'causal-result': 'rst', 'cause': 'rst', 'circumstance': 'rst',
        'concession': 'rst', 'condition': 'rst', 'context-background': 'rst', 'context-circumstance': 'rst',
        'contingency-condition': 'rst',  'elaboration': 'rst', 'elaboration-additional': 'rst',
        'elaboration-attribute': 'rst',
        'e-elaboration': 'rst', 'evaluation-n': 'rst','evaluation-s': 'rst',
        'enablement': 'rst', 'evaluation': 'rst', 'evaluation-comment': 'rst',
        'evidence': 'rst', 'explanation-evidence': 'rst', 'explanation-justify': 'rst',
        'explanation-motivation': 'rst', 'interpretation': 'rst', 'justify': 'rst', 'manner': 'rst', 'means': 'rst',
        'mode-manner': 'rst', 'mode-means': 'rst', 'motivation': 'rst', 'nonvolitional-cause': 'rst',
        'nonvolitional-result': 'rst', 'organization-heading': 'rst', 'organization-phatic': 'rst',
        'organization-preparation': 'rst', 'otherwise': 'rst', 'preparation': 'rst', 'propositional-attitude': 'rst',
        'purpose': 'rst', 'purpose-attribute': 'rst', 'purpose-goal': 'rst', 'question': 'rst', 'reason': 'rst',
        'restatement': 'rst', 'restatement-partial': 'rst', 'result': 'rst', 'rst': 'rst', 'solutionhood': 'rst',
        'summary': 'rst', 'topic-question': 'rst', 'topic-solutionhood': 'rst', 'unconditional': 'rst', 'unless': 'rst',
        'unstated-relation': 'rst', 'volitional-cause': 'rst', 'volitional-result': 'rst',
# experimental
        'motivation-enablement': 'rst',
# end experimental
        'adversative-contrast': 'multinuc', 'conjunction': 'multinuc', 'contrast': 'multinuc', 'disjunction': 'multinuc',
        'joint': 'multinuc', 'joint-disjunction': 'multinuc', 'joint-list': 'multinuc', 'joint-other': 'multinuc',
        'joint-sequence': 'multinuc', 'list': 'multinuc', 'restatement-mn': 'multinuc',
        'restatement-repetition': 'multinuc', 'same-unit': 'multinuc', 'sequence': 'multinuc'
        }
    MULTINUC_RELATIONSHIPS = ['adversative-contrast', 'conjunction', 'contrast', 'disjunction', 'joint',
                              'joint-disjunction', 'joint-list', 'joint-other', 'joint-sequence', 'list',
                              'restatement-mn', 'restatement-repetition', 'same-unit', 'sequence']


# Initialization
    def __init__(self, rel_string: str, text_dict: dict[str, str]):
        # After _initialize_connections is called,
        # _connections will contain all the _Connection objects
        self._connections = list()
        
        rel_string = self._de_snakify(rel_string)
        self._initialize_connections(text_dict)
        tuple_structure = self._recursively_create_struct(rel_string)
        self._recursively_convert_struct(tuple_structure)


    def _de_snakify(self, rel_string: str) -> str:
        '''fixes the names of certain relation types in rel_string'''
        return(rel_string.replace('list_', 'list').replace('_', '-'))
        


    def _initialize_connections(self, text_dict: dict[str, str]):
        '''loops through all the text information in text_dict, and creates new _Connection nodes
        for each, adding them to _connections.
        
        This method could be updated to work with either a dictionary or an ordered enumerable
        without much difficulty.'''
        for key, text in list(text_dict.items()):
            self._connections.append(_Connection(int(key), "segment", None, None, text))
            
        return()


# Main Algorithm Driver Methods
    def _recursively_create_struct(self, rel_string: str):
        '''recursively calls itself to form the tpl_strct from the rel_string given'''
        if rel_string.isnumeric():  # base case, cast to int
            return(int(rel_string))

        next_parenthesis_index = rel_string.find('(')
        
        # Collection of the indexes of the characters that seperate the
        # arguments of the current recursive rel_string relationship types.
        # The first and last indexes are always the outermost parenthesis in rel_string.
        sub_arg_indexes = [next_parenthesis_index] + self._arg_seperator_indexes(rel_string) + [len(rel_string) - 1]

        # Loop through all the arguments of the outermost layer of rel_string and
        # recursively calculate their tpl_strct, adding it to the structure list
        structure = []
        for i in range(len(sub_arg_indexes) - 1):
            lower_bound = sub_arg_indexes[i] + 1
            upper_bound = sub_arg_indexes[i + 1]
            sub_arg = rel_string[lower_bound: upper_bound]
            structure.append(self._recursively_create_struct(sub_arg))

        # Return a dict with the relationship type and the structure list
        # as its key, value pair
        return({rel_string[:next_parenthesis_index]: structure})


    def _recursively_convert_struct(self, tpl_strct, parent: _Connection=None):
        '''recursively interprets the tpl_strct data structure, setting the attributes of the _Connection
        objects in _connections to the appropriate value'''
        if isinstance(tpl_strct, int):  # base case int found, return its corresponding _Connection object
            return(self._connections[tpl_strct - 1])

        if parent == None:  # first iteration setting parent object
            parent = self._gen_span()

        relation_type, sections = list(tpl_strct.items())[0]
        

        # The following logic for handling different relation types is complex.
        # To simplify this function, I have opted to only perform the type checks inside
        # this function, and call other functions to handle the rest of the logic
        if relation_type in self.MULTINUC_RELATIONSHIPS:    # multinuc relations handling
            self._multinuc_rel_convert_handler(parent, sections, relation_type)

        elif relation_type == 'convergence':    # convergence relations handling
            self._convergence_rel_convert_handler(tpl_strct, parent, sections)

        else:   # non-multinuc and non-convergence relations handling
            self._other_rel_convert_handler(parent, sections, relation_type)
            
        return(parent)


    def _multinuc_rel_convert_handler(self, parent: _Connection, sections: list, relation_type: str):
        '''handles the setting of attributes for multinuc relation types'''
        # Mark given parent as a multinuc relationship to its parent
        parent.tag_type = 'multinuc'

        for sub_section in sections:
            # If this argument is a base int argument, use the current parent
            # as the parent arg in the next recursive call.
            # Otherwise, create a new span object and use that as the parent,
            # or its connection to the next node will look like a convergence.
            if isinstance(sub_section, int):
                sub_parent = parent
            else:
                sub_parent = self._gen_span()

            child = self._recursively_convert_struct(sub_section, sub_parent)
            child.parent_id = parent.id_num
            child.rel_name = relation_type
                
        return()


    def _convergence_rel_convert_handler(self, tpl_strct, parent: _Connection, sections: list):
        '''handles the setting of attributes for convergence relation types'''
        # All sections will share a common structure as a child, as that structure is what
        # the other nodes are actually pointing at.
        common_strct = self._find_common_connection(tpl_strct)

        # If the common_strct is an int, we can use the current parent as
        # its parent object.
        # However, if it is more complex, then we need a new span to seperate
        # it from the current parent, otherwise the connections go crazy.
        if isinstance(common_strct, int):
            sub_parent = self._recursively_convert_struct(common_strct, parent)
        else:
            temp = self._gen_span()
            sub_parent = self._recursively_convert_struct(common_strct, temp)
            
        sub_parent.parent_id = parent.id_num
        sub_parent.rel_name = 'span'

        
        for section in sections:
            # Generate new relation_type and sections from children.
            # Omit the common_strct from the new sections.
            relation_type, sections2 = list(section.items())[0]
            sections2 = sections2[:-1]

            # Treat these new sections like multinuc relations,
            # minus marking parent as multinuc and
            # setting child.parent_id to sub_parent.id_num
            for sub_section2 in sections2:
                if isinstance(sub_section2, int):
                    section_parent = sub_parent
                    
                else:
                    section_parent = self._gen_span()
                    
                child = self._recursively_convert_struct(sub_section2, section_parent)
                child.parent_id = sub_parent.id_num
                child.rel_name = relation_type
                
        return()


    def _other_rel_convert_handler(self, parent: _Connection, sections: list, relation_type: str):
        '''handles the setting of attributes for all non-convergence and non-multinuc relation types'''
        # With these relation types, the first subset points to the 2nd subset,
        # so they must be calculated seperately
        sub_parent = self._gen_span()
        child1 = self._recursively_convert_struct(sections[0], sub_parent)
        last_set1 = self._find_last_set(child1, [])
        child2 = self._recursively_convert_struct(sections[1], sub_parent)
        last_set2 = self._find_last_set(child2, last_set1)

        # only del redundant spans if both children are text statements.
        # Eg. tplstruct looks like "RELATIONSHIPNAME(int, int)
        if child1.text and child2.text:
            self._del_redundant_span(sub_parent)

        # If both relations have the same parent, point child1 at a new span, preventing them
        # from having a multinuc-like joint. Use last_set to find the actual child1 node/s, as child2
        # overwrites this nodes connection during its recursive calls.
        # If last_set is a multinuc, it will be set back to a span during child2 recursive calls, so
        # it should be set back during this section. That is why there are these if, elif, else statements.
        if child1 == child2:
            if len(last_set1) == 1:
                child1 = self._gen_span()
                last_set1[0].parent_id = child1.id_num
                
            elif len(last_set2) == 1:
                child2 = self._gen_span()
                last_set2[0].parent_id = child2.id_num
                
            else:
                child1 = self._gen_span()
                child1.tag_type = 'multinuc'
                for last in last_set1:
                    last.parent_id = child1.id_num


        # Point child1 at child2 via relation_type relationship.
        # Then point child2 at parent via span relationship
        child1.parent_id = child2.id_num
        child1.rel_name = relation_type

        child2.parent_id = parent.id_num
        child2.rel_name = 'span'

        return()


# Main Algorithm Helper Methods
    def _arg_seperator_indexes(self, rel_string: str) -> list[int]:
        '''find the indexes of the characters seperating the arguments
        of the top level relationship type in rel_string.
        Returns those indexes in a list.'''
        struct_depth = 0
        arg_seperators = []
        
        for index, char in enumerate(rel_string):
            if struct_depth == 1 and char == ',':   # found comma seperating 2 args
                arg_seperators.append(index)
            elif char == '(':   # increase in nested depth
                struct_depth += 1
            elif char == ')':   # decrease in nested depth
                struct_depth -= 1
                
        return(arg_seperators)


    def _gen_span(self) -> _Connection:
        '''creates a new span _Connection and adds it to _connections
        Returns newly-created _Connection'''
        span = _Connection(self._connections[-1].id_num + 1, 'span', None, None, None)
        self._connections.append(span)
        return(span)


    def _del_redundant_span(self, to_delete: _Connection):
        '''removes the given _Connection object from _connections and deletes it'''
        self._connections.remove(to_delete)
        del to_delete
        return()


    def _find_common_connection(self, tpl_strct):
        '''finds the common structure for convergence relationships'''
        # To Note: when given tpl_strct, the last elements of the second-level relationships
        # of the convergence layer are always the common structure.
        # Ex:
        #    {'convergence': [
        #        {'enablement': [2, 1]},
        #        {'motivation': [3, 1]}
        #        ]}
        # In above example, the common structure is 1, as it is the second element of all
        # subelements of the convergence relationship. This holds true for all convergence
        # relationships.
        return(list(list(tpl_strct.values())[0][0].values())[0][-1])
        

    def _find_last_set(self, last: _Connection, avoiding: list[_Connection]) -> list[_Connection]:
        '''finds the connections that point at `last` while not being in `avoiding`'''
        last_sets = []
        for connection in self._connections:
            if last.id_num == connection.parent_id and not connection in avoiding:
                last_sets.append(connection)
                
        return(last_sets)


#XML Saving Helper Methods
    def _get_unique_relation_types(self) -> tuple[list[str], list[str]]:
        '''collects all the unique relationships present in the structure and
        sorts them into rst and multinuc types, returning both as lists'''
        rst = set()
        multinuc = set()
        valid_connections = [connection for connection in self._connections
                             if not connection.rel_name in [None, 'span']]
        for connection in valid_connections:
            if self.RELATIONSHIP_DATA[connection.rel_name] == 'multinuc':
                multinuc.add(connection.rel_name)
            else:
                rst.add(connection.rel_name)
        return(list(rst), list(multinuc))


    def _sort_relation_types(self, rsts: list[str], multinucs: list[str]) -> dict[str, str]:
        '''sorts the rst and multinuc lists, transforming them into dictionaries
        and combining them together into a single sorted dictionary'''
        rst_dict = {rel: 'rst' for rel in sorted(rsts)}
        multinuc_dict = {rel: 'multinuc' for rel in sorted(multinucs)}
        return(rst_dict | multinuc_dict)


# Printing
    def __repr__(self) -> str:
        return(str(self))

    
    def __str__(self) -> str:
        return(str(self.structure_repr))


# Public Methods
    @property
    def relationship_types(self) -> dict[str, str]:
        '''creates sorted dictionary of the relationships used in the dictionary
        and their corresponding tag type (rst or multinuc)'''
        rsts, multinucs = self._get_unique_relation_types()
        output = self._sort_relation_types(rsts, multinucs)
        return(output)


    @property
    def connections(self):
        return(self._connections)


    @property
    def structure_repr(self) -> dict[int, list[str, int, str, str]]:
        return({c.id_num: [c.tag_type, c.parent_id, c.rel_name, c.text] for c in self._connections})

    def save_to_XML(self, path: str, name: str):
            '''saves the structure in XML format to the file specified by the path and name parameters'''
            root = ET.Element('rst')
            self._populate_header(root)
            self._populate_body(root)

            data = minidom.parseString(ET.tostring(root)).toprettyxml(indent='    ')

            with open(os.path.join(path, name), 'wb') as file:
                file.write(data.encode('utf8'))

            return()

##    def save_to_XML(self, path: str, name: str):
##        '''saves the structure in XML format to the file specified by the path and name parameters'''
##        root = ET.Element('rst')
##        self._populate_header(root)
##        self._populate_body(root)
##
##        data = minidom.parseString(ET.tostring(root)).toprettyxml(indent='    ')
##
##        #with open(f"{path}\\{name}", 'w') as file: # OS dependency?
####        with open(f"{path}/{name}", 'w') as file:   
####            file.write(data)
##
##        with open(os.path.join(path, name), 'w') as file:
##            file.write(data)
##
##        return()


# Save as XML Driver Methods
    def _populate_header(self, root: ET.Element):
        '''populates the header of the XML File given its root'''
        header = ET.SubElement(root, 'header')
        relations = ET.SubElement(header, 'relations')

        for rel_name, rel_type in list(self.relationship_types.items()):
            rel = ET.SubElement(relations, 'rel')
            rel.set('name', rel_name)
            rel.set('type', rel_type)
            
        return()


    def _populate_body(self, root: ET.Element):
        '''handles populating the body of the XML File with segments
        and group elements'''
        body = ET.SubElement(root, 'body')
        for connection in self._connections:
            if connection.tag_type == 'segment':
                self._create_segment_element(body, connection)
                
            else:
                self._create_group_element(body, connection)
                
        return()


    def _create_segment_element(self, body: ET.Element, connection: _Connection):
        '''handles converting the _Connection object into a segment-type tag
        in the body of the XML File'''
        segment = ET.SubElement(body, 'segment')
        segment.set('id', str(connection.id_num))

        # If parent_id is None, then this segment is disconnected from the rest of
        # the structure, and the parent and relname information should not be set
        if connection.parent_id != None:
            segment.set('parent', str(connection.parent_id))
            segment.set('relname', connection.rel_name)
            
        segment.text = connection.text
        
        return()


    def _create_group_element(self, body: ET.Element, connection: _Connection):
        '''handles converting the _Connection object into a group-type tag
        in the body of the XML File'''
        group = ET.SubElement(body, 'group')
        group.set('id', str(connection.id_num))
        group.set('type', connection.tag_type)

        # If parent_id or rel_name is None, then this segment is the top,
        # so the parent and relname information should not be set
        if connection.parent_id != None:
            group.set('parent', str(connection.parent_id))
            group.set('relname', connection.rel_name)
            
        return()
