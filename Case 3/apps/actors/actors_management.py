import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html  
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Actors'), # Page Header
        html.Hr(),
        dbc.Card( # Card Container
            [
                dbc.CardHeader( # Define Card Header
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody( # Define Card Contents
                    [
                        html.Div( # Add Actor Btn
                            [
                                dbc.Button(
                                    "Add Actor",
                                    href='/actors/actors_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of actors
                            [
                                html.H4('Find Actors'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='actor_namefilter',
                                                        placeholder='Actor Name'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                        )
                                    )
                                ),
                                html.Div(
                                    [
                                        dbc.Checklist(
                                            id='actor_deleted',
                                            options=[dict(value=1, label="Show Deleted")],
                                            value=[] 
                                        )
                                    ], 
                                    id='actor_deletediv'
                                ),
                                html.Div(
                                    "Table with actors will go here.",
                                    id='actor_actorlist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    [
        Output('actor_actorlist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('actor_namefilter', 'value'),
        Input('actor_deleted', 'value'),
    ],
)
def updateRecordsTable(pathname, namefilter, deleted):
    
    if pathname == '/actors/actors_management':
        # SQL selection using actor_fname and actor_lname
        sql = """ SELECT 
                    actor_fname, 
                    actor_lname, 
                    actor_id
                FROM actors
                WHERE 1=1
        """
        val = []

        if not deleted:
            sql += """ AND NOT actor_delete_ind """

        if namefilter:
            sql += """ AND (actor_fname ILIKE %s OR actor_lname ILIKE %s) """
            val += [f'%{namefilter}%', f'%{namefilter}%']

        sql += """ ORDER BY actor_lname, actor_fname ASC """

        col = ["First Name", "Last Name", 'id']

        df = getDataFromDB(sql, val, col)

        editButtons = []
        for actor_id in df['id']:
            editButtons += [
                html.Div(
                    dbc.Button(
                        "Edit", 
                        color='warning', 
                        size='sm', 
                        href=f'/actors/actors_management_profile?mode=edit&id={actor_id}'
                    ),
                    className='text-center'
                )
            ]
        
        df['Action'] = editButtons
        
        # Exclude 'id' column from display
        df = df[['First Name', 'Last Name', 'Action']]

        actor_table = dbc.Table.from_dataframe(
            df, 
            striped=True, 
            bordered=True,
            hover=True, 
            size='sm'
        )

    else:
        raise PreventUpdate

    return [actor_table]