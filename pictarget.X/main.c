
#pragma config JTAGEN = OFF
#pragma config GCP = OFF
#pragma config GWRP = OFF
#pragma config ICS = PGx1
#pragma config FWDTEN = OFF
#pragma config WINDIS = OFF
#pragma config FWPSA = PR32
#pragma config WDTPS = PS8192
 
#pragma config IESO = OFF
#pragma config FNOSC = FRCPLL
#pragma config OSCIOFNC = ON
#pragma config POSCMOD = NONE
#pragma config PLL96MHZ = ON
#pragma config PLLDIV = DIV2
#pragma config FCKSM = CSDCMD
#pragma config IOL1WAY = OFF
 
#pragma config WPFP = WPFP0
#pragma config SOSCSEL = IO
#pragma config WUTSEL = FST
#pragma config WPDIS = WPDIS
#pragma config WPCFG = WPCFGDIS
#pragma config WPEND = WPENDMEM
 
#pragma config DSWDTPS = DSWDTPS3
#pragma config DSWDTOSC = LPRC
#pragma config RTCOSC = LPRC
#pragma config DSBOREN = OFF
#pragma config DSWDTEN = OFF
 
 
#include <xc.h>
#define _XTAL_FREQ 16000000ULL
#define FOSC    (1600000ULL)
#define FCY     (FOSC/2)
#include <p24FJ64GB002.h>
#include <libpic30.h>
#include <stdio.h>
 
//END CONFIG
 
int main(void)
{
    TRISB &= !(1 << 0); //RB0 as Output PIN
    while(1)
    {
      PORTB |= 1;  // LED ON
      __delay_ms(1000); // 1 Second Delay
      PORTB &= ~1;  // LED OFF
      __delay_ms(1000); // 1 Second Delay
    }
    return 0;
}
