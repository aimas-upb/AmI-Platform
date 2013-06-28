#include <stdlib.h>
#include "session.h"

string generateSessionIdFromPlayerId(XnUserID playerId) {
    string result;

    const int HASH_LEN = 16;
    const int MAX_PLAYER_LEN = 3;

    char* playerID = (char*)malloc(MAX_PLAYER_LEN * sizeof(char));
    snprintf(playerID, MAX_PLAYER_LEN, "%d", player);
    char* sensorID = getSensorID();

    int len = strlen(sensorID) + strlen(playerID) + HASH_LEN  + strlen("__0");
    char *sessionID = (char*) malloc(len * sizeof(char));

    snprintf(sessionID, len, "%s_%s_%s", sensorID, playerID, gen_random(HASH_LEN));

    result = string(sessionID);
    free(sessionID);

    return result;
}
