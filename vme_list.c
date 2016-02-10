/*************************************************************************
 *
 *  vme_list.c - Library of routines for readout and buffering of 
 *                events using a JLAB Trigger Interface (TI) with 
 *                a Linux VME controller.
 *
 */

/* Event Buffer definitions */
#define MAX_EVENT_POOL     400
#define MAX_EVENT_LENGTH   1024*10      /* Size in Bytes */

/* Define Interrupt source and address */
#define TIR_SOURCE
#define TIR_ADDR 0x0ed0
/* TIR_MODE:  0 : interrupt on trigger,
              1 : interrupt from Trigger Supervisor signal
              2 : polling for trigger
              3 : polling for Trigger Supervisor signal  */
#define TIR_MODE 2

#include "linuxvme_list.c" /* source required for CODA */
#include "usrstrutils.c"   /* helper routines to pass data from mSQL to ROC */

/* Globals to be filled by usrstrutils */
int string1=0, string2=0; /* defined when string is present in CODA database */
int ps1=0,ps2=0,ps3=0,ps4=0,ps5=0,ps6=0,ps7=0,ps8=0; /* defined in "ffile" */

/* function prototype */
void rocTrigger(int arg);

void
rocDownload()
{

  /* Setup Address and data modes for DMA transfers
   *   
   *  vmeDmaConfig(addrType, dataType, sstMode);
   *
   *  addrType = 0 (A16)    1 (A24)    2 (A32)
   *  dataType = 0 (D16)    1 (D32)    2 (BLK32) 3 (MBLK) 4 (2eVME) 5 (2eSST)
   *  sstMode  = 0 (SST160) 1 (SST267) 2 (SST320)
   */
  vmeDmaConfig(2,5,1); 

  /* Initialize usrstrutils */
  init_strings();
  string1 = getflag("string");
  string2 = getflag("string2");

  printf("usrstrutils configuration:\n");
  printf("\tstring1 = %d\n\tstring2 = %d\n",string1,string2);

  printf("rocDownload: User Download Executed\n");

}

void
rocPrestart()
{
  unsigned short iflag;
  int stat;

  /* Check ffile for changes (usrstrutils) 
     Useful for items that may change without re-download (e.g. prescale factors) */
  init_strings();
  ps1 = getint("ps1");
  printf("usrstrutils configuration:\n");
  printf("\tps1 = %d\n",ps1);

  /* Program/Init VME Modules Here */

  printf("rocPrestart: User Prestart Executed\n");

}

void
rocGo()
{
  /* Enable modules, if needed, here */

  /* Interrupts/Polling enabled after conclusion of rocGo() */
}

void
rocEnd()
{

  printf("rocEnd: Ended after %d events\n",tirGetIntCount());
  
}

void
rocTrigger(int arg)
{
  int ii;

  /* Example: Raise the 0th (1<<0) and 2nd (1<<2) output level on the TI */
  tirIntOutput(1<<0 | 1<<2);

  /* Insert some data here - Make sure bytes are ordered little-endian (LSWAP)*/
  *dma_dabufp++ = LSWAP(0xda000022);
  for(ii=0; ii<20; ii++) 
    {
      *dma_dabufp++ = LSWAP(ii);
    }
  *dma_dabufp++ = LSWAP(0xda0000ff);

  /* Drop all output levels on the TI */
  tirIntOutput(0);

}
