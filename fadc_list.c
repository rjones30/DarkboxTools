/*************************************************************************
 *
 *  fadc_list.c - Library of routines for the user to write for
 *                readout and buffering of events from JLab FADC using
 *                a Linux VME controller.
 *
 */


/* Event Buffer definitions */
#define MAX_EVENT_POOL     400
#define MAX_EVENT_LENGTH   1024*34      /* Size in Bytes */

/* Define Interrupt source and address */
#define TIR_SOURCE
#define TIR_ADDR 0x0ed0
/* TIR_MODE:  0 : interrupt on trigger,
              1 : interrupt from Trigger Supervisor signal
              2 : polling for trigger
              3 : polling for Trigger Supervisor signal  */

#define TIR_MODE 2

#include "linuxvme_list.c"     /* source required for CODA */
#include "fadcLib.h"           /* library of FADC250 routines */
#include "f1tdcLib.h"          /* library of f1tdc routines */
#include "vmeDSClib.h"         /* library of routines for the vmeDSC */

#include "/usr/local/coda/2.6.1/common/include/BankTools.h"
#include "dmaBankTools.h"


/*  FADC Library Variables */
extern int fadcA32Base;
int FA_SLOT;
extern int fadcID[20];

/* F1TDC Specifics */
unsigned int F1_ADDR = 0x800000;

extern int f1tdcA32Base;
extern int f1ID[20];
int F1_SLOT;


unsigned int MAXFADCWORDS = 0;

int use_tdc = 1;

int ich;



/* function prototype */
void rocTrigger(int arg);

void
rocDownload()
{

  unsigned short iflag;
  int stat;


  f1tdcA32Base = 0x0a000000;
  fadcA32Base  = 0x09000000;
    
  /* Setup Address and data modes for DMA transfers
   *   
   *  vmeDmaConfig(addrType, dataType, sstMode);
   *
   *  addrType = 0 (A16)    1 (A24)    2 (A32)
   *  dataType = 0 (D16)    1 (D32)    2 (BLK32) 3 (MBLK) 4 (2eVME) 5 (2eSST)
   *  sstMode  = 0 (SST160) 1 (SST267) 2 (SST320)
   */

  /* DMA initialization. F1TDC does not support 2eSST */
  if(use_tdc) vmeDmaConfig(2,3,0);
  else vmeDmaConfig(2,5,1);
  


  /***************************************
   * FADC Setup 
   ***************************************/

  unsigned short thr = 10;
  unsigned short pedestal[16] ={152, 146, 165, 134, 176, 127, 154, 153, 151, 152, 139, 162, 149, 113, 117, 388};


  iflag = 0xea00;    /*  SDC Board address  */
  iflag |= 1<<0;     /*  Front panel sync-reset  */
  iflag |= 1<<1;     /*  Front Panel Input trigger source  */
  iflag |= 1<<4;     /* Front Panel 250MHz Clock source */
  //  iflag |= 0<<4;  /* Internal 250MHz Clock source */

  printf("TEST iflag = 0x%x\n",iflag);

  faInit((unsigned int)(5<<19),0x0,1,iflag);

  /* Block size for the raw data. Assume 100 samples (400 ns window) */
  /* Block size for the raw data. Assume 1024 samples (4096 ns window) */
  MAXFADCWORDS = (1 + 2 + 512*16 + 2) + 2*32;

  
  FA_SLOT = fadcID[0];
  
  /* Set the internal DAC level (pedestals) */
  faSetDAC(FA_SLOT,3200,0);


  /*   Set All channel thresholds to 0   */
  /*   Threshold is computed from FADC cnt = 0  */

  faSetThreshold(FA_SLOT,0,0xffff);
  
  //  for(ich = 0; ich < 16; ich++){    
  //    printf("Threshold = %d %d\n",pedestal[ich]+thr,(1<<ich));    
  //    faSetThreshold(FA_SLOT,pedestal[ich]+thr,(1<<ich));
  //  }


  
  /*  Setup option 1 processing - RAW Window Data      <-- */
  /*        option 2            - RAW Pulse Data           */
  /*        option 3            - Integral Pulse Data      */
  /*  Setup 200 nsec latency (PL  = 50)                    */
  /*  Setup  80 nsec Window  (PTW = 20)                    */
  /*  Setup Pulse widths of 36ns (NSB(3)+NSA(6) = 9)       */
  /*  Setup up to 1 pulse processed                        */
  /*  Setup for both ADC banks(0 - all channels 0-15)      */


  //faSetProcMode(FA_SLOT,1,102,100,3,6,1,0);
  faSetProcMode(FA_SLOT,1,128,256,3,6,1,0);
  
  faStatus(FA_SLOT,0);

  faSDC_Config(1,0);
  faSDC_Status(0);


  faPrintDAC(FA_SLOT);
  faPrintThreshold(FA_SLOT);


  /* Bus errors to terminate block transfers (preferred) */
  faEnableBusError(FA_SLOT);

  /* Set the Block level */
  faSetBlockLevel(FA_SLOT,1);



  //****************************************
  //********   Discriminators **************
  //****************************************
  
  printf(" Initialize Discriminators \n");
  dscInit((unsigned int)(14<<19),0,1);
  
  dscSetPulseWidth(0,30,1);
  
  for(ich = 0; ich < 16; ich++){
    //dscSetThreshold(0,ich,100,TDCTRG);
    //dscSetThreshold(0,ich,30,TDCTRG);
    dscSetThreshold(0,ich,25,TDCTRG);
  }
  
  for(ich = 0; ich < 16; ich++){
    printf(" Disc1  %d  \n",dscGetThreshold(0,ich,TDC));
  }
  

  dscSetChannelMask(0,0xffff,TDCTRG);
  dscSetChannelORMask(0,0xffff,TDCTRG);
  
  dscTest(0,0);
  
  dscStatus(0,0);

  printf("rocDownload: User Download Executed\n");

} 


