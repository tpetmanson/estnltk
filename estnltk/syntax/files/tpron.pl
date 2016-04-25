#!/usr/bin/perl -w

while(<>){
  s:(emb\+.* //_P_) ([s|p]):$1 det $2:g;
  s:(enda\+.* //_P_) ([s|p]):$1 pos refl $2:g;
  s:(enese\+.* //_P_) ([s|p]):$1 pos refl $2:g;
  s:(eikeegi.* //_P_) ([s|p]):$1 indef $2:g;
  s:(eimiski.* //_P_) ([s|p]):$1 indef $2:g;
  s:(emb-kumb.* //_P_) ([s|p]):$1 det $2:g;
  s:(esimene.* //_P_) ([s|p]):$1 dem $2:g;
  s:(iga\+.* //_P_) ([s|p]):$1 det $2:g;
  s:(iga_sugune.* //_P_) ([s|p]):$1 indef $2:g;
  s:(iga_.ks\+.* //_P_) ([s|p]):$1 det $2:g;
  s:(ise\+.* //_P_) ([s|p]):$1 pos det refl $2:g;
  s:(ise_enese.* //_P_) ([s|p]):$1 refl $2:g;
  s:(ise_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(keegi.* //_P_) ([s|p]):$1 indef $2:g;
  s:(kes.* //_P_) ([s|p]):$1 inter rel $2:g;
  s:(kumb\+.* //_P_) ([s|p]):$1 rel $2:g;
  s:(kumbki.* //_P_) ([s|p]):$1 det $2:g;
  s:(kõik.* //_P_) ([s|p]):$1 det $2:g;
  s:(k.ik.* //_P_) ([s|p]):$1 det $2:g;
  s:(meie_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(meie_taoline.* //_P_) ([s|p]):$1 dem $2:g;
  s:(mihuke\+.* //_P_) ([s|p]):$1 inter rel $2:g;
  s:(mihukene\+.* //_P_) ([s|p]):$1 inter rel $2:g;
  s:(mille_taoline.* //_P_) ([s|p]):$1 dem $2:g;
  s:(milline.* //_P_) ([s|p]):$1 rel $2:g;
  s:(milli=ne.* //_P_) ([s|p]):$1 rel $2:g;
  s:(mina\+.* //_P_) ([s|p]):$1 pers ps1 $2:g;
  s:( ma\+.* //_P_) ([s|p]):$1 pers ps1 $2:g;
  s:(minakene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(mina=kene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(minake\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(mina=ke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(mingi\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(mingi_sugune.* //_P_) ([s|p]):$1 indef $2:g;
  s:(minu_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(minu_taoline.* //_P_) ([s|p]):$1 dem $2:g;
  s:(miski.* //_P_) ([s|p]):$1 indef $2:g;
  s:(mis\+.* //_P_) ([s|p]):$1 inter rel $2:g; 
  s:(mis_sugune.* //_P_) ([s|p]):$1 inter rel $2:g; 
  s:(miski\+.* //_P_) ([s|p]):$1 inter rel $2:g; 
  s:(miski_sugune.* //_P_) ([s|p]):$1 inter rel $2:g; 
  s:(misuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(misu=ke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(misukene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(misu=kene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(mitme_sugune.* //_P_) ([s|p]):$1 indef $2:g; 
  s:(mitme_taoline.* //_P_) ([s|p]):$1 indef $2:g; 
  s:(mitmendik\+.* //_P_) ([s|p]):$1 inter rel $2:g; 
  s:(mitmes\+.* //_P_) ([s|p]):$1 inter rel indef $2:g; 
  s:(mitu.* //_P_) ([s|p]):$1 indef $2:g;
  s:(mi=tu.* //_P_) ([s|p]):$1 indef $2:g;
  s:(miuke\+.* //_P_) ([s|p]):$1 inter rel $2:g;
  s:(miukene\+.* //_P_) ([s|p]):$1 inter rel $2:g;
  s:(muist\+.* //_P_) :$1 indef :g;
  s:(muu.* //_P_) ([s|p]):$1 indef $2:g;
  s:(m.lema.* //_P_) ([s|p]):$1 det $2:g;
  s:(m.ne_sugune\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(m.ni\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(m.ningane\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(m.ningas.* //_P_) ([s|p]):$1 indef $2:g;
  s:(m.herdune\+.* //_P_) ([s|p]):$1 inder rel $2:g;
  s:(määntne\+.* //_P_) ([s|p]):$1 dem $2:g; 
  s:(na_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nende_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nende_taoline.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nihuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nihukene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nii_mitu\+.* //_P_) ([s|p]):$1 indef inter rel $2:g;
  s:(nii_mi=tu\+.* //_P_) ([s|p]):$1 indef inter rel $2:g;
  s:(nii_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(niisama_sugune.* //_P_) ([s|p]):$1 dem $2:g;
  s:(niisuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nisuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nisu=ke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nisukene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(nisu=kene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(niuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(niukene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(oma\+.* //_P_) ([s|p]):$1 pos det refl $2:g;
  s:(oma_enese\+.* //_P_) ([s|p]):$1 pos $2:g;
  s:(oma_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(oma_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(palju.* //_P_) ([s|p]):$1 indef $2:g;
  s:(sama\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(sama_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(sama_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(samune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see_sama\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see_samane\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see_samune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see_sinane\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(see_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(selle_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(selline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(selli=ne\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(setu\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(setmes\+.* //_P_) ([s|p]):$1 indef $2:g;
  s:(sihuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(sihuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(sina\+.* //_P_) ([s|p]):$1 pers ps2 $2:g;
  s:( sa\+.* //_P_) ([s|p]):$1 pers ps2 $2:g;
  s:(sinu_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(sinu_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(siuke\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(siukene\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(säherdune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(s.herdune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(säärane\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(s..rane\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(teie_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(teie_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(teine\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(teine_teise\+.* //_P_) ([s|p]):$1 rec $2:g;
  s:(teis_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(teist_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(tema\+.* //_P_) ([s|p]):$1 pers ps3 $2:g;
  s:( ta\+.* //_P_) ([s|p]):$1 pers ps3 $2:g;
  s:(temake\+.* //_P_) ([s|p]):$1 pers ps3 $2:g;
  s:(temakene\+.* //_P_) ([s|p]):$1 pers ps3 $2:g;
  s:(tema_sugune\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(tema_taoline\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(too\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(too_sama\+.* //_P_) ([s|p]):$1 dem $2:g;
  s:(üks.* //_P_) ([s|p]):$1 dem indef $2:g;
  s:(.ks.* //_P_) ([s|p]):$1 dem indef $2:g;
  s:(ükski.* //_P_) ([s|p]):$1 dem indef $2:g;
  s:(.kski.* //_P_) ([s|p]):$1 dem indef $2:g;
  s:(üks_teise.* //_P_) ([s|p]):$1 rec indef $2:g;
  s:(.ks_teise.* //_P_) ([s|p]):$1 rec $2:g;


  print;
}


