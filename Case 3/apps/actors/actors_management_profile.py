import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from urllib.parse import parse_qs, urlparse

from app import app
from apps.dbconnect import getDataFromDB, modifyDB 

layout = html.Div(
    [
        dcc.Store(id='actorprofile_toload', data=0),
        html.H2('Actor Details'),
        html.Hr(),
        dbc.Alert(id='actorprofile_alert', is_open=False),
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Actor Form')),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Label("First Name", width=2),
                                dbc.Col(
                                    dbc.Input(type="text", id="actor_fname", placeholder="First Name"),
                                    width=6
                                ),
                            ],
                            className="mb-3"
                        ),
                        dbc.Row(
                            [
                                dbc.Label("Last Name", width=2),
                                dbc.Col(
                                    dbc.Input(type="text", id="actor_lname", placeholder="Last Name"),
                                    width=6
                                ),
                            ],
                            className="mb-3"
                        ),
                        dbc.Row(
                            [
                                dbc.Label("Delete Actor?", width=2),
                                dbc.Col(
                                    dbc.Checklist(
                                        id='actor_removerecord',
                                        options=[{'label': "Mark as Deleted", 'value': 1}],
                                        value=[]
                                    ),
                                    width=6
                                )
                            ],
                            id='actor_removerecord_div',
                            className="mb-3"
                        )
                    ]
                )
            ]
        ),
        html.Br(),
        dbc.Button("Save", id="actor_savebtn", color="primary", className="me-2"),
        dbc.Button("Cancel", id="actor_cancelbtn", color="secondary", href="/actors/actors_management"),
    ]
)

# Populate Form on Load Mode
@app.callback(
    [
        Output('actor_fname', 'value'),
        Output('actor_lname', 'value'),
        Output('actorprofile_toload', 'data'),
        Output('actor_removerecord_div', 'style')
    ],
    [Input('url', 'pathname')],
    [State('url', 'search')]
)
def load_actor_profile(pathname, search):
    if pathname == '/actors/actors_management_profile':
        parsed = parse_qs(urlparse(search).query)
        mode = parsed.get('mode', [None])[0]

        if mode == 'edit':
            actor_id = parsed.get('id', [None])[0]
            # Updated column name to actor_lname
            sql = "SELECT actor_fname, actor_lname FROM actors WHERE actor_id = %s"
            df = getDataFromDB(sql, [actor_id], ['fname', 'lname'])

            return df['fname'][0], df['lname'][0], int(actor_id), {'display': 'flex'}
        else:
            return "", "", 0, {'display': 'none'}

    raise PreventUpdate


# Save with Duplicate Input Validation
@app.callback(
    [
        Output('actorprofile_alert', 'is_open'),
        Output('actorprofile_alert', 'children'),
        Output('actorprofile_alert', 'color')
    ],
    [Input('actor_savebtn', 'n_clicks')],
    [
        State('actor_fname', 'value'),
        State('actor_lname', 'value'),
        State('actor_removerecord', 'value'),
        State('actorprofile_toload', 'data'),
        State('url', 'search')
    ]
)
def save_actor(n_clicks, fname, lname, removerecord, actor_id, search):
    if n_clicks:
        if not fname or not lname:
            return True, "Please fill in all required fields.", "danger"

        fname_clean = fname.strip()
        lname_clean = lname.strip()

        # Duplicate Check with updated actor_lname column name
        dup_sql = """
            SELECT actor_id 
            FROM actors 
            WHERE LOWER(actor_fname) = LOWER(%s) 
              AND LOWER(actor_lname) = LOWER(%s)
              AND NOT actor_delete_ind
              AND actor_id != %s
        """
        dup_df = getDataFromDB(dup_sql, [fname_clean, lname_clean, actor_id], ['actor_id'])

        if not dup_df.empty:
            return True, f"An actor with the name '{fname_clean} {lname_clean}' already exists.", "warning"

        parsed = parse_qs(urlparse(search).query)
        mode = parsed.get('mode', [None])[0]
        delete_ind = 1 in removerecord if removerecord else False

        if mode == 'add':
            sql = """
                INSERT INTO actors (actor_fname, actor_lname, actor_delete_ind, actor_modified_date) 
                VALUES (%s, %s, %s, NOW())
            """
            modifyDB(sql, [fname_clean, lname_clean, False])
        elif mode == 'edit':
            sql = """
                UPDATE actors 
                SET actor_fname = %s, actor_lname = %s, actor_delete_ind = %s, actor_modified_date = NOW() 
                WHERE actor_id = %s
            """
            modifyDB(sql, [fname_clean, lname_clean, delete_ind, actor_id])

        return True, "Actor details saved successfully! You can now return to the list.", "success"

    raise PreventUpdate