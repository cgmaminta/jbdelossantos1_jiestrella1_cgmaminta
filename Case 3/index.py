import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

# Importing your app variable from app.py so we can use it
from app import app
from apps import commonmodules as cm
from apps import home, signup, login ##update
from apps.movies import movie_management, movie_management_profile
from apps.genres import genre_management, genre_management_profile
from apps.reports import report
from apps.actors import actors_management, actors_management_profile

CONTENT_STYLE = {
    "margin-top": "1em",
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

app.layout = html.Div(
    [
        # Location Variable -- contains details about the url
        dcc.Location(id='url', refresh=True),

        # LOGIN DATA
        # 1) logout indicator, storage_type='session' means that data will be retained
        #  until browser/tab is closed (vs clearing data upon refresh)
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),
        
        # 2) current_user_id -- stores user_id
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        
        # 3) currentrole -- stores the role
        # we will not use them but if you have roles, you can use it
        dcc.Store(id='currentrole', data=-1, storage_type='session'),

        # Adding the navbar
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),

        # Page Content -- Div that contains page layout
        html.Div(id='page_content', className='m-2 p-2'),
    ]
)

@app.callback(
    [
        Output('page_content', 'children'),
        Output('sessionlogout', 'data'),
        Output('navbar_div', 'className'),
    ],
    [
        # If the path (i.e. part after the website name; 
        # in url = youtube.com/watch, path = '/watch') changes, 
        # the callback is triggered
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage (pathname,
                 sessionlogout, userid):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        
    else:
        raise PreventUpdate
    
    if eventid == 'url':
        if userid < 0: # if logged out
            if pathname == '/':
                returnlayout = login.layout
            elif pathname == '/signup':
                returnlayout = signup.layout
            else:
                returnlayout = '404: request not found'
            
        else:    
            if pathname == '/logout':
                returnlayout = login.layout
                sessionlogout = True
                
            elif pathname == '/' or pathname == '/home':
                # From the imported module 'home', we get the layout variable
                returnlayout = home.layout

            elif pathname == '/reports/report':
                returnlayout = report.layout

            elif pathname == '/genres/genre_management':
                returnlayout = genre_management.layout

            elif pathname == '/genres/genre_management_profile':
                returnlayout = genre_management_profile.layout

            elif pathname == '/movies/movie_management':
                returnlayout = movie_management.layout
            elif pathname == '/movies/movie_management_profile':
                returnlayout = movie_management_profile.layout

            elif pathname == '/actors/actors_management':
                returnlayout = actors_management.layout
            elif pathname == '/actors/actors_management_profile':
                returnlayout = actors_management_profile.layout
            else:
                returnlayout = '404: request not found'
                
        # decide sessionlogout value
        logout_conditions = [
            pathname in ['/', '/logout'],
            userid == -1,
            not userid
        ]
        sessionlogout = any(logout_conditions)
        
        # hide navbar if logged-out; else, set class/style to default
        navbar_classname = 'd-none' if sessionlogout else ''
        
        return [returnlayout, sessionlogout, navbar_classname]
    else:
        raise PreventUpdate
    

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run(debug=False)