void
rocPrestart()
{

  /***************************************
   *   F1 TDC SETUP
   ***************************************/
  if(use_tdc){

    //    f1ConfigReadFile("/home/halld/micro/rol/cfg_bcal.dat");
    f1ConfigReadFile("/home/halld/micro/rol/uconn_tdc.dat");

    int iflag_f1 = 0;
    /*   iflag = 0x0ee0; /* SDC Board address */ 
    iflag_f1 = 0x0; /* no SDC */
    iflag_f1 |= 4;  /* read from file */
    /*   iflag |= 2;  /* Normal Resolution, Trigger matching */
    printf("F1 TDC iflag_f1 = 0x%x\n",iflag_f1);
    
    f1Init(F1_ADDR, 0x0, 1, iflag_f1);
    F1_SLOT = f1ID[0];
    
    printf(" SASCHA: F1TDC SLOT = %d \n",F1_SLOT);
    
    /*   Setup F1TDC */
    /*   f1Clear(F1_SLOT); */
    /*   f1SetConfig(F1_SLOT,2,0xff); */
    

    f1EnableData(F1_SLOT,0xff);
    f1SetBlockLevel(F1_SLOT,1);
    /*   f1DisableBusError(F1_SLOT); */
    f1EnableBusError(F1_SLOT);

    f1Clear(F1_SLOT);

  /* lock the resolution using the TIR output bit */
    tirIntOutput(1<<1);
    tirIntOutput(0);


    //    tidSetOutputPort(1,1,1,1);
    //    usleep(50000);
    //    tidSetOutputPort(0,0,0,0);

    /* wait for resolution to lock */
    usleep(50000);    

    f1Status(F1_SLOT,0);
  }

  printf("rocPrestart: User Prestart Executed\n");

}

void
rocGo()
{
  /*  Enable FADC */
  faEnable(FA_SLOT,0,0);

  taskDelay(1);
  
  /*  Send Sync Reset to FADC */
  /*     faSync(FA_SLOT); */
  faSDC_Sync();

  /* Interrupts/Polling enabled after conclusion of rocGo() */
}

void
rocEnd()
{

  /* FADC Disable */
  faDisable(FA_SLOT,0);

  /* FADC Event status - Is all data read out */
  faStatus(FA_SLOT,0);

  faReset(FA_SLOT,0);

  printf("rocEnd: Ended after %d events\n",tirGetIntCount());
  
}

void
rocTrigger(int arg)
{
  int ii, nwords;
  unsigned int datascan;

  BANKOPEN(4,BT_UI4,0);


  /* Insert trigger count  - Make sure bytes are ordered little-endian (LSWAP)*/
  *dma_dabufp++ = LSWAP(tirGetIntCount());

  BANKCLOSE;


  BANKOPEN(5,BT_UI4,0);

  /* Check for valid data here */
  for(ii=0;ii<100;ii++) 
    {
      datascan = faBready(FA_SLOT);
      if (datascan>0) 
	{
	  break;
	}
    }

  if(datascan>0) 
    {
      nwords = faReadBlock(FA_SLOT,dma_dabufp,MAXFADCWORDS,1);
    
      if(nwords < 0) 
	{
	  printf("ERROR: in transfer (event = %d), nwords = 0x%x\n", tirGetIntCount(),nwords);
	  *dma_dabufp++ = LSWAP(0xda000bad);
	} 
      else 
	{
	  dma_dabufp += nwords;
	  //printf("Readout FADC \n"); 
	}
    } 
  else 
    {
      printf("ERROR: Data not ready in event %d\n",tirGetIntCount());
      *dma_dabufp++ = LSWAP(0xda000bad);
    }

  *dma_dabufp++ = LSWAP(0x1234);

  BANKCLOSE;



  //***************************
  //******   F1 TDC  **********
  //***************************

  if(use_tdc){

    BANKOPEN(6,BT_UI4,0);
    
    /* Check for valid data here */
    for(ii=0;ii<100;ii++) 
      {
        datascan = f1Dready(F1_SLOT);
        if (datascan>0) 
          {
            break;
          }
      }

    if(datascan>0) 
      {
        nwords = f1ReadEvent(F1_SLOT,dma_dabufp,500,1);
        //printf(" Read out F1 TDC %d \n",nwords);

        if(nwords < 0) 
          {
            printf("ERROR: F1TDC transfer (nwords = %d)", nwords);
            *dma_dabufp++ = LSWAP(0xda000bad);
          } 
        else 
          {
            dma_dabufp += nwords;
          }
      } 
    else 
      {
        printf("ERROR: F1TDC data not ready in event %d\n");
        *dma_dabufp++ = LSWAP(0xda000bad);
      }
    *dma_dabufp++ = LSWAP(0xda0000ff); /* Event EOB */
    

    BANKCLOSE;
  }
}


/*
 * rocCleanup
 *  - Routine called just before the library is unloaded.
 */


void
rocCleanup()
{

  /*
   * Perform a RESET on all FADC250s.
   *   - Turn off all A32 (block transfer) addresses
   */
  printf("%s: Reset all FADCs\n",__FUNCTION__);
  
  FA_SLOT = fadcID[0];
  faReset(FA_SLOT,1); /* Reset, and DO NOT restore A32 settings (1) */

}

