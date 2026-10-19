import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from apps import commonmodules as cm
from apps import home
from apps.movies import movie_management as mm
from apps.movies import movie_management_profile as mmp
from apps.genres import genre_management as gm
from apps.genres import genre_management_profile as gmp


# Importing your app variable from app.py so we can use it
from app import app

app.layout = html.Div(
     [
         # Location Variable -- contains details about the url
         dcc.Location(id='url', refresh=True),

         cm.navbar,

         # Page Content -- Div that contains page layout
         html.Div(id='page_content', className='m-2 p-2'),
     ]
)

@app.callback(
    [
        Output('page_content', 'children')
    ],
    [
        Input('url', 'pathname')
    ]
)
def displaypage (pathname):
    
    # This code block extracts the id of the triggered input
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]   
    else:
        raise PreventUpdate

        
    # This code block executes action based on the value of eventid
    if eventid == 'url':
        if pathname == '/' or pathname == '/home':
            returnlayout = home.layout

        elif pathname == '/movies':
            returnlayout = 'moviepage'

        elif pathname == '/movies/movie_management':
            returnlayout = mm.layout
            
        elif pathname == '/movies/movie_management_profile':
            returnlayout = mmp.layout

        elif pathname == '/genres/genre_management':
            returnlayout = gm.layout
            
        elif pathname == '/genres/genre_management_profile':
            returnlayout = gmp.layout
        else:
            returnlayout = 'error404'
    
    else: 
        raise PreventUpdate
    
    return [returnlayout]

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run(debug=False)
