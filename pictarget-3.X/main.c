#include "mcc_generated_files/mcc.h"

#define FCY 4000000ULL
#include <libpic30.h>

#define MY_BUFFER_SIZE 40

unsigned char myBuffer[MY_BUFFER_SIZE];

void getData(int bytesToGet)
{
    unsigned int             numBytes;
    UART1_TRANSFER_STATUS status ;

    numBytes = 0;
    while( numBytes < MY_BUFFER_SIZE)
    {
        status = UART1_TransferStatusGet ( ) ;
        if (status & UART1_TRANSFER_STATUS_RX_FULL)
        {
            numBytes += UART1_ReadBuffer( myBuffer + numBytes, MY_BUFFER_SIZE - numBytes )  ;
            if(numBytes < bytesToGet)
            {
                continue;
            }
            else
            {
                break;
            }
        }
        else
        {
            continue;
        }
    }
}

void putData()
{
    unsigned int             numBytes;
    
    numBytes = 0;
    while( numBytes < MY_BUFFER_SIZE);
    {
        if( !(UART1_TRANSFER_STATUS_TX_FULL & UART1_TransferStatusGet()) )
        {
            UART1_Write(myBuffer[numBytes++]);
        }

        // Do something else...
    }
}
    
int main(void)
{
    SYSTEM_Initialize();
    UART1_Initialize();

    while (1)
    {
        getData(5);
        putData();
        __delay_ms(500);
    }

    return -1;
}
