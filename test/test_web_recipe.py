
"""
Test that GETting a recipe in wiki form, gets a tiddlywiki.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore

from tiddlyweb.store import Store

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.default_app('urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = Store('text')
    reset_textstore()
    muchdata(module.store)

def test_get_recipe_wiki():
    """
    Return a wiki for a recipe we can access.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.wiki',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert 'i am tiddler 8' in content, 'wiki contains tiddler 8'

def test_get_recipe_txt():
    """
    Return a wiki for a recipe we can access.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    assert response['status'] == '200'
    assert '/bags/bag8/tiddlers?tiddler8' in content

def test_get_recipe_not():
    """
    Return a 415 when content type no good.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.xml',
            method='GET')

    assert response['status'] == '415'

def test_get_recipe_not_with_accept():
    """
    Return a default content type when the extension and
    content type conflict.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.xml',
            method='GET', headers={'Accept': 'text/plain'})

    assert response['status'] == '200'

def test_get_missing_recipe():
    """
    Return 404 for a recipe that is not there.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/not_there',
            method='GET')

    assert response['status'] == '404', 'response status should be 404'

def test_get_recipe_tiddler_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert len(content.rstrip().split('\n')) == 12, 'len tiddlers should be 12 is %s' % len(content.split('\n'))

def test_get_recipes_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 3, 'len recipe should be 3 is %s' % len(content.rstrip().split('\n'))

def test_get_recipes_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 1, 'len recipe should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_recipes_json():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.json',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'application/json; charset=UTF-8', \
            'response content-type should be application/json; charset=UTF-8 is %s' % response['content-type']
    info = simplejson.loads(content)
    assert type(info) == list
    assert len(info) == 1
    assert info[0] == 'long'

def test_get_recipes_unsupported_neg_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_recipes_unsupported_neg_format_with_accept():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']

def test_put_recipe():
    """
    Get a recipe as json then put it back with a different name.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.json',
            method='GET')

    json = content
    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'

def test_put_recipe_415():
    """
    Get a recipe as json then fail to put it back as text.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    text = content
    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=text)

    assert response['status'] == '415'
