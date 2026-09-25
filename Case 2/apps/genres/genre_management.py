import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html  
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Genres'), # Page Header
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
                        html.Div( # Add Movie Btn
                            [
                                # Add movie button will work like a 
                                # hyperlink that leads to another page
                                dbc.Button(
                                    "Add Genre",
                                    href='/genres/genre_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of movies
                            [
                                html.H4('Find Genres'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='genre_titlefilter',
                                                        placeholder='Genre Title'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with genres will go here.",
                                    id='genre_genrelist'
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
        Output('genre_genrelist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('genre_titlefilter', 'value'),
    ],
)
def updateRecordsTable(pathname, titlefilter):
    
    if pathname == '/genres/genre_management':
        sql = """ SELECT genre_name, genre_id
        FROM genres g
        WHERE NOT genre_delete_ind
        """
        val = []

        if titlefilter:
            sql += """ AND genre_name ilike %s"""
            val += [f'%{titlefilter}%']

        col = ["Genre Title", 'id']

        df = getDataFromDB(sql, val, col)

        #print(df)

        editButtons = []
        for movie_id in df['id']:
            editButtons += [
                html.Div(
                    dbc.Button("Edit", color='warning', size='sm', 
                            href = f'/genres/genre_management_profile?mode=edit&id={movie_id}'),
                    className='text-center'
                )
            ]
        
        df['Action'] = editButtons
        
        # we don't want to display the 'id' column -- let's exclude it
        df = df[['Genre Title', 'Action']]

        genre_table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')

    else:
        raise PreventUpdate

    
    return [genre_table]