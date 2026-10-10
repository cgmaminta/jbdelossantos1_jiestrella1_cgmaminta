import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB
from urllib.parse import urlparse, parse_qs

layout = html.Div(
    [
        dcc.Store(id='movieprofile_movieid', storage_type='memory', data=0),

        html.H2('Movie Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='movieprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='movieprofile_title',
                                placeholder="Title"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Genre", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_genre',
                                    placeholder='Genre'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Release Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='movieprofile_releasedate',
                                placeholder='Release Date',
                                month_format='MMM Do, YY',
                            ),
                            width=5, 
                            className='dash-bootstrap'
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Country of Origin", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='movieprofile_country',
                                placeholder="Select where the movie was produced.",
                                searchable=True,
                                options=[]
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Main Actor", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='movieprofile_actor',
                                placeholder="Select the main actor or actress.",
                                searchable=True,
                                options=[]
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
            ]
        ),
        html.Div(
            [
                dbc.Checklist(
                    id='movieprofile_deleteind',
                    options= [dict(value=1, label="Mark as Deleted")],
                    value=[] 
                )
            ], 
            id='movieprofile_deletediv'
        ),
          dbc.Button(
            'Submit',
            id='movieprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success',
                    id = 'movieprofile_successmodalheader')
                ),
                dbc.ModalBody(
                    'Message here! Edit me please!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/movies/movie_management' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='movieprofile_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)

# DROPDOWNS
@app.callback(
    [
        Output('movieprofile_genre', 'options'),
        Output('movieprofile_country', 'options'),
        Output('movieprofile_actor', 'options'),
        Output('movieprofile_movieid', 'data'),
        Output('movieprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url','search')
    ]
)
def movieprofile_populategenres(pathname, urlsearch):
    if pathname == '/movies/movie_management_profile':

        # Genre dropdown
        genre_sql = """
        SELECT genre_name as label, genre_id as value
        FROM genres 
        WHERE genre_delete_ind = False
        """
        values = []
        cols = ['label', 'value']

        df = getDataFromDB(genre_sql, values, cols)
            # The output must be a dictionary with the following structure
            # options=[
            #     {'label': "Factorial", 'value': 1},
            #     {'label': "Palindrome Checker", 'value': 2},
            #     {'label': "Greeter", 'value': 3},
            # ]
        genre_options = df.to_dict('records')

        # Country dropdown
        country_sql = """
                SELECT country_name AS label,
                country_id AS value
                FROM countries
                WHERE country_delete_ind = False
                ORDER BY country_name ASC
                """

        country_df = getDataFromDB(country_sql, [], ['label','value'])
        country_options = country_df.to_dict('records') if not country_df.empty else []

        # Actors dropdown
        actor_sql = """
                SELECT CONCAT(actor_fname,' ', actor_lname) AS label,
                actor_id AS value
                FROM actors
                WHERE actor_delete_ind = False
                ORDER BY actor_lname, actor_fname ASC
                """

        actor_df = getDataFromDB(actor_sql, [], ['label','value'])
        actor_options = actor_df.to_dict('records') if not actor_df.empty else []

        # To check mode
        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]

        if create_mode == 'add':
            movieid = 0
            deletediv = 'd-none'
        else:
            movieid = int(parse_qs(parsed.query)['id'][0])
            deletediv= ''

        return [genre_options, country_options, actor_options, movieid, deletediv]
    else:
        raise PreventUpdate


