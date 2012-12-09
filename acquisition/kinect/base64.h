#ifndef __BASE_64__
#define __BASE_64__

#include<stdlib.h>

void base64_init();
void base64_done();

char *base64_encode(const char *data,
                    size_t input_length,
                    size_t *output_length);
                    
char *base64_decode(const char *data,
                    size_t input_length,
                    size_t *output_length);

#endif