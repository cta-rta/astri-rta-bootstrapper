#!/bin/bash

#read -p "Enter id: " id

id=$1

echo $id

if [ $id -lt 10 ] 
then
  echo "<10"
  cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_00000"$id"_001_0201.lv2b EVT2/astri_000_41_001_00001_R_000000_001_0201.lv2b.ok
  cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_00000"$id"_001_0601.lv0 EVT2/
  cp ../astripipe_v0.2.5/data/DL2b/IRF2/irf2_C3.lv2b EVT2/
fi

if [ $id -gt 9 ] 
then
  echo ">9"
  cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_0000"$id"_001_0201.lv2b EVT2/astri_000_41_001_00001_R_000000_001_0201.lv2b.ok
  cp ../astripipe_v0.2.5/data/DL2b/EVT2b/dummy/astri_000_41_001_00001_R_0000"$id"_001_0601.lv0 EVT2/
  cp ../astripipe_v0.2.5/data/DL2b/IRF2/irf2_C3.lv2b EVT2/
fi
