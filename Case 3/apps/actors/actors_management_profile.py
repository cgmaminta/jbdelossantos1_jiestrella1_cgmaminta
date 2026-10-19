import datetime
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from urllib.parse import parse_qs, urlparse

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [
        dcc.Store(id='actorprofile_actorid', storage_type='memory', data=0),

        html.H2('Actor Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='actorprofile_alert', is_open=False), # For feedback / error messages

        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("First Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text',
                                id='actorprofile_fname',
                                placeholder="First Name"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Last Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text',
                                id='actorprofile_lname',
                                placeholder="Last Name"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                html.Div(
                    [
                        dbc.Checklist(
                            id='actorprofile_deleteind',
                            options=[dict(value=1, label="Mark as Deleted")],
                            value=[]
                        )
                    ],
                    id='actorprofile_deletediv'
                )
            ]
        ),

        dbc.Button(
            'Submit',
            id='actorprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),

        dbc.Modal( # Modal = dialog box; feedback for successful saving/updating.
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    id='actorprofile_modalbody' # Target for dynamic success message
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/actors/actors_management' # Navigation back to actors management
                    )
                )
            ],
            centered=True,
            id='actorprofile_successmodal',
            backdrop='static'
        )
    ]
)


# Callback 1: Check mode (add/edit) and set store data & deletediv visibility
@app.callback(
    [
        Output('actorprofile_actorid', 'data'),
        Output('actorprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def actorprofile_setmode(pathname, urlsearch):
    if pathname == '/actors/actors_management_profile':
        parsed = urlparse(urlsearch)
        query_dict = parse_qs(parsed.query)
        create_mode = query_dict.get('mode', [None])[0]

        if create_mode == 'add':
            actorid = 0
            deletediv = 'd-none'
        else:
            actorid = int(query_dict.get('id', [0])[0])
            deletediv = ''

        return [actorid, deletediv]
    else:
        raise PreventUpdate


# Callback 2: Populate actor profile fields when editing
@app.callback(
    [
        Output('actorprofile_fname', 'value'),
        Output('actorprofile_lname', 'value')
    ],
    [
        Input('actorprofile_actorid', 'modified_timestamp')
    ],
    [
        State('actorprofile_actorid', 'data')
    ]
)
def actorprofile_loadprofile(timestamp, actorid):
    if actorid: # check if actorid > 0
        sql = """
            SELECT actor_fname, actor_lname
            FROM actors
            WHERE actor_id = %s
        """
        values = [actorid]
        col = ['fname', 'lname']

        df = getDataFromDB(sql, values, col)

        fname = df['fname'][0]
        lname = df['lname'][0]

        return [fname, lname]
    else:
        raise PreventUpdate


# Callback 3: Save profile with duplicate validation and trigger success modal with dynamic message
@app.callback(
    [
        # dbc.Alert Properties
        Output('actorprofile_alert', 'color'),
        Output('actorprofile_alert', 'children'),
        Output('actorprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('actorprofile_successmodal', 'is_open'),
        Output('actorprofile_modalbody', 'children')
    ],
    [
        Input('actorprofile_submit', 'n_clicks')
    ],
    [
        State('actorprofile_fname', 'value'),
        State('actorprofile_lname', 'value'),
        State('url', 'search'),
        State('actorprofile_actorid', 'data'),
        State('actorprofile_deleteind', 'value')
    ]
)
def actorprofile_saveprofile(submitbtn, fname, lname, urlsearch, actorid, delete):
    ctx = dash.callback_context

    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'actorprofile_submit' and submitbtn:

            parsed = urlparse(urlsearch)
            create_mode = parse_qs(parsed.query).get('mode', [None])[0]

            # Set default outputs
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            msg = ''

            # Input Validations
            if not fname or not fname.strip():
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the actor first name.'
                return [alert_color, alert_text, alert_open, modal_open, msg]
            elif not lname or not lname.strip():
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the actor last name.'
                return [alert_color, alert_text, alert_open, modal_open, msg]
            else:
                fname_clean = fname.strip()
                lname_clean = lname.strip()

                if create_mode == 'add':
                    # Check Duplicate Input for Add Mode
                    check_sql = """
                        SELECT actor_id 
                        FROM actors 
                        WHERE LOWER(actor_fname) = LOWER(%s) 
                          AND LOWER(actor_lname) = LOWER(%s)
                          AND actor_delete_ind = False
                    """
                    duplicate_df = getDataFromDB(check_sql, [fname_clean, lname_clean], ['actor_id'])

                    if not duplicate_df.empty:
                        alert_open = True
                        alert_color = 'warning'
                        alert_text = f"The actor '{fname_clean} {lname_clean}' already exists."
                        return [alert_color, alert_text, alert_open, modal_open, msg]

                    sql = """
                        INSERT INTO actors (actor_fname, actor_lname, actor_delete_ind, actor_modified_date)
                        VALUES (%s, %s, %s, NOW())
                    """
                    values = [fname_clean, lname_clean, False]
                    msg = "Actor Added! Success! Click Proceed to go back to Actors Management Page."

                elif create_mode == 'edit':
                    # Check Duplicate Input for Edit Mode
                    check_sql = """
                        SELECT actor_id 
                        FROM actors 
                        WHERE LOWER(actor_fname) = LOWER(%s) 
                          AND LOWER(actor_lname) = LOWER(%s)
                          AND actor_delete_ind = False
                          AND actor_id != %s
                    """
                    duplicate_df = getDataFromDB(check_sql, [fname_clean, lname_clean, actorid], ['actor_id'])

                    if not duplicate_df.empty:
                        alert_open = True
                        alert_color = 'warning'
                        alert_text = f"The actor '{fname_clean} {lname_clean}' already exists."
                        return [alert_color, alert_text, alert_open, modal_open, msg]

                    sql = """
                        UPDATE actors
                        SET
                            actor_fname = %s,
                            actor_lname = %s,
                            actor_delete_ind = %s,
                            actor_modified_date = %s
                        WHERE
                            actor_id = %s
                    """
                    values = [fname_clean, lname_clean, bool(delete), datetime.datetime.now(), actorid]
                    msg = "Update Success! Click Proceed to go back to the Actors Management Page."

                else:
                    raise PreventUpdate

                modifyDB(sql, values)
                modal_open = True

                return [alert_color, alert_text, alert_open, modal_open, msg]

        else:
            raise PreventUpdate
    else:
        raise PreventUpdate