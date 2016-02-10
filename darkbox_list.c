/*************************************************************************
 *
 *  darkbox_list.c - Library of routines for readout and buffering of 
 *                   events using a JLAB Trigger Interface (TI) with 
 *                   a Linux VME controller, a JLab VME discriminator,
 *                   and a CAEN V792 integrating ADC.
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

#define ADC_ID 0
#define ADC_ADDR 0x00380000
#define MAX_ADC_DATA 36

#include "linuxvme_list.c" /* source required for CODA */
#include "usrstrutils.c"   /* helper routines to pass data from mSQL to ROC */
#include "vmeDSClib.h"     /* library of routines for the vmeDSC */
#include "c792Lib.h"       /* library of routines for the CAEN v792 */

#include "/usr/local/coda/2.6.1/common/include/BankTools.h"
#include "dmaBankTools.h"

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

  //vmeDmaConfig(2,5,1); 
  vmeDmaConfig(1,3,0); 

  /* Initialize usrstrutils */
  init_strings();
  string1 = getflag("string");
  string2 = getflag("string2");

  printf("usrstrutils configuration:\n");
  printf("\tstring1 = %d\n\tstring2 = %d\n",string1,string2);

  //****************************************
  //********   Discriminators **************
  //****************************************
  
  printf(" Initialize Discriminators \n");

  int slot = 4;
  vmeDSCInit((unsigned int)(slot<<19),0,1,0);
  
  vmeDSCSetDelay(0,0,2);        // TRG output pulse delay
  vmeDSCSetPulseWidth(0,15,1);  // TDC pulse width
  vmeDSCSetPulseWidth(0,25,2);  // TRG pulse width
  
  int ich;
  for(ich = 0; ich < 16; ich++){
    vmeDSCSetThreshold(0,ich,150,TDCTRG);
    vmeDSCSetTRGOut(0,ich,250,0);
  }
  
  for(ich = 0; ich < 16; ich++){
    printf(" Disc1  %d  \n",vmeDSCGetThreshold(0,ich,TDC));
  }
  

  vmeDSCSetChannelMask(0,0xffff,TDCTRG);
  vmeDSCSetChannelORMask(0,0xffff,TDCTRG);
  
  vmeDSCSetTestInput(0,0);
  
  vmeDSCStatus(0,0);

  c792Init(ADC_ADDR,0,1,0);

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
  /* Setup ADCs (no sparcification, enable berr for block reads) */
  c792Sparse(ADC_ID,0,0);
  c792Clear(ADC_ID);
  c792EnableBerr(ADC_ID);

  c792Status(ADC_ID,0,0);
  

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
  int ii, status, dma, count;
  int nwords;
  unsigned int datascan, tirval, vme_addr;
  int length,size;
  int itimeout=0;

/*   tirIntOutput(2); */

  BANKOPEN(4,BT_UI4,0);

  *dma_dabufp++ = LSWAP(tirGetIntCount()); /* Insert Event Number */

  BANKCLOSE;

  /* Check if an Event is available */

  BANKOPEN(5,BT_UI4,0);

  while(itimeout<1000)
    {
      itimeout++;
      status = c792Dready(ADC_ID);
      if(status>0) break;
    }
  if(status > 0) 
    {
      if(tirGetIntCount() %1000==0)
	{
	  printf("itimeout = %d\n",itimeout);
	  c792PrintEvent(ADC_ID,0);
	}
      else
	{
/* 	  nwords = c792ReadEvent(ADC_ID,dma_dabufp); */
	  nwords = c792ReadBlock(ADC_ID,dma_dabufp,MAX_ADC_DATA);
	  if(nwords<=0) 
	    {
	      logMsg("ERROR: ADC Read Failed - Status 0x%x\n",nwords,0,0,0,0,0);
	      *dma_dabufp++ = 0xda000bad;
	      c792Clear(ADC_ID);
	    } 
	  else 
	    {
	      dma_dabufp += nwords;
	    }
	}
    }
  else
    {
      logMsg("ERROR: NO data in ADC  datascan = 0x%x, itimeout=%d\n",status,itimeout,0,0,0,0);
      c792Clear(ADC_ID);
    }

  *dma_dabufp++ = LSWAP(0xd00dd00d); /* Event EOB */

  BANKCLOSE;

  /* Drop all output levels on the TI */
/*    tirIntOutput(0);  */

}
