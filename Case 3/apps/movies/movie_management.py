import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html  
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Movies'), # Page Header
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
                                    "Add Movie",
                                    href='/movies/movie_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of movies
                            [
                                html.H4('Find Movies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='movie_titlefilter',
                                                        placeholder='Movie Title'
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
                                            id='movie_deleted',
                                            options= [dict(value=1, label="Show Deleted")],
                                            value=[] 
                                        )
                                    ], 
                                    id='movie_deletediv'
                                ),
                                html.Div(
                                    "Table with movies will go here.",
                                    id='movie_movielist'
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
        Output('movie_movielist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('movie_titlefilter', 'value'),
        Input('movie_deleted', 'value'),
    ],
)
def updateRecordsTable(pathname, titlefilter, deleted):
    
    if pathname == '/movies/movie_management':
        sql = """ SELECT 
            m.movie_name, 
            g.genre_name, 
            c.country_name,
            CONCAT(a.actor_fname,' ', a.actor_lname) AS actor_name,
            to_char(movie_release_date, 'DD Mon YYYY'),
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, m.movie_release_date))::INT AS movie_age,
            movie_id
        FROM movies m
            INNER JOIN genres g ON m.genre_id = g.genre_id
            LEFT JOIN countries c ON m.country_id = c.country_id
            LEFT JOIN actors a ON m.actor_id = a.actor_id
        WHERE 1=1
        """
        val = []

        if not deleted:
            sql+= """ AND NOT m.movie_delete_ind """

        if titlefilter:
            sql += """ AND m.movie_name ilike %s"""
            val += [f'%{titlefilter}%']

        col = ["Movie Title", "Genre", "Country of Origin", "Lead Actor","Release Date", "Movie Age (Years)", 'id']

        df = getDataFromDB(sql, val, col)

        #print(df)

        editButtons = []
        for movie_id in df['id']:
            editButtons += [
                html.Div(
                    dbc.Button("Edit", color='warning', size='sm', 
                            href = f'/movies/movie_management_profile?mode=edit&id={movie_id}'),
                    className='text-center'
                )
            ]
        
        df['Action'] = editButtons
        
        # we don't want to display the 'id' column -- let's exclude it
        df = df[['Movie Title', 'Genre', "Country of Origin", "Lead Actor",'Release Date', "Movie Age (Years)", 'Action']]

        movie_table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')

        #print(movie_table)
    else:
        raise PreventUpdate

    #movie_table = [] brah bakit may ganto
    
    return [movie_table]