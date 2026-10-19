from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from app import app
from apps import dbconnect as db



layout = html.Div(
    [
        html.H2('Reports'),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('View Reports')
                    ]
                ),
                dbc.CardBody( 
                    [
                        html.Div(
                            [
                                html.Div(
                                    dbc.Form(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Label("Country", width=1),
                                                    dbc.Col(
                                                        dcc.Dropdown(
                                                            id='report_countryfilter',
                                                            placeholder='Select Country',
                                                            searchable=True,
                                                            options = [],
                                                            multi = True
                                                        ),
                                                        width=5
                                                    )
                                                ],
                                                className='mb-3'
                                            ),
                                        ],
                                    )
                                ),
                                html.Div([
                                    dcc.Loading(
                                        id="reportbodyload",
                                        children=[
                                        dcc.Graph(id='reportbodyreceipts',)
                                      ],type="circle")
                                ],style={'width':'100%',"border": "3px #5c5c5c solid",} ),
                                html.Hr(),
                                html.H5('Number of movies and actors per genre and country.'),
                                html.Div(
                                    id='report_movielist'
                                ),
                                html.Hr(),
                                html.H5('Number of movies and actors per genre and language.'),
                                dbc.Form(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Label("Genre", width=1),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id='report_genrefilter',
                                                    placeholder='Select Genre',
                                                    searchable=True,
                                                    options = [],
                                                    multi = True
                                                ),
                                                width=5
                                            )
                                        ],
                                            className='mb-3'
                                            ),
                                    dbc.Row(
                                        [
                                        dbc.Label("Language", width=1),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='report_languagefilter',
                                                placeholder='Select Language',
                                                searchable=True,
                                                options = [],
                                                multi = True
                                            ),
                                            width=5
                                        )
                                        ],
                                        className='mb-3'
                                    ),
                                ]
                                ),
                                
                                html.Div(
                                    id='report_movielist2'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


#callback to populate dropdown options
@app.callback(
    [
        Output('report_countryfilter', 'options'),
        Output('report_genrefilter', 'options'),
        Output('report_languagefilter', 'options'),
        
    ],
    [
        Input('url', 'pathname'),
    ]
)
def moviehome_loadmovielist(pathname):
    if pathname == '/reports/report':
        sql = """ SELECT country_name as label, 
                    country_id as value
                FROM countries
                WHERE country_delete_ind = %s
            """
        columns = ['label', 'value']
        values = [False]
        dfsql = db.getDataFromDB(sql, values, columns)

        gsql = """ SELECT genre_name as label, 
                            genre_id as value
                        FROM genres
                        WHERE genre_delete_ind = %s
                    """
        gcolumns = ['label', 'value']
        gvalues = [False]
        gdfsql = db.getDataFromDB(gsql, gvalues, gcolumns)
                

        lsql = """ SELECT language_name as label, 
                                    language_id as value
                                FROM languages
                                WHERE language_delete_ind = %s
                            """
        lcolumns = ['label', 'value']
        lvalues = [False]
        ldfsql = db.getDataFromDB(lsql, lvalues, lcolumns)
        
        return [dfsql.to_dict('records'), gdfsql.to_dict('records'), ldfsql.to_dict('records')]
    
    else:
        raise PreventUpdate


#callback for figure and table
@app.callback(
    [
        Output('report_movielist', 'children'),
        Output('reportbodyreceipts', 'figure')
    ],
    [
        Input('url', 'pathname'),
        Input('report_countryfilter', 'value')
    ]
)
def moviehome_loadmovielist(pathname, filter_country):
    if pathname == '/reports/report':
        sql = """ SELECT g.genre_id,count(movie_name), country_name, genre_name, count(distinct(m.actor_id))
                FROM movies m
                    INNER JOIN genres g ON m.genre_id = g.genre_id
                    INNER JOIN actors a ON m.actor_id = a.actor_id
                    INNER JOIN countries c ON m.country_id = c.country_id
                WHERE movie_delete_ind = false
            """
        values = []
        
        if filter_country:
            sql += " AND c.country_id IN %s"
            values += [tuple(filter_country)]
        
        sql += """ Group By g.genre_id, country_name, genre_name
                    Order By country_name, genre_name
        """

        cols = ['ID', 'Number of Movies', 'Country Name', 'Genre', 'Number of Actors']

        df = db.getDataFromDB(sql, values, cols)

        
        df = df[['Genre','Country Name','Number of Movies','Number of Actors']]

        listofgenre = df["Genre"].unique().tolist()

    
        traces={}
        #setting up the values of the x-axis and y-axis of the Bar graph
        for genre in listofgenre:
            traces['tracebar_' + genre]=go.Bar(y=df[df["Genre"]==genre]["Number of Movies"],
                                    x=df[df["Genre"]==genre]["Country Name"],
                                    # orientation = 'h', #try to uncomment this line
                                    name=genre)
        
        #setting up the values of the x-axis and y-axis of the line chart
        for genre in listofgenre:
            traces['traceline_' + genre] = go.Scatter(y=df[df["Genre"]==genre]["Number of Actors"],
                                    x=df[df["Genre"]==genre]["Country Name"],
                                    # orientation = 'h', #try to uncomment this line
                                    mode = 'lines+markers',
                                    name=genre,
                                    yaxis='y2')
        
        #you can add more traces if you want!

        data=list(traces.values())

        #layout of the chart/graph
        layout = go.Layout(
                yaxis1={'categoryorder':'total ascending', 'title':"Number of Movies (y-axis for bar)",'range':[0,10]},
                yaxis2={'categoryorder':'total ascending', 'title':"Number of Actors (y-axis for line)",'overlaying':'y','side':'right', 'range':[0,10]},
                xaxis={'title':"Country", "mirror":False, "zeroline":True },
                height=500,
                width = 2000,
                margin={'b': 50,'t':20, 'l':175},
                hovermode='closest',
                autosize= False,
                dragmode = 'zoom',
                #bar graph
                barmode='stack', #try other barmodes (e.g. group)
                boxmode= "overlay",
                )


        figure3 = {'data':data, 'layout':layout }
        

        table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                hover=True, size='sm')
        
        if df.shape[0]:
            return [table, figure3]
        else:
            return [table, go.Figure()]
    else:
        raise PreventUpdate

#callback for table 2
@app.callback(
    [
        Output('report_movielist2', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('report_genrefilter', 'value'),
        Input('report_languagefilter', 'value'),
    ]
)
def loadmoviereport2(pathname, filter_genre, filter_language):
    if pathname == '/reports/report':
        sql = """ SELECT g.genre_id,count(movie_name), genre_name, language_name
                FROM movies m
                    INNER JOIN genres g ON m.genre_id = g.genre_id
                    INNER JOIN languages l ON m.language_id = l.language_id
                WHERE movie_delete_ind = false
            """
        values = []
        
        if filter_genre:
            sql += " AND g.genre_id IN %s"
            values += [tuple(filter_genre)]

        if filter_language:
            sql += " AND l.language_id IN %s"
            values += [tuple(filter_language)]
        
        sql += """ Group By g.genre_id, genre_name, language_name
                    Order By genre_name, language_name
        """

        cols = ['ID', 'Number of Movies', 'Genre', 'Language']

        df = db.getDataFromDB(sql, values, cols)

        
        df = df[['Language','Genre','Number of Movies']]

        table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                hover=True, size='sm')
        
        if df.shape[0]:
            return [table]
        else:
            return [table]
    else:
        raise PreventUpdate