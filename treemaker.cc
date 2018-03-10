//
// treemaker.cc - main program to read data in from an evio
//                event file produced by the readout of the
//                UConn darkbox data acquisition crate, and
//                save the results in a root tree.
// 
// authors: richard.t.jones at uconn.edu,
// version: november 12, 2015
//
// usage:
//	$ ./treemaker <input_file>.evt.0
//	$ root -l <input_file>.root
//	root> v792.Draw("q[0]")
//	root>
// 
// notes:
// 1) The input is a single evio file that is assumed to
//    end with the extension ".evio.N" which is named as the
//    only required command line argument.
// 2) The output is a root file created in the same
//    directory as the input file, and with the same name
//    with the extension ".evio.N" changed to ".root". This
//    file contains a tree named "v792" with a single leaf
//    variable q, which is an array of 32 elements that
//    contain the pulse integral for the 32 input channels
//    of the CAEN v792 charge-integrating adc.

#define TRIGGERED_BY_PULSER 1
#define MAX_EVENT_COUNT 1e30

#include <netinet/in.h>
#include <evioFileChannel.hxx>
#include <evioUtil.hxx>
#include <unistd.h>
#include <vector>

// root stuff
#include <TFile.h>
#include <TTree.h>
#include <TH1D.h>

int evtCount = 0;
int verbose_print = 0;

TFile *ROOTfile = 0;
TTree *v792 = 0;
int run_number = -1;
int event_number = -1;
double q[32];
int status = 99;

// prototypes
void analyzeEvent(evio::evioDOMTree &eventTree);
void analyzeBank(evio::evioDOMNodeP bankPtr);
void initRootTree(const char* filename);
bool event_passes_trigger();


int main(int argc, char **argv)
{
  if (argc == 1) {
     printf("Usage: treemaker <path_to_evio_file>\n");
     exit(1);
  }

  char filename[999];
  strncpy(filename, argv[1], 999);

  try {
    char fname[999],fname1[999];
    sprintf(fname, "%s", filename);
    //strtok(fname, "/");
    sprintf(fname1, "%s.root", strtok(fname, "."));
    initRootTree(fname1);
    TH1D *hnorm = new TH1D("hnorm", "laser pulser normalization",
                           512, 0, 4096.);
    
    std::cout << "open data file " << filename << std::endl;
    evio::evioFileChannel chan(filename);
    chan.open();

    while (chan.read()) {
      evtCount++;
      if (evtCount == MAX_EVENT_COUNT) {
         break;
      }

      if (evtCount%100000 == 0) {
         std::cout << "treemaker read " << evtCount << " events" << std::endl;
      }
 
      evio::evioDOMTree eventTree(chan);
      analyzeEvent(eventTree);

      if (event_passes_trigger()) {
         hnorm->Fill(double(q[14]));
         v792->Fill();
      }
    }
    
    chan.close();

    std::cout << std::endl
              << "normalization pulse height mean = " << hnorm->GetMean()
              << ", rms = " << hnorm->GetRMS()
              << std::endl;
    
    ROOTfile->cd();
    ROOTfile->Write();
    ROOTfile->Close();
    delete ROOTfile;
    std::cout << std::endl << "\nClose ROOT file" << std::endl;

  } catch (evio::evioException *e) {
    std::cerr << std::endl << e->toString() << std::endl << std::endl;
    exit(EXIT_FAILURE);
  }
  
  std::cout << std::endl << std::endl 
            << " ***File analyzer done after " 
            << evtCount << " events***" << std::endl << std::endl;
  exit(EXIT_SUCCESS);
}

void analyzeEvent(evio::evioDOMTree &eventTree)
{
  evio::evioDOMNodeListP bankList = eventTree.getNodeList();
  for_each (bankList->begin(), bankList->end(), analyzeBank);
}

void analyzeBank(evio::evioDOMNodeP bankPtr)
{
  switch (bankPtr->tag) {
    
  case 17:          // new run header
    {
      const std::vector<uint32_t> *vec = bankPtr->getVector<uint32_t>();
      if (vec == NULL) {
         std::cerr << "?unable to get header bank vector" << std::endl;
         return;
      }
      run_number = (*vec)[1];
      break;
    }

  case 4:          // event header bank
    {
      const std::vector<uint32_t> *vec = bankPtr->getVector<uint32_t>();
      if (vec == NULL) {
         std::cerr << "?unable to get header bank vector" << std::endl;
         return;
      }
      event_number = (*vec)[0];
      if (verbose_print) {
         std::cout << dec << "found header bank:  run number " 
                   << run_number << std::endl
                   << "                    event number " 
                   << event_number << std::endl << std::endl;
      }
      break;
    }
    
  case 5:        // CAEN v792 QDC data block
    {
      const vector<uint32_t> *vec = bankPtr->getVector<uint32_t>();
      if (vec == NULL) {
         std::cerr << "?unable to get qdc bank vector" << std::endl;
         return;
      }

      if (verbose_print) {
        std::cout << " ------------------" << std::endl;
        std::cout << " QDC Vector Size = " << vec->size() << std::endl;
        std::cout << " ------------------" << std::endl;      
      }

      for (unsigned i = 1; i <= 32; i++){
        unsigned int  channel = ((*vec)[i] & 0x1f0000) >> 16;
        q[channel] = ((*vec)[i] & 0x3fff);
        if (verbose_print) {
           std::cout << "   q[" << channel << "] = "
                     << q[channel] << std::endl;
        }
      }
      status = (*vec)[34];
      break;
    }

  default:
    {
      break;
    }
  }
}

void initRootTree(const char* fname)
{
  ROOTfile = new TFile(fname,"RECREATE","new");
  std::cout << "Opened ROOT file " << fname << " ..." << std::endl;
  std::cout << "Create Root tree ..." << std::endl;
  ROOTfile->cd();

  v792 = new TTree( "v792", "QDC output" );
  v792->Branch("RunNo", &run_number, "runno/I");
  v792->Branch("EventNo", &event_number, "eventno/I");
  v792->Branch("Q", q, "q[32]/D" );
  v792->Branch("Status", &status, "status/I" );
}

bool event_passes_trigger()
{
   return true;
}
