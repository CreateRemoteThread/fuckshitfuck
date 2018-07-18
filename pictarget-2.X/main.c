#include "mcc_generated_files/mcc.h"
#include <xc.h>

#define FCY 8000000UL
#include <libpic30.h>
#include <stdio.h>

char c_in[128];

void fghettos(int charsize)
{
    int i = 0;
    while(i < charsize)
    {
        char c = UART1_Read();
        if(c == '\0')
        {
            continue;
        }
        printf("Got char %02x\r\n",c);
        if(c == '\r' || c == '\n')
        {
            continue;
        }
        else
        {
            c_in[i++] = c;
        }
    }
    c_in[i++] = '\0';
    return;
}

int main(void)
{
    SYSTEM_Initialize();
    UART1_Initialize();
    
    printf("test\r\n");
    
    while (1)
    {    
        fghettos(10);
        printf("hello [%s]\r\n",c_in);
    }

    return -1;
}
/**
 End of File
*/