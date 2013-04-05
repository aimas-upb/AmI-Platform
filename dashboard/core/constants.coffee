define [], () ->
    Constants =
        UNAUTHORIZED_EXCEPTION: '__UNAUTHORIZED__'
        DELAY_WIDGET: 'uberdelay'
        ROOM_X: 5000
        ROOM_Y: 9000
        BLACK: "#000000"
        RED: "#FF0000"
        GREEN: "#008000"
        BLUE: "#0000FF"
        PURPLE: "#800080"
        ORANGE: "#FFA500"
        FUCHSIA: "#FF00FF"

    window.Constants = Constants
    return Constants