# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing


#----------------------------------------------------------------------------

# Setup Settings for ONIA SKIM:

isMC           = False     # if input is MONTECARLO: True or if it's DATA: False
muonSelection  = "Trk"     # Single muon selection: Glb(isGlobal), GlbTrk(isGlobal&&isTracker), Trk(isTracker) are availale

#----------------------------------------------------------------------------


# Print Onia Skim settings:
print( " " ) 
print( "[INFO] Settings used for ONIA SKIM: " )  
print( "[INFO] isMC          = " + ("True" if isMC else "False") )  
print( "[INFO] muonSelection = " + muonSelection )  
print( " " ) 

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.inputFiles = '/store/hidata/PARun2016B/PADoubleMuon/AOD/PromptReco-v1/000/284/763/00000/D826A45E-4CAB-E611-8A3B-FA163E7A8987.root'
options.outputFile = 'skimPromptC.root'

options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.categories.extend(["HiOnia2MuMuPAT_muonLessSizeORpvTrkSize"])
process.MessageLogger.cerr.HiOnia2MuMuPAT_muonLessSizeORpvTrkSize = cms.untracked.PSet( limit = cms.untracked.int32(5) )

# load the Geometry and Magnetic Field for the TransientTrackBuilder
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

# Global Tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '80X_dataRun2_v18', '')
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

# HLT Dimuon Triggers
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
# HLT pPb MENU:  /users/anstahll/PA2016/PAMuon2016Full/V3
process.hltOniaHI.HLTPaths =  [
  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt10_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt15_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0Lt10_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0Lt15_v1",
  "HLT_PASingleMuOpen_HFOneTowerVeto_SingleTrack_v1",
  "HLT_PASingleMuOpen_HFOneTowerVeto_v1",
  "HLT_PASingleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
  "HLT_PASingleMuOpen_HFTwoTowerVeto_v1",
  "HLT_PADoubleMuOpen_HFOneTowerVeto_SingleTrack_v1",
  "HLT_PADoubleMuOpen_HFOneTowerVeto_v1",
  "HLT_PADoubleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
  "HLT_PADoubleMuOpen_HFTwoTowerVeto_v1"
  ]

process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True
process.hltOniaHI.TriggerResultsTag = cms.InputTag("TriggerResults","","HLT")

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *
onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=isMC, HLT="HLT", Filter=False, useL1Stage2=True)

### For the PAT Trigger prescale warnings.
process.patTriggerFull.l1GtReadoutRecordInputTag = cms.InputTag("gtDigis","","RECO")
process.patTriggerFull.l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis","","RECO")
process.patTriggerFull.l1tExtBlkInputTag = cms.InputTag("gtStage2Digis","","RECO")
process.patTriggerFull.getPrescales      = cms.untracked.bool(False)
###

##### Onia2MuMuPAT input collections/options
process.onia2MuMuPatGlbGlb.dimuonSelection          = cms.string("mass > 0")
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity   = True
process.onia2MuMuPatGlbGlb.srcTracks                = cms.InputTag("generalTracks")
process.onia2MuMuPatGlbGlb.primaryVertexTag         = cms.InputTag("offlinePrimaryVertices")
process.patMuonsWithoutTrigger.pvSrc                = cms.InputTag("offlinePrimaryVertices")
# Adding muonLessPV gives you lifetime values wrt. muonLessPV only
process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = True
if isMC:
  process.genMuons.src = "genParticles"
  process.onia2MuMuPatGlbGlb.genParticles = "genParticles"

##### Dimuon pair selection
commonP1 = ""
commonP2 = ""
#commonP1 = "|| (innerTrack.isNonnull && genParticleRef(0).isNonnull)"
#commonP2 = " && abs(innerTrack.dxy)<4 && abs(innerTrack.dz)<35"
if muonSelection == "Glb":
  highP = "isGlobalMuon"; # At least one muon must pass this selection
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "isGlobalMuon"; # BOTH muons must pass this selection
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
elif muonSelection == "GlbTrk":
  highP = "(isGlobalMuon && isTrackerMuon)";
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "(isGlobalMuon && isTrackerMuon)";
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
elif muonSelection == "Trk":
  highP = "isTrackerMuon";
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "isTrackerMuon";
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
else:
  print "ERROR: Incorrect muon selection " + muonSelection + " . Valid options are: Glb, Trk, GlbTrk"

##### Remove few paths for MC
if isMC:
  process.patMuonSequence.remove(process.hltOniaHI)


process.source.fileNames      = cms.untracked.vstring(options.inputFiles)        
process.maxEvents             = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.outOnia2MuMu.fileName = cms.untracked.string( options.outputFile )
process.e                     = cms.EndPath(process.outOnia2MuMu)
process.schedule              = cms.Schedule(process.Onia2MuMuPAT,process.e)

from Configuration.Applications.ConfigBuilder import MassReplaceInputTag
MassReplaceInputTag(process)
