define ['cs!core/constants'], (Constants) ->
    # This file contains core Constants specific to the Mozaic Core.
    # To add project specific constants create a new constants file and extend window.Constants

    DashboardConstants =
        BLACK: "#000000"
        WHITE: "#FFFFFF"
        RED: "#FF0000"
        GREEN: "#008000"
        BLUE: "#0000FF"
        PURPLE: "#800080"
        ORANGE: "#FFA500"
        FUCHSIA: "#FF00FF"

        SECOND: 1000
        POSITION_SHAPE: 'CIRCLE'
        DRAW_LINES: false

    _.extend(Constants, DashboardConstants)
