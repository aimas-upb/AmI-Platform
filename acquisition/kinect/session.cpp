#include <stdlib.h>
#include "session.h"
#include "ami_environment.h"

char* gen_random(const int len)
{
    int i;
    char* s = (char*)malloc(len * sizeof(char));
    static const char alphanum[] = "0123456789"\
                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"\
                                   "abcdefghijklmnopqrstuvwxyz";
    for (i=0; i<len; i++)
        s[i] = alphanum[rand() % (sizeof(alphanum)-1)];
    s[len] = 0;
    return s;
}

string generateSessionIdFromPlayerId(XnUserID player) {
    string result;

    const int HASH_LEN = 16;
    const int MAX_PLAYER_LEN = 3;

    char* playerID = (char*)malloc(MAX_PLAYER_LEN * sizeof(char));
    snprintf(playerID, MAX_PLAYER_LEN, "%d", player);
    const char* sensorID = getSensorID();

    int len = strlen(sensorID) + strlen(playerID) + HASH_LEN  + strlen("__0");
    char *sessionID = (char*) malloc(len * sizeof(char));

    snprintf(sessionID, len, "%s_%s_%s", sensorID, playerID, gen_random(HASH_LEN));

    result = string(sessionID);
    free(sessionID);

    return result;
}
