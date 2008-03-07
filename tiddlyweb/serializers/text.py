"""
Text based serializers.
"""

import urllib

def recipe_as(recipe, sortkey):
    """
    Never sort a recipe, so ignore sortkey, but
    keep it there for sake of the interface.
    """
    lines = []
    for bag, filter in recipe:
        line = ''
# enable BagS in recipes
        if type(bag) != str:
            bag = bag.name
        line += '/bags/%s' % urllib.quote(bag)
        if filter:
            line += '?%s' % urllib.quote(filter)
        lines.append(line)
    return "\n".join(lines)

def as_recipe(recipe, input):
    """
    Turn a string back into a recipe.
    """
    lines = input.split('\n')
    recipe_lines = []
    for line in lines:
        bag, filter = line.split('?')
        bagname = urllib.unquote(bag.split('/')[2])
        filter = urllib.unquote(filter)
        recipe_lines.append([bagname, filter])
    recipe.set_recipe(recipe_lines)
    return recipe

def bag_as(bag, sortkey):
    """
    List the tiddlers in a bag as text.

    Is the bag an ordered list, so we shouldn't be sorting.
    """
    lines = []
    for tiddler in sorted(bag.list_tiddlers(), key=sortkey):
        line = 'tiddlers/%s' % urllib.quote(tiddler.title)
        lines.append(line)
    return "\n".join(lines)

def as_bag(bag, input):
    pass

def tiddler_as(tiddler, sortkey):
    return 'title: %s\nmodifier: %s\ntags: %s\n\n%s\n' \
            % (tiddler.title, tiddler.modifier, tags_as(tiddler.tags, sortkey), tiddler.content)

def as_tiddler(tiddler, input):
    pass

def tags_as(tags, sortkey):
    tag_string_list = []
    for tag in sorted(tags, key=sortkey):
        if ' ' in tag:
            tag = '[[%s]]' % tag
        tag_string_list.append(tag)
    return ' '.join(tag_string_list)