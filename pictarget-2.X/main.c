#include "mcc_generated_files/mcc.h"
#include <xc.h>

#define FCY 8000000UL
#include <libpic30.h>
#include <stdio.h>

char c_in[128];

int main(void)
{
    // initialize the device
    SYSTEM_Initialize();
    // UART1_Initialize();
    
    printf("hello \r\n");

    int i = 0;
    
    while (1)
    {
        read(1,&c_in,120);
        for(;i < 128;i++)
        {
            if(c_in[i] == '\r' || c_in[i] == '\n')
            {
                c_in[i] = '\0';
                break;
            }
        }
        // c_in[0] = UART1_Read();
        printf("hello [%s]\r\n",c_in);

        __delay_ms(500);
        // Add your application code
    }

    return -1;
}
/**
 End of File
*/