#include <stdio.h>
#include <stdlib.h>

#include "context.h"

char* get_context() {
	char* buffer = (char*) malloc(100 * sizeof(char));
	FILE *f = fopen("/tmp/context", "rt");
	if (!f) {
		snprintf(buffer, 100, "default");
	} else {
		fscanf(f, "%s", buffer);
		fclose(f);
	}

	return buffer;
}