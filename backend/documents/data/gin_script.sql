-- drop table json_to_pos
-- select * from json_to_pos;

-- crear una nueva columna
alter table json_to_pos add column search_txt tsvector;
-- crear los vectores de terminos para el par: title, description
update json_to_pos
set search_txt = R.weight
from (
select id_, 
          setweight(to_tsvector('english', abstract), 'A')
      as weight
from json_to_pos
) R
where R.id_ = json_to_pos.id_;
-- crear el indice
create index json_idx_search on json_to_pos using GIN (search_txt);
-- capturar el tiempo 
explain analyze
select count(*) from json_to_pos where plainto_tsquery('english', 'A fully differential calculation in perturbative quantum chromodynamics is presented for the production of massive photon pairs at hadron colliders. All next-to-leading order perturbative contributions from quark-antiquark, gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as all-orders resummation of initial-state gluon radiation valid at next-to-next-to-leading logarithmic accuracy. The region of phase space is specified in which the calculation is most reliable. Good agreement is demonstrated with data from the Fermilab Tevatron, and predictions are made for more detailed tests with CDF and DO data. Predictions are shown for distributions of diphoton pairs produced at the energy of the Large Hadron Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs boson are contrasted with those produced from QCD processes at the LHC, showing that enhanced sensitivity to the signal can be obtained with judicious selection of events.') @@ search_txt;
-- obtener el tok de documentos similares a la query
explain analyze
select id_,title, abstract, ts_rank_cd(search_txt, query) as score
from json_to_pos, plainto_tsquery('english', 'A fully differential calculation in perturbative quantum chromodynamics is presented for the production of massive photon pairs at hadron colliders. All next-to-leading order perturbative contributions from quark-antiquark, gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as all-orders resummation of initial-state gluon radiation valid at next-to-next-to-leading logarithmic accuracy. The region of phase space is specified in which the calculation is most reliable. Good agreement is demonstrated with data from the Fermilab Tevatron, and predictions are made for more detailed tests with CDF and DO data. Predictions are shown for distributions of diphoton pairs produced at the energy of the Large Hadron Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs boson are contrasted with those produced from QCD processes at the LHC, showing that enhanced sensitivity to the signal can be obtained with judicious selection of events.') query
where query @@ search_txt
order by  score desc
limit 10;