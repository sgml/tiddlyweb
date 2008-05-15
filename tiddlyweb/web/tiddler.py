
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.store import Store, NoTiddlerError, NoBagError
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.web.http import HTTP404, HTTP415, HTTP409
from tiddlyweb import control
from tiddlyweb import web

# XXX duplication with get_by_recipe, refactor
def _tiddler_from_path(environ):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    revision = environ['wsgiorg.routing_args'][1].get('revision', None)
    if revision:
        revision = web.handle_extension(environ, revision)
    else:
        tiddler_name = web.handle_extension(environ, tiddler_name)

    tiddler = Tiddler(tiddler_name)
    if revision:
        try:
            tiddler.revision = int(revision)
        except ValueError, e:
            raise HTTP404, '%s not a revision of %s: %s' % (revision, tiddler_name, e)
    tiddler.bag = bag_name

    return tiddler

def get_by_recipe(environ, start_response):
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    revision = environ['wsgiorg.routing_args'][1].get('revision', None)
    if revision:
        revision = web.handle_extension(environ, revision)
    else:
        tiddler_name = web.handle_extension(environ, tiddler_name)

    tiddler = Tiddler(tiddler_name)
    if revision:
        try:
            tiddler.revision = int(revision)
        except ValueError, e:
            raise HTTP404, '%s not a revision of %s: %s' % (revision, tiddler_name, e)

    recipe = Recipe(recipe_name)
    store = environ['tiddlyweb.store']
    store.get(recipe)

    try:
        bag = control.determine_tiddler_bag_from_recipe(recipe, tiddler)
    except NoBagError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    tiddler.bag = bag.name

    return _send_tiddler(environ, start_response, tiddler)

def get(environ, start_response):
    tiddler = _tiddler_from_path(environ)

    return _send_tiddler(environ, start_response, tiddler)

def _send_tiddler(environ, start_response, tiddler):

    store = environ['tiddlyweb.store']

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tiddler

    try:
        content = serializer.to_string()
    except TiddlerFormatError, e:
        raise HTTP415, e

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [content]

def put_by_recipe(environ, start_response):
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    tiddler_name = web.handle_extension(environ, tiddler_name)
    store = environ['tiddlyweb.store']
    content_type = environ['tiddlyweb.type']

    tiddler = Tiddler(tiddler_name)
    recipe = Recipe(recipe_name)
    store.get(recipe)

    try:
        bag = control.determine_bag_for_tiddler(recipe, tiddler)
    except NoBagError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    tiddler.bag = bag.name

    return _put_tiddler(environ, start_response, tiddler)

def put(environ, start_response):
    tiddler = _tiddler_from_path(environ)

    return _put_tiddler(environ, start_response, tiddler)

def _put_tiddler(environ, start_response, tiddler):

    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    content_type = environ['tiddlyweb.type']

    if content_type != 'text/plain' and content_type != 'application/json':
        raise HTTP415, '%s not supported yet' % content_type

    content = environ['wsgi.input'].read(int(length))
    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tiddler
    serializer.from_string(content.decode('UTF-8'))

    try:
        store.put(tiddler)
    except NoBagError, e:
        raise HTTP409, "Unable to put tiddler, %s. There is no bag named: %s (%s). Create the bag." % \
                (tiddler.title, tiddler.bag, e)

    start_response("204 No Content",
            [('Location', web.tiddler_url(environ, tiddler))])

    return []

