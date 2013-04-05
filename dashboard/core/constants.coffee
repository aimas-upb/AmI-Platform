define [], () ->
    Constants =
        UNAUTHORIZED_EXCEPTION: '__UNAUTHORIZED__'
        DELAY_WIDGET: 'uberdelay'
        BLACK: "#000000"
        WHITE: "#FFFFFF"
        RED: "#FF0000"
        GREEN: "#008000"
        BLUE: "#0000FF"
        PURPLE: "#800080"
        ORANGE: "#FFA500"
        FUCHSIA: "#FF00FF"
        SECOND: 1000

    window.Constants = Constants
    return Constants