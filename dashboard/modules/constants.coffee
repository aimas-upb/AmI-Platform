define ['cs!core/constants'], (Constants) ->
    # This file contains core Constants specific to the Mozaic Core.
    # To add project specific constants create a new constants file and extend window.Constants

    DashboardConstants =
        BLACK: [0, 0, 0]
        WHITE: [255, 255, 255]
        RED: [128, 0, 0]
        GREEN: [0, 128, 0]
        BLUE: [0, 0, 128]
        PURPLE: [128, 0, 128]
        ORANGE: [255, 165, 0]
        FUCHSIA: [255, 0, 255]

        SECOND: 1000
        POSITION_SHAPE: 'CIRCLE'
        DRAW_LINES: false

    _.extend(Constants, DashboardConstants)