# SAVE PROFILE  
@app.callback(
    [
        # dbc.Alert Properties
        Output('movieprofile_alert', 'color'),
        Output('movieprofile_alert', 'children'),
        Output('movieprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('movieprofile_successmodal', 'is_open'),
        Output('movieprofile_successmodalheader', 'children')
    ],
    [
        # For buttons, the property n_clicks 
        Input('movieprofile_submit', 'n_clicks')
    ],
    [
        # The values of the fields are States 
        # They are required in this process but they 
        # do not trigger this callback
        State('movieprofile_title', 'value'),
        State('movieprofile_genre', 'value'),
        State('movieprofile_releasedate', 'date'),
        State('movieprofile_country','value'),
        State('movieprofile_actor','value'),
        State('url', 'search'),
        State('movieprofile_movieid', 'data'),
        State('movieprofile_deleteind', 'value')
    ]
)
def movieprofile_saveprofile(submitbtn, title, genre, releasedate, country, actor, urlsearch, movieid, delete):
    ctx = dash.callback_context
    # The ctx filter -- ensures that only a change in url will activate this callback
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'movieprofile_submit' and submitbtn:
            # the submitbtn condition checks if the callback was indeed activated by a click
            # and not by having the submit button appear in the layout
            parsed = urlparse(urlsearch)
            # get the corresponding value for 'mode' from the URL
            create_mode = parse_qs(parsed.query)['mode'][0]
            # Set default outputs
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            # We need to check inputs
            if not title: # If title is blank, not title = True
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie title.'
            elif not genre:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie genre.'
            elif not releasedate:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie release date.'
            elif not country:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please select the country of origin of the movie.'
            elif not actor:
                alert_open =  True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please select the main actor or actress of the movie.'

            else: # all inputs are valid
                # Add the data into the db
                if create_mode == 'add':
                    title = title.strip()
                    check_sql = '''
                        SELECT movie_id 
                        FROM movies 
                        WHERE LOWER(movie_name) = LOWER(%s) 
                          AND movie_delete_ind = False
                    '''
                    duplicate_df = getDataFromDB(check_sql, [title], ['movie_id'])

                    if not duplicate_df.empty:
                        alert_open = True
                        alert_color = 'warning'
                        alert_text = f"The movie '{title}' already exists."
                        return [alert_color, alert_text, alert_open, modal_open, msg]
                    
                    sql = '''
                        INSERT INTO movies (movie_name, genre_id,
                            movie_release_date, 
                            country_id, actor_id, 
                            movie_delete_ind)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                    values = [title, genre, releasedate, country, actor, False]
                    msg = "Save Success"

                elif create_mode == 'edit':
                    sql = '''
                        UPDATE movies 
                        SET 
                            movie_name = %s,
                            genre_id = %s,
                            movie_release_date = %s,
                            country_id = %s,
                            actor_id = %s,
                            movie_delete_ind = %s
                        WHERE
                            movie_id = %s
                    '''
                    values = [title.strip(), genre, releasedate, country, actor, bool(delete), movieid]
                    msg = "Update Success"
                else:
                    raise PreventUpdate
                
                modifyDB(sql, values)

                # If this is successful, we want the successmodal to show
                modal_open = True
            return [alert_color, alert_text, alert_open, modal_open, msg]

        else: 
            raise PreventUpdate

    else:
        raise PreventUpdate

# Populating the movie details  
@app.callback(
    [
        Output('movieprofile_title', 'value'),
        Output('movieprofile_genre', 'value'),
        Output('movieprofile_releasedate', 'date'),
        Output('movieprofile_country','value'),
        Output('movieprofile_actor','value'),
        Output('movieprofile_deleteind', 'value'),
    ],
    [
        Input('movieprofile_movieid', 'modified_timestamp')
    ],
    [
        State('movieprofile_movieid', 'data'),
    ]
)

def movieprofile_loadprofile(timestamp, movieid):
    if movieid: # check if movieid > 0

        # Query from db 
        # country_id because you can populate only the countries there while others have their own module that's connected
        sql = """
            SELECT movie_name, 
                genre_id, 
                movie_release_date, 
                country_id,     
                actor_id,
                movie_delete_ind
            FROM movies
            WHERE movie_id = %s
        """
        values = [movieid]
        col = ['moviename', 'genreid', 'releasedate', 'country', 'actorid','deleted']

        df = getDataFromDB(sql, values, col)

        moviename = df['moviename'][0]

        # Our dropdown list has the genreids as values then it will display the corresponding labels
        genreid = int(df['genreid'][0])
        releasedate = df['releasedate'][0]
        country = df['country'][0]
        actor = int(df['actorid'][0]) # same as genre 
        deleted = [] if df['deleted'][0] == 0 else [1]

        return [moviename, genreid, releasedate, country, actor, deleted]

    else:
        raise PreventUpdate


@app.callback(
    [
        Output('movieprofile_submit', 'color'),
    ],
    [
        Input('movieprofile_deleteind', 'value')
    ],
    [
        
    ]
)
def movieprofile_deletewarn(delete):

    if delete:
        return ['danger']
    else:
        return ['primary']


        