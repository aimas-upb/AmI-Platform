#include <stdio.h>

void SaveImageToFile(unsigned char *img, int width, int height) {
    unsigned char bmpfileheader[14] = {'B','M', 0,0,0,0, 0,0, 0,0, 54,0,0,0};
    unsigned char bmpinfoheader[40] = {40,0,0,0, 0,0,0,0, 0,0,0,0, 1,0, 24,0};
    unsigned char bmppad[3] = {0,0,0};
    unsigned int filesize = 3 * width * height;
    unsigned int i;

    // double word. file size
    bmpfileheader[ 2] = (unsigned char)(filesize );
    bmpfileheader[ 3] = (unsigned char)(filesize>> 8);
    bmpfileheader[ 4] = (unsigned char)(filesize>>16);
    bmpfileheader[ 5] = (unsigned char)(filesize>>24);

    bmpinfoheader[ 4] = (unsigned char)( width	);
    bmpinfoheader[ 5] = (unsigned char)( width>> 8);
    bmpinfoheader[ 6] = (unsigned char)( width>>16);
    bmpinfoheader[ 7] = (unsigned char)( width>>24);
    bmpinfoheader[ 8] = (unsigned char)( height );
    bmpinfoheader[ 9] = (unsigned char)( height>> 8);
    bmpinfoheader[10] = (unsigned char)( height>>16);
    bmpinfoheader[11] = (unsigned char)( height>>24);


    FILE *f = fopen("/home/ami/AmI-Platform/image.bmp","w");
    fwrite(bmpfileheader,1,14,f);
    fwrite(bmpinfoheader,1,40,f);
    for(i=0; i<height; i++)
    {
        fwrite(img + (3 * width * (height-1-i)), 3, width, f);
    }
    fclose(f);
}

