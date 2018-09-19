import sys,os

runid = sys.argv[1]

print(runid)

if(int(runid)<10):
    os.system("cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_00000"+runid+"_001_0201.lv2b EVT2/astri_000_41_001_00001_R_000000_001_0201.lv2b.ok")
    os.system("cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_00000"+runid+"_001_0601.lv0 EVT2/")
    os.system("cp ../astripipe_v0.2.5/data/DL2b/IRF2/irf2_C3.lv2b EVT2/")

if(int(runid)>9):
    os.system("cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_0000"+runid+"_001_0201.lv2b EVT2/astri_000_41_001_00001_R_000000_001_0201.lv2b.ok")
    os.system("cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_0000"+runid+"_001_0601.lv0 EVT2/")
    os.system("cp ../astripipe_v0.2.5/data/DL2b/IRF2/irf2_C3.lv2b EVT2/")
