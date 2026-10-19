import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback 
from dash.exceptions import PreventUpdate
from utilities import generateFibonacci, getFactorial

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

app.title = "My First Dash App"


# App Layout
app.layout = html.Div(
    style={
            "justifyContent": "center",
            "alignItems": "center",
            "display":"flex",
            "flexDirection": "column", # Makes header on top, cards underneath
            "minHeight":"100vh",
            "gap":"2vw",
            "backgroundColor":"#FFF1D1",
            "padding":"0 4vw"
        },
    children=[
        html.Div(
            "Amazing Calculator",
            style={
                "color":"#E20B0B", 
                "fontSize":"50px", 
                "fontWeight":"bold",
                "fontFamily":"Helvetica, sans-serif",
                "width":"92vw", # Adjusts the width of the text Div so it aligns with the total width of the cards
                "textAlign":"left"}, 
        ),
        html.Div(
            "Select from three processes - getting its factorial, the numbers corresponding to the Fibonnaci Sequence, and its digital root.",
            style={
                "color":"#E20B0B", 
                "fontSize":"15px", 
                "fontStyle":"italic",
                "fontFamily":"Helvetica, sans-serif",
                "width":"92vw", # Adjusts the width of the text Div so it aligns with the total width of the cards
                "textAlign":"left",
                "marginTop":"-2rem"
            },
        ),
        html.Div(
            style={
                "display":"flex",
                "flexDirection":"row",
                "gap":"2vw",
            },
            children=[
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                ["Calculator"],
                                style={"backgroundColor":"#E20B0B", 
                                       "color":"white",
                                       "fontWeight":"bold",
                                       "fontFamily":"Helvetica, sans-serif",}
                                ),
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            dbc.Label("Number"),
                                            dbc.Input(placeholder="Place a number here", type="text", id='num_input'),
                                            dbc.FormText("Negative numbers are not allowed."),
                                        ]
                                    ), 
                                    html.Div(
                                        [
                                            dbc.Label("Process", style={"marginTop":"15px"}),
                                            dbc.Select(
                                                id="process_select",
                                                options=[
                                                    {"label": "Get Factorial", "value": 1},
                                                    {"label": "Generate Fibonacci", "value": 2},
                                                    {"label": "Get Digital Root", "value": 3}
                                                ],
                                            ),
                                            dbc.FormText("Select an operation"),
                                        ]
                                    ), 
                                    dbc.Button(
                                        "Calculate!", id='btn_calculate', color='primary', n_clicks=0,
                                        style={"backgroundColor":"#2700C4", "marginLeft":"332px"}
                                    ),
                            
                                ]
                            ),
                            dbc.CardFooter("Made by Delos Santos, Estrella, and Maminta"),
                        ],
                        style={"width": "30vw","height":"52vh"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardHeader(["Result"],
                                           style={"backgroundColor":"#E20B0B", 
                                                  "color":"white",
                                                  "fontWeight":"bold",
                                                  "fontFamily":"Helvetica, sans-serif"}),
                            dbc.CardBody(
                                [
                                html.Div(id='output_area')
                                ],
                            style = {
                                "display":"flex",
                                "justifyContent":"center",
                                "alignItems":"center",
                                "height":"100%"
                            }
                            ),
                            dbc.CardFooter("Hope you had fun calculating!")
                        ],
                        style={"width": "60vw","height":"52vh"}
                    ),
                ],
        ),
    ],
)

from utilities import generateFibonacci, getFactorial, digitalRoot

@callback(
    [
        Output('output_area', 'children'),
        Output('output_area', 'style')
    ],
    [
        Input('btn_calculate', 'n_clicks')
    ], 
    [
        State('num_input', 'value'), 
        State('process_select', 'value')
    ]
)
def calculateResults(btncalculate_clicks, num_input, process_select):
    if btncalculate_clicks > 0:
        try:
            num_input = float(num_input)
        except ValueError:
            return ["Words are not allowed", {"color": "red"}]
        except:
            return ["Unknown input, try again!", {"color": "red"}]

        if num_input % 1 > 0:
            return ["Integers only", {"color": "red"}]
        
        if num_input < 0:
            return ["No negative numbers",{ "color": "red"}]
            
        process_select = int(process_select)
        

        if process_select == 1:
            factorial_value = getFactorial(num_input)
            output_val =  f"The factorial is {int(factorial_value)}."

        elif process_select == 2:
            fib_sequence = generateFibonacci(num_input)
            fib_sequence_str = [str(i) for i in fib_sequence]
            output_val = f"We get the sequence {", ".join(fib_sequence_str)}" 

        elif process_select == 3:
            digroot = digitalRoot(num_input)
            output_val = f"The digital root of {int(num_input)} is {digroot}." 

        else:
            output_val = "Please select a process."

    else:
        raise PreventUpdate
    
    return [output_val, {"color": "black"}]

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050', autoraise=True)
    app.run()
