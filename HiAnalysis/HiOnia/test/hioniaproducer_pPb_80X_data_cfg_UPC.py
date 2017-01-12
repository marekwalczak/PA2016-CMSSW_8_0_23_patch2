import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing


#----------------------------------------------------------------------------

# Setup Settings for ONIA TREE:
   
isMC           = False    # if input is MONTECARLO: True or if it's DATA: False
applyMuonCuts  = False    # Apply muon ID quality cuts
muonSelection  = "Trk"    # Single muon selection: Glb(isGlobal), GlbTrk(isGlobal&&isTracker), Trk(isTracker) are availale

#----------------------------------------------------------------------------

# Print Onia Skim settings:
print( " " ) 
print( "[INFO] Settings used for ONIA TREE DATA: " )  
print( "[INFO] isMC          = " + ("True" if isMC else "False") )  
print( "[INFO] applyMuonCuts = " + ("True" if applyMuonCuts else "False") ) 
print( "[INFO] muonSelection = " + muonSelection )  
print( " " )


# set up process
process = cms.Process("HIOnia")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# Input and Output File Names
options.outputFile = "OniaTreePromptC.root"
options.secondaryOutputFile = "Jpsi_DataSet.root"
options.inputFiles =  ''
options.maxEvents = -1 # -1 means all events

# Get and parse the command line arguments
options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.categories.extend(["GetManyWithoutRegistration","GetByLabelWithoutRegistration"])
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.categories.extend(["HiOnia2MuMuPAT_muonLessSizeORpvTrkSize"])
process.MessageLogger.cerr.HiOnia2MuMuPAT_muonLessSizeORpvTrkSize = cms.untracked.PSet( limit = cms.untracked.int32(5) )


# Global Tag:
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '80X_dataRun2_Prompt_v15', '')
process.GlobalTag.snapshotTime = cms.string("9999-12-31 23:59:59.000")

process.GlobalTag.toGet = cms.VPSet(
  cms.PSet(
    record = cms.string("HeavyIonRcd"),
    tag = cms.string("CentralityTable_HFtowersPlusTrunc200_EPOS5TeV_v80x01_mc"),
    connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
    label = cms.untracked.string("HFtowersPlusTruncEpos")
    ),
  cms.PSet(
    record = cms.string('L1TUtmTriggerMenuRcd'),
    tag = cms.string("L1Menu_HeavyIons2016_v2_m2_xml"),
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
    ),
  cms.PSet(
    record = cms.string('L1TGlobalPrescalesVetosRcd'),
    tag = cms.string("L1TGlobalPrescalesVetos_Stage2v0_hlt"),
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
    )
  )


### For Centrality
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("pACentrality")
process.centralityBin.centralityVariable = cms.string("HFtowersPlusTrunc")
process.centralityBin.nonDefaultGlauberModel = cms.string("Epos")
process.EventAna_step = cms.Path( process.centralityBin )

