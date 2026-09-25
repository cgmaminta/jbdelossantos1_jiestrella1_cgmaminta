import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB
from urllib.parse import urlparse, parse_qs

layout = html.Div(
    [
        dcc.Store(id='genreprofile_genreid', storage_type='memory', data=0),

        html.H2('Genre Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='genreprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='genreprofile_title',
                                placeholder="Title"
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
                    id='genreprofile_deleteind',
                    options= [dict(value=1, label="Mark as Deleted")],
                    value=[] 
                )
            ], 
            id='genreprofile_deletediv'
        ),
          dbc.Button(
            'Submit',
            id='genreprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success',
                    id = 'genreprofile_successmodalheader')
                ),
                dbc.ModalBody(
                    'Message here! Edit me please!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/genres/genre_management' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='genreprofile_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)

@app.callback(
    [
        Output('genreprofile_genreid', 'data'),
        Output('genreprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url','search')
    ]
)
def genreprofile_populategenres(pathname, urlsearch):
    if pathname == '/genres/genre_management_profile':
        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]

        if create_mode == 'add':
            genreid = 0
            deletediv = 'd-none'
        else:
            genreid = int(parse_qs(parsed.query)['id'][0])
            deletediv= ''

        return [genreid, deletediv]
    else:
        raise PreventUpdate

        
@app.callback(
    [
        # dbc.Alert Properties
        Output('genreprofile_alert', 'color'),
        Output('genreprofile_alert', 'children'),
        Output('genreprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('genreprofile_successmodal', 'is_open'),
        Output('genreprofile_successmodalheader', 'children')
    ],
    [
        # For buttons, the property n_clicks 
        Input('genreprofile_submit', 'n_clicks')
    ],
    [
        # The values of the fields are States 
        # They are required in this process but they 
        # do not trigger this callback
        State('genreprofile_title', 'value'),
        State('url', 'search'),
        State('genreprofile_genreid', 'data'),
        State('genreprofile_deleteind', 'value')
    ]
)
def genreprofile_saveprofile(submitbtn, title, urlsearch, genreid, delete):
    ctx = dash.callback_context
    # The ctx filter -- ensures that only a change in url will activate this callback
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'genreprofile_submit' and submitbtn:
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
                alert_text = 'Check your inputs. Please supply the genre title.'
        
            else: # all inputs are valid
                # Add the data into the db
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO genres (genre_name,
                            genre_delete_ind)
                        VALUES (%s, %s)
                    '''
                    values = [title, False]
                    msg = "Save Success"
                elif create_mode == 'edit':
                    sql = '''
                        UPDATE genres 
                        SET 
                            genre_name = %s,
                            genre_delete_ind = %s
                        WHERE
                            genre_id = %s
                    '''
                    values = [title, bool(delete), genreid]
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

@app.callback(
    [
        Output('genreprofile_title', 'value'),
    ],
    [
        Input('genreprofile_genreid', 'modified_timestamp')
    ],
    [
        State('genreprofile_genreid', 'data'),
    ]
)
def genreprofile_loadprofile(timestamp, genreid):
    if genreid: # check if genreid > 0

        # Query from db
        sql = """
            SELECT genre_name
            FROM genres
            WHERE genre_id = %s
        """
        values = [genreid]
        col = ['genrename']

        df = getDataFromDB(sql, values, col)

        genrename = df['genrename'][0]
        # Our dropdown list has the genreids as values then it will 
        # display the correspoinding labels

        return [genrename]

    else:
        raise PreventUpdate


@app.callback(
    [
        Output('genreprofile_submit', 'color'),
    ],
    [
        Input('genreprofile_deleteind', 'value')
    ],
    [
        
    ]
)
def genreprofile_deletwarn(delete):
    if delete:
        return ['danger']
    else:
        return ['primary']