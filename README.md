# State [![Build Status](https://travis-ci.org/hyzhak/bot-story.svg?branch=develop)](https://travis-ci.org/hyzhak/bot-story)

Under active development

# Idea

Easy reading API to describe dialogs (scenery) of bots in Python language.
Key problem is asyn nature of any dialog - 
we can wait for are months answer from user and should store context 
until that. As well dialog structure should be simply and clear 
and show sequence of questions and reactions. 
 
Sure dialog can be made in diagrams but my thought that code should 
clear enough to show story of dialog and should be open for modification. 

# Draft of API 0.2.0

## Simple example

```python
"""
v0.2.0
Bot asks user about destionation of space travelling.
- stateless story. it stores context of story (current question and results) somewhere (maybe DB)
"""
@story.on('lets go!')
def stateless_story(message):
    @story.then()
    def then(message):
        return ask_location(message['user'], text='Where do you go?')

    @story.then()
    def then(message):
        store_destination(message['location'])
        return ask_location(message['user'], text='Where do you now?')

    @story.then()
    def then(message):
        store_origin(message['location'])
        return tell(message['user'], 'Thanks! Give me a minute I will find you right spaceship!')
```

## example with bifurcations

```python
"""
v0.2.1
Bot asks user about destionation of space travelling.
- stateless story. it stores context of story (current question and results) somewhere (maybe DB)
"""
@story.on('lets go!')
def stateless_story_with_bifurcation():
    @story.then()
    def request_destination(message):
        return ask_location(message['user'], text='Where do you go?')

    @story.then()
    def receive_destination(message):
        location = message['location']]
        if location == 'stars':
            #cycle back
            return ask_location(message['user'], text='Which star do you prefer?', then=receive_destination)
        elif location == 'planets':
            #cycle back
            return ask_location(message['user'], text='Which planet do you prefer?', then=receive_destination)
        elif:
            return choose_option(top10_planets, 
                                 text='Here is the most popular places. Maybe you would like to choose one?',
                                 then=receive_destination_options)
        else:
            store_destination(message['location'])
            return request_origin(message)

    @story.then()
    def receive_destination_options(message):
        store_destination(message['location'])
        return request_origin(message)

    @story.then()
    def request_origin(message):
        return ask_location(message['user'], text='Where do you now?', topic='get-origin')

    @story.then()
    def receive_origin(message):
        store_origin(message['location'])
        return tell(message['user'], 'Thanks! Give me a minute I will find you right spaceship!')
```

## example of callable function

```python

from ... import chat, story
from ...matchers.any import any
from ...matchers.location import location
from ...matchers.text import text


@story.callable()
def ask_location():
    """
    v0.2.2

    case/default/recursion version
    based on indents and no any goto

    :return:
    """
    @story.begin()
    def ask(body, options=None, user=None):
        if not options:
            # default aliases for current user
            # like 'home', 'work', or other
            options = default_aleases(user)
        chat.say(body, options, user)
        return {
            'args': {
                'location': location.Any(),
                'option': option.Any(),
                'text': text.Any(),
            },
        }

    # 2 wait for answer
    @story.case(match='location')
    def location_case():
        @story.part()
        def return_location(message):
            return {
                'return': message,
            }

    @story.case(match='option')
    def aliase():
        @story.part()
        def return_aliase(message):
            # it can be location or any other message data
            return {
                'return': message['option']['data']
            }

    @story.case(match='text')
    def text_case():
        @story.part()
        def parse_text(message):
            text_message = message['text']['raw']
            # try aliases (common names like home, work, or other)
            aliase = aliases.lookup(text_message)
            if aliase:
                return {
                    'return': {
                        'location': aliase['data'],
                    }
                }

            # if it is not alias maybe it is name of some place
            options = googlemap.lookup_location_by_name(text_message)
            if len(options) > 0:
                return {
                    'args': 'many',
                    'wait': chat.choose_option(
                        body='We have few options',
                        options=[{'title': o.name, 'data': o.json()} for o in options],
                        user=message['user'],
                    ),
                }
            else:
                return {
                    'args': None,
                }

        @story.case(value='many')
        def have_options():
            @story.part()
            def choose_one_location_from_many(message):
                location = message['option']['data']
                if location:
                    return {
                        'return': {
                            'location': location,
                        },
                    }
                else:
                    # choose something else
                    pass

        @story.case(value=None)
        def not_any_option():
            @story.check_alternative_stories()
            @story.part()
            def do_you_have_other_data(message):
                text_message = message['text']['raw']
                return chat.ask(
                    body='I can not find {} on map. Do you mean something else? Skip it?'.format(text_message),
                    options=[{
                        'title': 'skip',
                        'data': 'skip',
                    }],
                    user=message['user'],
                )

            @story.part()
            def unknown_name(message):
                if message['option']['data'] == 'skip':
                    return {
                        'return': None,
                    }
                else:
                    # TODO: restart (tail recursion?)
                    return {
                        # ????
                        'recursion': location_case,
                    }

    @story.case(default=True)
    def default_case():
        @story.check_alternative_stories()
        @story.part()
        def react_on_joke(message):
            chat.say('Very funny! :)', message['user'])
            return {
                'return': None,
            }


```
[original sources](https://gist.github.com/hyzhak/b9adcc938abe9bfb4335cf31ef0abbee)