process.hionia = cms.EDAnalyzer('HiOniaAnalyzer',
                                #-- Collections
                                srcMuon             = cms.InputTag("patMuonsWithTrigger"),     # Name of PAT Muon Collection
                                srcMuonNoTrig       = cms.InputTag("patMuonsWithoutTrigger"),  # Name of PAT Muon Without Trigger Collection
                                src                 = cms.InputTag("onia2MuMuPatGlbGlb"),      # Name of Onia Skim Collection
                                EvtPlane            = cms.InputTag("hiEvtPlane",""),           # Name of Event Plane Collection. For RECO use: hiEventPlane,recoLevel

                                triggerResultsLabel = cms.InputTag("TriggerResults","","HLT"), # Label of Trigger Results

                                #-- Reco Details
                                useBeamSpot = cms.bool(False),  
                                useRapidity = cms.bool(True),
                                
                                #--
                                maxAbsZ = cms.double(24.0),
                                
                                pTBinRanges      = cms.vdouble(0.0, 6.0, 8.0, 9.0, 10.0, 12.0, 15.0, 40.0),
                                etaBinRanges     = cms.vdouble(0.0, 2.5),
                                centralityRanges = cms.vdouble(20,40,100),

                                onlyTheBest        = cms.bool(False),
                                applyCuts          = cms.bool(applyMuonCuts),
                                selTightGlobalMuon = cms.bool(False),
                                storeEfficiency    = cms.bool(False),
                      
                                removeSignalEvents = cms.untracked.bool(False),  # Remove/Keep signal events
                                removeTrueMuons    = cms.untracked.bool(False),  # Remove/Keep gen Muons
                                storeSameSign      = cms.untracked.bool(True),   # Store/Drop same sign dimuons
                                
                                #-- Gen Details
                                oniaPDG = cms.int32(443),
                                muonSel = cms.string(muonSelection),
                                isHI = cms.untracked.bool(False),
                                isPA = cms.untracked.bool(True),
                                isMC = cms.untracked.bool(isMC),
                                isPromptMC = cms.untracked.bool(True),
                                useEvtPlane = cms.untracked.bool(False),
                                useGeTracks = cms.untracked.bool(False),
                                runVersionChange = cms.untracked.uint32(182133),

                                #-- Histogram configuration
                                combineCategories = cms.bool(False),
                                fillRooDataSet    = cms.bool(False),
                                fillTree          = cms.bool(True),
                                fillHistos        = cms.bool(False),
                                minimumFlag       = cms.bool(False),
                                fillSingleMuons   = cms.bool(True),
                                fillRecoTracks    = cms.bool(False),
                                histFileName      = cms.string(options.outputFile),		
                                dataSetName       = cms.string(options.secondaryOutputFile),
                                    
                                # HLT pPb MENU:  /users/anstahll/PA2016/PAMuon2016Full/V3
                                
                                dblTriggerPathNames = cms.vstring("HLT_PADoubleMuOpen_HFOneTowerVeto_SingleTrack_v1",
                                                                  "HLT_PADoubleMuOpen_HFOneTowerVeto_v1",
                                                                  "HLT_PADoubleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
                                                                  "HLT_PADoubleMuOpen_HFTwoTowerVeto_v1"),

                                dblTriggerFilterNames = cms.vstring("hltL1fL1shltUPCL1DoubleMuOpenHFOneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenHFOneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenNotHF0TwoTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenNotHF0TwoTowerFiltered0"),

                                sglTriggerPathNames = cms.vstring("HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt10_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt15_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0Lt10_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0Lt15_v1",
                                                                  "HLT_PASingleMuOpen_HFOneTowerVeto_SingleTrack_v1",
                                                                  "HLT_PASingleMuOpen_HFOneTowerVeto_v1",
                                                                  "HLT_PASingleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
                                                                  "HLT_PASingleMuOpen_HFTwoTowerVeto_v1"),

                                sglTriggerFilterNames = cms.vstring("hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0OneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0OneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0TwoTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0TwoTowerFiltered0")
                                )

process.hionia.primaryVertexTag = cms.InputTag("offlinePrimaryVertices")
process.hionia.genParticles     = cms.InputTag("genParticles")
process.hionia.muonLessPV       = cms.bool(True)
process.hionia.EvtPlane         = cms.InputTag("hiEvtPlaneFlat","")
process.hionia.CentralitySrc    = cms.InputTag("pACentrality")
process.hionia.CentralityBinSrc = cms.InputTag("centralityBin","HFtowersPlusTrunc")
process.hionia.srcTracks        = cms.InputTag("generalTracks")
      
#Options:
process.source    = cms.Source("PoolSource",
                               fileNames = cms.untracked.vstring( options.inputFiles )
                               )
process.TFileService = cms.Service("TFileService", 
                                   fileName = cms.string( options.outputFile )
                                   )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.options   = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.p         = cms.Path(process.hionia)
#process.schedule  = cms.Schedule( process.EventAna_step, process.p )
process.schedule  = cms.Schedule( process.p )
