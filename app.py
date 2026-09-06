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
    [
        dbc.Card(
            [
                dbc.CardHeader("This is the header"),
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
                                dbc.Label("Process"),
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
                        dbc.Button("Calculate!", id='btn_calculate', color='primary', n_clicks=0),
                        html.Div(id='output_area')
                    ]
                ),
                dbc.CardFooter("This is the footer"),
            ],
            style={"width": "18rem"},
        )
    ],
    style={
        "justifyContent": "center",
        "alignItems": "center",
        "display":"flex",
        "minHeight":"100vh",
    },
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
